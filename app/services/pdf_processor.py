import fitz
import logging

logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.doc = fitz.open(file_path)
        self.total_pages = len(self.doc)
        self.current_page = 0
        self.extracted_text = ""
        logger.info(f"Initialized PDF processor for {file_path} with {self.total_pages} pages")

    def get_next_page(self):
        """获取下一页的文本内容"""
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
        self.doc.close()
        logger.info("PDF document closed")

    # ... PDF处理方法 ... 