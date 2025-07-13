import os
from typing import Dict, Any

class PromptManager:
    """プロンプトファイルを管理するクラス"""
    
    def __init__(self, prompts_dir: str = None):
        if prompts_dir is None:
            # 現在のファイルの場所を基準にプロンプトディレクトリを設定
            current_dir = os.path.dirname(os.path.abspath(__file__))
            prompts_dir = os.path.join(os.path.dirname(current_dir), "prompts")
        self.prompts_dir = prompts_dir
        self._prompts_cache = {}
    
    def load_prompt_template(self, filename: str) -> str:
        """プロンプトファイルを読み込む"""
        if filename in self._prompts_cache:
            return self._prompts_cache[filename]
        
        filepath = os.path.join(self.prompts_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                self._prompts_cache[filename] = content
                return content
        except FileNotFoundError:
            raise FileNotFoundError(f"プロンプトファイルが見つかりません: {filepath}")
    

    
    def get_period_analysis_prompt(self, mode: str, **kwargs) -> str:
        """期間分析用のプロンプトを取得"""
        # モードに応じて専用のプロンプトファイルを読み込む
        if mode == "default":
            filename = "default_analysis_prompt.txt"
        elif mode == "kpt":
            filename = "kpt_analysis_prompt.txt"
        elif mode == "ywt":
            filename = "ywt_analysis_prompt.txt"
        elif mode == "custom":
            filename = "custom_analysis_prompt.txt"
        else:
            raise ValueError(f"不明な分析モード: {mode}")
        
        # プロンプトファイルを読み込む
        prompt_template = self.load_prompt_template(filename)
        
        # テンプレート変数を置換
        return prompt_template.format(**kwargs) 