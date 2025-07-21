"""
Supabase設定と認証機能
"""

import os
from typing import Optional, Dict, Any
from supabase import create_client, Client
from dotenv import load_dotenv
from config.app_config import SUPABASE_URL, SUPABASE_ANON_KEY

# 環境変数を読み込み
load_dotenv()

class SupabaseConfig:
    """Supabase設定管理クラス"""
    
    def __init__(self):
        self.url = SUPABASE_URL
        self.anon_key = SUPABASE_ANON_KEY
        
        if not self.url or not self.anon_key:
            raise ValueError("SUPABASE_URL と SUPABASE_ANON_KEY が設定されていません")
        
        self.client: Client = create_client(self.url, self.anon_key)
    
    def get_client(self) -> Client:
        """Supabaseクライアントを取得"""
        return self.client
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """現在のユーザーを取得"""
        try:
            response = self.client.auth.get_user()
            return response.user
        except Exception:
            return None
    
    def sign_up_with_email(self, email: str, password: str) -> Dict[str, Any]:
        """メールアドレスでサインアップ"""
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password
            })
            return {
                "success": True,
                "user": response.user,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "user": None,
                "error": str(e)
            }
    
    def sign_in_with_email(self, email: str, password: str) -> Dict[str, Any]:
        """メールアドレスでサインイン"""
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return {
                "success": True,
                "user": response.user,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "user": None,
                "error": str(e)
            }
    
    def sign_in_with_google(self) -> Dict[str, Any]:
        """Googleでサインイン"""
        try:
            response = self.client.auth.sign_in_with_oauth({
                "provider": "google"
            })
            return {
                "success": True,
                "url": response.url,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "url": None,
                "error": str(e)
            }
    
    def sign_out(self) -> Dict[str, Any]:
        """サインアウト"""
        try:
            self.client.auth.sign_out()
            return {
                "success": True,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def reset_password(self, email: str) -> Dict[str, Any]:
        """パスワードリセット"""
        try:
            response = self.client.auth.reset_password_email(email)
            return {
                "success": True,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# グローバルインスタンス
supabase_config = None

def get_supabase_config() -> SupabaseConfig:
    """Supabase設定インスタンスを取得"""
    global supabase_config
    if supabase_config is None:
        supabase_config = SupabaseConfig()
    return supabase_config 