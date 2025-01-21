from flask import Blueprint, jsonify, request, current_app, session
from werkzeug.utils import secure_filename
from app.services.pdf_processor import PDFProcessor
from app.services.ai_processor import AIProcessor
from app.utils.prompt_manager import PromptManager
import os
import uuid
import logging
import traceback

# 创建日志记录器
logger = logging.getLogger(__name__)

pdf_bp = Blueprint('pdf', __name__)
prompt_manager = PromptManager()

# 存储当前处理的PDF会话
pdf_sessions = {}

@pdf_bp.route('/start-pdf-processing', methods=['POST'])
def start_pdf_processing():
    """开始处理PDF文件"""
    try:
        if 'file' not in request.files:
            logger.error("No file part in request")
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            logger.error("No selected file")
            return jsonify({'error': 'No selected file'}), 400
        
        if file and file.filename.endswith('.pdf'):
            try:
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                logger.info(f"File saved: {file_path}")
                
                session_id = str(uuid.uuid4())
                pdf_sessions[session_id] = {
                    'processor': PDFProcessor(file_path),
                    'output_content': [],
                    'current_prompt': session.get('current_prompt', prompt_manager.get_default_prompt())
                }
                
                first_page = pdf_sessions[session_id]['processor'].get_next_page()
                logger.info(f"PDF processing session started: {session_id}")
                
                return jsonify({
                    'success': True,
                    'session_id': session_id,
                    'page_info': first_page
                })
                
            except Exception as e:
                logger.error(f"Error starting PDF processing: {str(e)}")
                return jsonify({'error': str(e)}), 500
        
        logger.error("Invalid file type")
        return jsonify({'error': 'Invalid file type'}), 400
        
    except Exception as e:
        logger.error(f"PDF processing error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@pdf_bp.route('/prompts', methods=['GET'])
def get_prompts():
    """获取所有提示模板"""
    try:
        prompts = prompt_manager.get_all_prompts()
        return jsonify(prompts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pdf_bp.route('/prompts', methods=['POST'])
def add_prompt():
    """添加新的提示模板"""
    try:
        data = request.json
        new_prompt = prompt_manager.add_prompt(
            data['name'],
            data['description'],
            data['prompt']
        )
        return jsonify(new_prompt)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pdf_bp.route('/preview-next-page', methods=['POST'])
def preview_next_page():
    """预览下一页内容"""
    try:
        session_id = request.json.get('session_id')
        if not session_id or session_id not in pdf_sessions:
            return jsonify({'error': 'Invalid session ID'}), 400
            
        processor = pdf_sessions[session_id]['processor']
        current_page = processor.current_page
        
        # 获取下一页内容但不更新当前页
        if current_page + 1 < processor.total_pages:
            next_page = processor.doc[current_page + 1].get_text()
            return jsonify({
                'success': True,
                'page_number': current_page + 2,  # 显示给用户的页码从1开始
                'content': next_page
            })
        return jsonify({'error': 'No more pages'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pdf_bp.route('/skip-page', methods=['POST'])
def skip_page():
    """跳过当前页"""
    try:
        session_id = request.json.get('session_id')
        if not session_id or session_id not in pdf_sessions:
            return jsonify({'error': 'Invalid session ID'}), 400
            
        session = pdf_sessions[session_id]
        processor = session['processor']
        
        # 直接移到下一页
        processor.current_page += 1
        next_page = processor.get_next_page()
        
        if next_page:
            return jsonify({
                'success': True,
                'page_info': next_page
            })
        return jsonify({
                'success': True,
                'is_complete': True
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pdf_bp.route('/process-page', methods=['POST'])
def process_page():
    """处理单页PDF内容"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        custom_prompt = data.get('prompt')
        
        logger.info(f"Processing PDF page request - Session ID: {session_id}")
        
        # 如果没有提供自定义提示，使用当前选中的提示
        if not custom_prompt:
            custom_prompt = session.get('current_prompt', prompt_manager.get_default_prompt())
            logger.debug(f"Using prompt: {custom_prompt[:50]}...")
        
        if not session_id or session_id not in pdf_sessions:
            logger.error(f"Invalid session ID: {session_id}")
            return jsonify({'error': 'Invalid session ID'}), 400
            
        session = pdf_sessions[session_id]
        processor = session['processor']
        ai_processor = AIProcessor()
        
        # 获取当前页信息
        page_info = processor.get_next_page()
        if not page_info:
            logger.info("PDF processing complete")
            return jsonify({
                'success': True,
                'is_complete': True
            })
        
        logger.info(f"Processing page {processor.current_page + 1}/{processor.total_pages}")
        logger.debug(f"Page text length: {len(page_info['text'])} characters")
        
        # 处理当前页
        response = ai_processor.process_text(
            page_info['text'],
            custom_prompt
        )
        
        if 'error' in response:
            logger.error(f"Error processing page: {response['error']}")
            return jsonify(response), 500
        
        processed_content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
        logger.debug(f"Processed content length: {len(processed_content)} characters")
        
        # 更新页码
        processor.current_page += 1
        logger.info(f"Page {processor.current_page}/{processor.total_pages} processed successfully")
        
        return jsonify({
            'success': True,
            'content': processed_content,
            'page_info': page_info,
            'is_complete': processor.current_page >= processor.total_pages
        })
        
    except Exception as e:
        logger.error(f"Error processing PDF page: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@pdf_bp.route('/process-batch', methods=['POST'])
def process_batch():
    """处理接下来的10页"""
    try:
        session_id = request.json.get('session_id')
        custom_prompt = request.json.get('prompt')
        
        logger.info(f"Starting batch processing - Session ID: {session_id}")
        
        if not session_id or session_id not in pdf_sessions:
            logger.error(f"Invalid session ID: {session_id}")
            return jsonify({'error': 'Invalid session ID'}), 400
            
        session = pdf_sessions[session_id]
        processor = session['processor']
        ai_processor = AIProcessor()
        
        results = []
        pages_processed = 0
        current_page = processor.current_page
        
        logger.info(f"Starting from page {current_page + 1}")
        
        while pages_processed < 10 and current_page < processor.total_pages:
            page_info = processor.get_next_page()
            if not page_info:
                break
                
            logger.info(f"Processing page {current_page + 1}/{processor.total_pages}")
            logger.debug(f"Page text length: {len(page_info['text'])} characters")
            
            response = ai_processor.process_text(
                page_info['text'],
                custom_prompt or session['current_prompt']
            )
            
            if 'error' in response:
                logger.error(f"Error processing page {current_page + 1}: {response['error']}")
                continue
            
            processed_content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
            logger.debug(f"Processed content length: {len(processed_content)} characters")
            
            results.append({
                'page_number': current_page + 1,
                'content': processed_content
            })
            
            processor.current_page += 1
            current_page = processor.current_page
            pages_processed += 1
            logger.info(f"Page {current_page}/{processor.total_pages} processed successfully")
        
        logger.info(f"Batch processing complete - {pages_processed} pages processed")
        return jsonify({
            'success': True,
            'results': results,
            'is_complete': current_page >= processor.total_pages
        })
        
    except Exception as e:
        logger.error(f"Error in batch processing: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

# ... 其他PDF相关路由 ... 