"""
環境変数管理クラス
"""

import os
from typing import Optional
from dotenv import load_dotenv

class ConfigManager:
    """環境変数とアプリケーション設定を管理するクラス"""
    
    def __init__(self, env_file: str = ".env"):
        """初期化"""
        self.env_file = env_file
        self._load_env()
    
    def _load_env(self) -> None:
        """環境変数ファイルを読み込み"""
        # .envファイルが存在する場合は読み込み
        if os.path.exists(self.env_file):
            load_dotenv(self.env_file)
        else:
            print(f"⚠️ {self.env_file} ファイルが見つかりません。デフォルト値を使用します。")
    
    def get(self, key: str, default: Optional[str] = None) -> str:
        """環境変数を取得"""
        return os.getenv(key, default)
    
    def get_database_path(self) -> str:
        """データベースパスを取得"""
        return self.get("DATABASE_PATH", "data/diary_normalized.db")
    
    def get_test_user_password(self) -> str:
        """テストユーザーパスワードを取得"""
        return self.get("TEST_USER_PASSWORD", "password123")
    
    def get_admin_password(self) -> str:
        """管理者パスワードを取得"""
        return self.get("ADMIN_PASSWORD", "admin123")
    
    def get_demo_password(self) -> str:
        """デモユーザーパスワードを取得"""
        return self.get("DEMO_PASSWORD", "demo123")
    
    def get_gemini_api_key(self) -> Optional[str]:
        """Gemini APIキーを取得"""
        return self.get("GEMINI_API_KEY")
    
    def get_openai_api_key(self) -> Optional[str]:
        """OpenAI APIキーを取得"""
        return self.get("OPENAI_API_KEY")
    
    def is_production(self) -> bool:
        """本番環境かどうかを判定"""
        return self.get("ENVIRONMENT", "development").lower() == "production"
    
    def get_secret_key(self) -> str:
        """セッション用のシークレットキーを取得"""
        return self.get("SECRET_KEY", "your-secret-key-change-in-production")

# グローバルインスタンス
config = ConfigManager() 