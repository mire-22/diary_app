"""
ユーザー認証・認可機能を管理するクラス
"""

import hashlib
import os
import uuid
from typing import Optional, Dict, Any
from datetime import datetime
import sqlite3

class UserManager:
    """ユーザー認証・認可機能を管理するクラス"""
    
    def __init__(self, db_path: str = "data/diary_normalized.db"):
        self.db_path = db_path
        self._ensure_users_table()
    
    def _ensure_users_table(self) -> None:
        """ユーザーテーブルの存在確認と作成"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        try:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    last_login TEXT
                )
            ''')
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _hash_password(self, password: str) -> str:
        """パスワードをハッシュ化"""
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return salt.hex() + key.hex()
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """パスワードを検証"""
        try:
            salt = bytes.fromhex(hashed[:64])
            key = bytes.fromhex(hashed[64:])
            new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
            return key == new_key
        except:
            return False
    
    def create_user(self, username: str, password: str) -> bool:
        """新規ユーザーを作成"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        try:
            # ユーザー名の重複チェック
            cur.execute('SELECT id FROM users WHERE username = ?', (username,))
            if cur.fetchone():
                return False
            
            # ユーザーを作成
            user_id = str(uuid.uuid4())
            password_hash = self._hash_password(password)
            
            cur.execute('''
                INSERT INTO users (id, username, password_hash, created_at)
                VALUES (?, ?, ?, ?)
            ''', (user_id, username, password_hash, datetime.now().isoformat()))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """ユーザー認証"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        try:
            cur.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
            result = cur.fetchone()
            
            if result and self._verify_password(password, result[1]):
                # 最終ログイン時刻を更新
                cur.execute('UPDATE users SET last_login = ? WHERE id = ?', 
                           (datetime.now().isoformat(), result[0]))
                conn.commit()
                return result[0]
            
            return None
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """ユーザーIDでユーザー情報を取得"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        try:
            cur.execute('''
                SELECT id, username, created_at, last_login
                FROM users WHERE id = ?
            ''', (user_id,))
            
            result = cur.fetchone()
            if result:
                return {
                    'id': result[0],
                    'username': result[1],
                    'created_at': result[2],
                    'last_login': result[3]
                }
            
            return None
            
        finally:
            conn.close()
    
    def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """パスワード変更"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        try:
            # 現在のパスワードを確認
            cur.execute('SELECT password_hash FROM users WHERE id = ?', (user_id,))
            result = cur.fetchone()
            
            if not result or not self._verify_password(current_password, result[0]):
                return False
            
            # 新しいパスワードで更新
            new_password_hash = self._hash_password(new_password)
            cur.execute('UPDATE users SET password_hash = ? WHERE id = ?', 
                       (new_password_hash, user_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def delete_user(self, user_id: str) -> bool:
        """ユーザー削除"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        try:
            cur.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
            return cur.rowcount > 0
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_all_users(self) -> list[Dict[str, Any]]:
        """全ユーザー一覧を取得（管理者用）"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        try:
            cur.execute('''
                SELECT id, username, created_at, last_login
                FROM users ORDER BY created_at DESC
            ''')
            
            users = []
            for row in cur.fetchall():
                users.append({
                    'id': row[0],
                    'username': row[1],
                    'created_at': row[2],
                    'last_login': row[3]
                })
            
            return users
            
        finally:
            conn.close() 