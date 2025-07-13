#!/usr/bin/env python3
"""
テスト用ユーザー作成スクリプト（環境変数対応版）
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from diary_manager_sqlite import DiaryManagerSQLite
from utils.config_manager import config

def main():
    """テスト用ユーザーを作成"""
    
    # データベースマネージャーを初期化（環境変数からパスを取得）
    db_path = config.get_database_path()
    diary_manager = DiaryManagerSQLite(db_path)
    diary_manager.ensure_database()
    
    print("=== テスト用ユーザー作成 ===\n")
    
    # 環境変数からパスワードを取得
    test_users = [
        {"username": "testuser", "password": config.get_test_user_password()},
        {"username": "admin", "password": config.get_admin_password()},
        {"username": "demo", "password": config.get_demo_password()}
    ]
    
    # ユーザーを作成
    for user in test_users:
        success = diary_manager.create_user(user["username"], user["password"])
        if success:
            print(f"✅ ユーザー作成成功: {user['username']}")
        else:
            print(f"❌ ユーザー作成失敗: {user['username']} (既に存在する可能性)")
    
    print("\n=== 作成完了 ===")
    print("以下のユーザーでログインできます:")
    for user in test_users:
        print(f"- ユーザー名: {user['username']}, パスワード: {user['password']}")
    
    print(f"\n💡 パスワードを変更する場合は .env ファイルを編集してください")

if __name__ == "__main__":
    main() 