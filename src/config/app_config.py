"""
アプリケーション設定管理機能を提供するクラス
"""

import os
from typing import Dict, Any, Optional
from constants import DEFAULT_DB_PATH, APP_NAME, APP_VERSION
from dotenv import load_dotenv

# 環境切り替え（local or cloud）
ENV = os.getenv("APP_ENV", "local")
if ENV == "local":
    load_dotenv()

# アプリケーション設定
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
DB_PATH = os.getenv('DB_PATH', 'data/diary_normalized.db')
PASSWORD_MIN_LENGTH = int(os.getenv('PASSWORD_MIN_LENGTH', 6))
SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 3600))

# Supabase設定
USE_SUPABASE = os.getenv('USE_SUPABASE', 'false').lower() == 'true'
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY', '')

class AppConfig:
    """アプリケーション設定管理クラス"""
    
    def __init__(self):
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """設定を読み込み"""
        return {
            'app': {
                'name': APP_NAME,
                'version': APP_VERSION,
                'debug': DEBUG
            },
            'database': {
                'path': DB_PATH,
                'backup_enabled': os.getenv('BACKUP_ENABLED', 'True').lower() == 'true',
                'backup_interval': int(os.getenv('BACKUP_INTERVAL', '24'))  # 時間
            },
            'ai': {
                'provider': os.getenv('AI_PROVIDER', 'gemini'),
                'api_key': os.getenv('GEMINI_API_KEY'),
                'model': os.getenv('AI_MODEL', 'gemini-1.5-flash'),
                'timeout': int(os.getenv('AI_TIMEOUT', '30'))  # 秒
            },
            'security': {
                'password_min_length': PASSWORD_MIN_LENGTH,
                'session_timeout': SESSION_TIMEOUT,  # 秒
                'max_login_attempts': int(os.getenv('MAX_LOGIN_ATTEMPTS', '5'))
            },
            'ui': {
                'theme': os.getenv('UI_THEME', 'light'),
                'language': os.getenv('UI_LANGUAGE', 'ja'),
                'page_size': int(os.getenv('PAGE_SIZE', '10'))
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """設定値を取得"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """設定値を設定"""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def get_database_path(self) -> str:
        """データベースパスを取得"""
        return self.get('database.path')
    
    def get_ai_config(self) -> Dict[str, Any]:
        """AI設定を取得"""
        return self.get('ai', {})
    
    def get_security_config(self) -> Dict[str, Any]:
        """セキュリティ設定を取得"""
        return self.get('security', {})
    
    def get_ui_config(self) -> Dict[str, Any]:
        """UI設定を取得"""
        return self.get('ui', {})
    
    def is_debug_mode(self) -> bool:
        """デバッグモードかどうかを確認"""
        return self.get('app.debug', False)
    
    def get_app_info(self) -> Dict[str, str]:
        """アプリケーション情報を取得"""
        return {
            'name': self.get('app.name'),
            'version': self.get('app.version')
        }
    
    def validate_config(self) -> bool:
        """設定の妥当性を検証"""
        # 必須設定のチェック
        required_configs = [
            'database.path',
            'ai.provider',
            'security.password_min_length'
        ]
        
        for config_key in required_configs:
            if not self.get(config_key):
                return False
        
        return True
    
    def get_config_summary(self) -> Dict[str, Any]:
        """設定サマリーを取得"""
        return {
            'app': self.get_app_info(),
            'database': {
                'path': self.get_database_path(),
                'backup_enabled': self.get('database.backup_enabled')
            },
            'ai': {
                'provider': self.get('ai.provider'),
                'model': self.get('ai.model')
            },
            'security': {
                'password_min_length': self.get('security.password_min_length'),
                'session_timeout': self.get('security.session_timeout')
            },
            'ui': {
                'theme': self.get('ui.theme'),
                'language': self.get('ui.language')
            }
        } 