"""
バリデーション機能を統合するユーティリティ
"""

from typing import Tuple, Optional
import re
from constants import MIN_PASSWORD_LENGTH, ERROR_MESSAGES

class Validator:
    """バリデーション機能を提供するクラス"""
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, Optional[str]]:
        """パスワードの妥当性を検証"""
        if not password:
            return False, ERROR_MESSAGES["MISSING_FIELDS"]
        
        if len(password) < MIN_PASSWORD_LENGTH:
            return False, ERROR_MESSAGES["PASSWORD_TOO_SHORT"]
        
        # 追加のパスワード強度チェック（将来的に実装）
        # - 大文字・小文字・数字・記号の組み合わせ
        # - 連続文字のチェック
        # - 辞書攻撃対策
        
        return True, None
    
    @staticmethod
    def validate_password_confirmation(password: str, confirm_password: str) -> Tuple[bool, Optional[str]]:
        """パスワード確認の妥当性を検証"""
        if password != confirm_password:
            return False, ERROR_MESSAGES["PASSWORD_MISMATCH"]
        
        return True, None
    
    @staticmethod
    def validate_password_change(current_password: str, new_password: str) -> Tuple[bool, Optional[str]]:
        """パスワード変更の妥当性を検証"""
        if current_password == new_password:
            return False, ERROR_MESSAGES["PASSWORD_SAME"]
        
        is_valid, error = Validator.validate_password(new_password)
        if not is_valid:
            return False, error
        
        return True, None
    
    @staticmethod
    def validate_username(username: str) -> Tuple[bool, Optional[str]]:
        """ユーザー名の妥当性を検証"""
        if not username:
            return False, ERROR_MESSAGES["MISSING_FIELDS"]
        
        # ユーザー名の長さチェック
        if len(username) < 3:
            return False, "ユーザー名は3文字以上で入力してください"
        
        if len(username) > 20:
            return False, "ユーザー名は20文字以下で入力してください"
        
        # ユーザー名の文字種チェック
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "ユーザー名は英数字とアンダースコアのみ使用できます"
        
        return True, None
    
    @staticmethod
    def validate_diary_content(content: str) -> Tuple[bool, Optional[str]]:
        """日記内容の妥当性を検証"""
        if not content or not content.strip():
            return False, ERROR_MESSAGES["ENTER_DIARY_CONTENT"]
        
        # 最小文字数チェック
        if len(content.strip()) < 10:
            return False, "日記は10文字以上で入力してください"
        
        # 最大文字数チェック
        if len(content) > 10000:
            return False, "日記は10,000文字以下で入力してください"
        
        return True, None
    
    @staticmethod
    def validate_answer_content(content: str) -> Tuple[bool, Optional[str]]:
        """回答内容の妥当性を検証"""
        if not content or not content.strip():
            return False, ERROR_MESSAGES["ENTER_ANSWER"]
        
        # 最小文字数チェック
        if len(content.strip()) < 5:
            return False, "回答は5文字以上で入力してください"
        
        return True, None
    
    @staticmethod
    def validate_date_range(start_date: str, end_date: str) -> Tuple[bool, Optional[str]]:
        """日付範囲の妥当性を検証"""
        try:
            from datetime import datetime
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            
            if start > end:
                return False, "開始日は終了日より前の日付を選択してください"
            
            # 日付範囲の制限（例：1年以内）
            if (end - start).days > 365:
                return False, "日付範囲は1年以内で選択してください"
            
            return True, None
            
        except ValueError:
            return False, "日付形式が正しくありません"
    
    @staticmethod
    def validate_custom_prompt(prompt: str) -> Tuple[bool, Optional[str]]:
        """カスタムプロンプトの妥当性を検証"""
        if not prompt or not prompt.strip():
            return False, ERROR_MESSAGES["ENTER_PROMPT"]
        
        # 最小文字数チェック
        if len(prompt.strip()) < 10:
            return False, "プロンプトは10文字以上で入力してください"
        
        # 最大文字数チェック
        if len(prompt) > 2000:
            return False, "プロンプトは2,000文字以下で入力してください"
        
        return True, None 