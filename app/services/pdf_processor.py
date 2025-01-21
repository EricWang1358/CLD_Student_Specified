import fitz
import logging

logger = logging.getLogger(__name__)

class PDFProcessor:
    """
    PDF处理服务类
    用途：处理PDF文件的读取和文本提取
    
    主要功能：
    - 打开和读取PDF文件
    - 逐页提取文本
    - 追踪处理进度
    
    被调用位置：
    - app/routes/pdf.py: 处理PDF文件上传和文本提取
    """

    def __init__(self, file_path):
        """
        初始化PDF处理器
        
        Args:
            file_path: PDF文件路径
            
        设置：
        - 打开PDF文档
        - 获取总页数
        - 初始化页面计数器
        - 初始化文本缓存
        """
        self.file_path = file_path
        self.doc = fitz.open(file_path)
        self.total_pages = len(self.doc)
        self.current_page = 0
        self.extracted_text = ""
        logger.info(f"Initialized PDF processor for {file_path} with {self.total_pages} pages")

    def get_next_page(self):
        """
        获取下一页的文本内容
        
        Returns:
            dict: 包含页面信息和文本内容的字典,如果没有更多页面则返回None
            
        功能：
        - 提取当前页面文本
        - 更新处理进度信息
        - 返回页面元数据
        """
        if self.current_page < self.total_pages:
            page = self.doc[self.current_page]
            self.extracted_text = page.get_text()
            page_info = {
                'page_number': self.current_page + 1,
                'total_pages': self.total_pages,
                'text': self.extracted_text
            }
            logger.info(f"Extracted text from page {self.current_page + 1}")
            return page_info
        return None

    def close(self):
        """
        关闭PDF文档
        
        用途：
        - 释放文件句柄
        - 清理资源
        
        调用时机：
        - PDF处理完成后
        - 发生错误需要清理时
        """
        self.doc.close()
        logger.info("PDF document closed")

    # ... PDF处理方法 ... 