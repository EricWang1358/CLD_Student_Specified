import os
import sys
from pathlib import Path
from pdf_to_images import PDFToImages
import inquirer  # 用于交互式命令行
from rich.console import Console  # 用于美化输出
from rich.progress import Progress
import logging

console = Console()

def select_pdf_file():
    """选择PDF文件"""
    # 获取当前目录下的所有PDF文件
    pdf_files = list(Path('.').glob('**/*.pdf'))
    
    # 添加手动输入选项
    choices = ['手动输入路径...'] + [str(f) for f in pdf_files]
    
    if not pdf_files:
        console.print("[yellow]当前目录及子目录下没有找到PDF文件！[/yellow]")
        console.print("[green]请手动输入PDF文件路径[/green]")
    
    questions = [
        inquirer.List('file',
                     message="选择要处理的PDF文件",
                     choices=choices)
    ]
    
    answers = inquirer.prompt(questions)
    if not answers:
        return None
        
    selected = answers['file']
    
    # 如果选择手动输入
    if selected == '手动输入路径...':
        path_question = [
            inquirer.Text('path',
                         message="请输入PDF文件的完整路径",
                         validate=lambda _, x: Path(x).exists() and Path(x).suffix.lower() == '.pdf')
        ]
        
        path_answer = inquirer.prompt(path_question)
        if not path_answer:
            return None
            
        return path_answer['path']
        
    return selected

def get_page_range(total_pages):
    """获取页面范围"""
    questions = [
        inquirer.Text('start',
                     message=f"输入起始页码 (1-{total_pages}, 回车默认为1)",
                     validate=lambda _, x: x == '' or (x.isdigit() and 1 <= int(x) <= total_pages),
                     default=''),
        inquirer.Text('end',
                     message=f"输入结束页码 (1-{total_pages}, 回车默认为{total_pages})",
                     validate=lambda _, x: x == '' or (x.isdigit() and 1 <= int(x) <= total_pages),
                     default='')
    ]
    
    answers = inquirer.prompt(questions)
    if not answers:
        return None, None
        
    # 处理默认值
    start = int(answers['start']) if answers['start'] else 1
    end = int(answers['end']) if answers['end'] else total_pages
    
    if start > end:
        console.print("[red]起始页码不能大于结束页码！[/red]")
        return None, None
        
    return start, end

def get_output_settings():
    """获取输出设置"""
    questions = [
        inquirer.Text('output',
                     message="输入输出目录 (留空使用默认)",
                     default=''),
        inquirer.List('dpi',
                     message="选择输出图片DPI",
                     choices=['150', '300', '600'],
                     default='300'),
        inquirer.Text('workers',
                     message="输入处理线程数 (留空使用默认)",
                     default='')
    ]
    
    return inquirer.prompt(questions)

def main():
    try:
        # 显示欢迎信息
        console.print("[bold blue]PDF转PNG工具[/bold blue]")
        console.print("=" * 50)
        
        # 选择PDF文件
        pdf_file = select_pdf_file()
        if not pdf_file:
            return 1
            
        # 创建转换器实例
        converter = PDFToImages(pdf_file)
        
        # 打开PDF获取总页数
        with converter.pdf_path.open('rb') as f:
            import fitz
            doc = fitz.open(f)
            total_pages = len(doc)
            doc.close()
        
        console.print(f"\n[green]PDF文件: {pdf_file}[/green]")
        console.print(f"[green]总页数: {total_pages}[/green]\n")
        
        # 获取页面范围
        start_page, end_page = get_page_range(total_pages)
        if start_page is None:
            return 1
            
        # 获取输出设置
        settings = get_output_settings()
        if not settings:
            return 1
            
        # 处理设置
        output_dir = settings['output'] if settings['output'] else None
        dpi = int(settings['dpi'])
        workers = int(settings['workers']) if settings['workers'] else None
        
        # 确认设置
        console.print("\n[yellow]转换设置确认:[/yellow]")
        console.print(f"PDF文件: {pdf_file}")
        console.print(f"页面范围: {start_page} - {end_page}")
        console.print(f"输出目录: {output_dir or '默认'}")
        console.print(f"DPI: {dpi}")
        console.print(f"线程数: {workers or '默认'}")
        
        questions = [
            inquirer.Confirm('confirm',
                           message="确认开始转换",
                           default=True)
        ]
        
        if not inquirer.prompt(questions)['confirm']:
            return 0
            
        # 创建新的转换器（使用用户设置）
        converter = PDFToImages(pdf_file, output_dir, dpi)
        
        # 开始转换
        console.print("\n[green]开始转换...[/green]")
        converter.convert(start_page=start_page, end_page=end_page, max_workers=workers)
        
        return 0
        
    except KeyboardInterrupt:
        console.print("\n[yellow]操作已取消[/yellow]")
        return 1
    except Exception as e:
        console.print(f"\n[red]发生错误: {str(e)}[/red]")
        return 1

if __name__ == '__main__':
    exit(main()) 