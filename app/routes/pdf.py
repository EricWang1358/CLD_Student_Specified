from flask import Blueprint, jsonify, request, current_app
from werkzeug.utils import secure_filename
from app.services.pdf_processor import PDFProcessor
from app.services.ai_processor import AIProcessor
import os
import uuid

pdf_bp = Blueprint('pdf', __name__)

# 存储当前处理的PDF会话
pdf_sessions = {}

@pdf_bp.route('/start-pdf-processing', methods=['POST'])
def start_pdf_processing():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and file.filename.endswith('.pdf'):
        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            session_id = str(uuid.uuid4())
            pdf_sessions[session_id] = {
                'processor': PDFProcessor(file_path),
                'output_content': [],
                'current_prompt': "Please convert this text into detailed markdown notes."
            }
            
            first_page = pdf_sessions[session_id]['processor'].get_next_page()
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'page_info': first_page
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

# ... 其他PDF相关路由 ... 