import os
import json
from flask import current_app
from app.config.prompts import PDF_PROMPTS  # 使用 prompts.py 中的提示

class PromptManager:
    """
    提示管理器
    用于管理和加载PDF处理的提示模板
    """
    def __init__(self):
        self.prompts = PDF_PROMPTS
        self.prompts_dir = 'prompts'
        self._ensure_prompts_dir()
        self._ensure_default_prompts()

    def _ensure_prompts_dir(self):
        """确保prompts目录存在"""
        if not os.path.exists(self.prompts_dir):
            os.makedirs(self.prompts_dir)

    def _ensure_default_prompts(self):
        """创建默认提示模板"""
        default_prompts = [
            {
                "id": 1,
                "name": "标准笔记转换",
                "description": "将PDF内容转换为结构化的markdown笔记",
                "prompt": "请将这段文本转换为详细的markdown格式笔记，包含标题、要点和补充说明。"
            },
            {
                "id": 2,
                "name": "关键概念提取",
                "description": "提取文本中的关键概念和定义",
                "prompt": "请从文本中提取所有关键概念和定义，以markdown格式列出，并添加简短解释。"
            },
            # 可以添加更多默认提示
        ]
        
        default_file = os.path.join(self.prompts_dir, 'default_prompts.json')
        if not os.path.exists(default_file):
            with open(default_file, 'w', encoding='utf-8') as f:
                json.dump(default_prompts, f, ensure_ascii=False, indent=2)

    def get_all_prompts(self):
        """获取所有PDF处理提示"""
        return self.prompts

    def get_prompt_by_id(self, prompt_id):
        """根据ID获取提示"""
        return next((p for p in self.prompts if p['id'] == int(prompt_id)), None)

    def add_prompt(self, name, description, prompt_text):
        """添加新的提示模板"""
        prompts = self.get_all_prompts()
        new_id = max([p['id'] for p in prompts], default=0) + 1
        
        new_prompt = {
            "id": new_id,
            "name": name,
            "description": description,
            "prompt": prompt_text
        }
        
        user_file = os.path.join(self.prompts_dir, 'user_prompts.json')
        existing_prompts = []
        if os.path.exists(user_file):
            with open(user_file, 'r', encoding='utf-8') as f:
                existing_prompts = json.load(f)
        
        existing_prompts.append(new_prompt)
        
        with open(user_file, 'w', encoding='utf-8') as f:
            json.dump(existing_prompts, f, ensure_ascii=False, indent=2)
        
        return new_prompt

    def get_default_prompt(self):
        """获取默认提示"""
        return self.prompts[0]['prompt'] 