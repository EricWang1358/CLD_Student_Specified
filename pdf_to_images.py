import fitz  # PyMuPDF
import os
from pathlib import Path
import logging
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PDFToImages:
    """PDF转PNG工具类"""
    
    def __init__(self, input_path, output_dir=None, dpi=300):
        """
        初始化转换器
        
        Args:
            input_path: PDF文件路径
            output_dir: 输出目录，默认为PDF同目录下的同名文件夹
            dpi: 输出图片的DPI，默认300
        """
        self.pdf_path = Path(input_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF文件不存在: {input_path}")
            
        # 设置输出目录
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = self.pdf_path.parent / self.pdf_path.stem
            
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dpi = dpi
        
    def convert_page(self, args):
        """
        转换单页为PNG
        
        Args:
            args: (页码, 页面对象)元组
        """
        page_num, page = args
        try:
            # 转换为PNG
            pix = page.get_pixmap(matrix=fitz.Matrix(self.dpi/72, self.dpi/72))
            output_path = self.output_dir / f"page_{page_num + 1}.png"
            pix.save(str(output_path))
            return True
        except Exception as e:
            logger.error(f"转换第 {page_num + 1} 页时出错: {str(e)}")
            return False
            
    def convert(self, start_page=None, end_page=None, max_workers=None):
        """
        转换PDF指定范围的页面为PNG
        
        Args:
            start_page: 起始页码(从1开始)，默认为1
            end_page: 结束页码(包含)，默认为最后一页
            max_workers: 最大线程数，默认为CPU核心数
        """
        try:
            doc = fitz.open(self.pdf_path)
            total_pages = len(doc)
            
            # 处理页码范围
            if start_page is None:
                start_page = 1
            if end_page is None:
                end_page = total_pages
                
            # 验证页码范围
            if not (1 <= start_page <= total_pages and 1 <= end_page <= total_pages):
                raise ValueError(f"页码范围无效: {start_page}-{end_page}, PDF总页数: {total_pages}")
            if start_page > end_page:
                raise ValueError(f"起始页码({start_page})大于结束页码({end_page})")
            
            # 转换为0基页码
            start_idx = start_page - 1
            end_idx = end_page - 1
            
            logger.info(f"开始转换 PDF: {self.pdf_path.name}")
            logger.info(f"转换范围: 第{start_page}页 - 第{end_page}页")
            logger.info(f"输出目录: {self.output_dir}")
            
            # 创建指定范围的页面和页码的元组列表
            pages = [(i, doc[i]) for i in range(start_idx, end_idx + 1)]
            
            # 使用线程池并行处理
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # 使用tqdm显示进度条
                results = list(tqdm(
                    executor.map(self.convert_page, pages),
                    total=len(pages),
                    desc="转换进度"
                ))
            
            # 统计结果
            success_count = sum(results)
            total_converted = len(pages)
            logger.info(f"转换完成: 成功 {success_count} 页, 失败 {total_converted - success_count} 页")
            logger.info(f"输出目录: {self.output_dir}")
            
        except Exception as e:
            logger.error(f"转换过程出错: {str(e)}")
        finally:
            if 'doc' in locals():
                doc.close()

def main():
    """主函数"""
    import argparse
    parser = argparse.ArgumentParser(description='将PDF转换为PNG图片')
    parser.add_argument('input', help='输入PDF文件路径')
    parser.add_argument('-o', '--output', help='输出目录路径')
    parser.add_argument('-d', '--dpi', type=int, default=300, help='输出图片DPI(默认300)')
    parser.add_argument('-w', '--workers', type=int, help='最大线程数')
    parser.add_argument('-s', '--start', type=int, help='起始页码(从1开始)')
    parser.add_argument('-e', '--end', type=int, help='结束页码')
    
    args = parser.parse_args()
    
    try:
        converter = PDFToImages(args.input, args.output, args.dpi)
        converter.convert(
            start_page=args.start,
            end_page=args.end,
            max_workers=args.workers
        )
    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")
        return 1
    return 0

if __name__ == '__main__':
    exit(main()) 