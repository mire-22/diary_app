#!/usr/bin/env python3
"""
デバッグ用テストスクリプト
特定のテストケースを個別に実行してデバッグできます
"""

import sys
import os
import tempfile
import sqlite3

# プロジェクトのルートディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.diary_manager_sqlite import DiaryManagerSQLite

def debug_basic_functionality():
    """基本的な機能のデバッグ"""
    print("=== 基本機能デバッグ ===")
    
    # 一時的なデータベースファイルを作成
    temp_dir = tempfile.mkdtemp()
    test_db_path = os.path.join(temp_dir, "debug_test.db")
    
    try:
        print(f"テストデータベース: {test_db_path}")
        
        # DiaryManagerSQLiteインスタンスを作成
        diary_manager = DiaryManagerSQLite(test_db_path)
        print("✅ DiaryManagerSQLiteインスタンス作成成功")
        
        # 基本的なエントリを追加
        test_entry = {
            'id': 'debug_test_001',
            'created_at': '2025-01-01 10:00:00',
            'date': '2025-01-01',
            'text': 'デバッグテスト用の日記',
            'question': 'デバッグは成功しましたか？',
            'user_id': 'debug_user'
        }
        
        entry_id = diary_manager.add_diary_entry(test_entry)
        print(f"✅ エントリ追加成功: {entry_id}")
        
        # データを取得して確認
        all_data = diary_manager.get_all_diary_data()
        print(f"✅ データ取得成功: {len(all_data)}件")
        
        if all_data:
            print(f"取得したデータ: {all_data[0]['text']}")
        
        # データベースの構造を確認
        conn = sqlite3.connect(test_db_path)
        cur = conn.cursor()
        
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cur.fetchall()]
        print(f"✅ テーブル一覧: {tables}")
        
        # 各テーブルのレコード数を確認
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            print(f"  - {table}: {count}件")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # クリーンアップ
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
        print("✅ クリーンアップ完了")

def debug_complex_data():
    """複雑なデータのデバッグ"""
    print("\n=== 複雑データデバッグ ===")
    
    temp_dir = tempfile.mkdtemp()
    test_db_path = os.path.join(temp_dir, "debug_complex.db")
    
    try:
        diary_manager = DiaryManagerSQLite(test_db_path)
        
        # 複雑なエントリを追加
        complex_entry = {
            'id': 'debug_complex_001',
            'created_at': '2025-01-02 15:30:00',
            'date': '2025-01-02',
            'text': '複雑なデバッグテスト',
            'question': '複雑なデータは正しく保存されますか？',
            'user_id': 'debug_user',
            'emotions': ['嬉しい', '緊張', '期待'],
            'topics': ['仕事', '家族', '趣味'],
            'thoughts': ['頑張ろう', '感謝', '成長'],
            'goals': ['健康維持', '学習', '人間関係'],
            'followup_questions': ['明日の予定は？', '週末の計画は？', '来月の目標は？'],
            'qa_chain': [
                {'question': '今日の気分は？', 'answer': 'とても良いです', 'created_at': '2025-01-02 15:35:00'},
                {'question': '何か困ったことは？', 'answer': '特にありません', 'created_at': '2025-01-02 15:40:00'},
                {'question': '明日の目標は？', 'answer': '早起きして運動する', 'created_at': '2025-01-02 15:45:00'}
            ]
        }
        
        entry_id = diary_manager.add_diary_entry(complex_entry)
        print(f"✅ 複雑エントリ追加成功: {entry_id}")
        
        # データを取得して確認
        all_data = diary_manager.get_all_diary_data()
        if all_data:
            saved_entry = all_data[0]
            print(f"✅ 基本データ: {saved_entry['text']}")
            print(f"✅ 感情: {saved_entry['emotions']}")
            print(f"✅ トピック: {saved_entry['topics']}")
            print(f"✅ 思考: {saved_entry['thoughts']}")
            print(f"✅ 目標: {saved_entry['goals']}")
            print(f"✅ 追加質問: {saved_entry['followup_questions']}")
            print(f"✅ Q&A履歴: {len(saved_entry['qa_chain'])}件")
            
            for i, qa in enumerate(saved_entry['qa_chain']):
                print(f"  Q&A{i+1}: {qa['question']} → {qa['answer']}")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # クリーンアップ
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
        print("✅ クリーンアップ完了")

def debug_error_handling():
    """エラーハンドリングのデバッグ"""
    print("\n=== エラーハンドリングデバッグ ===")
    
    # 無効なパスでのテスト
    try:
        print("無効なパスでのテスト...")
        diary_manager = DiaryManagerSQLite("/invalid/path/test.db")
        print("❌ エラーが発生すべきでした")
    except Exception as e:
        print(f"✅ 期待されるエラー: {e}")
    
    # 正常なパスでのテスト
    temp_dir = tempfile.mkdtemp()
    test_db_path = os.path.join(temp_dir, "debug_error.db")
    
    try:
        diary_manager = DiaryManagerSQLite(test_db_path)
        print("✅ 正常なパスでの作成成功")
        
        # 存在しないエントリの削除テスト
        result = diary_manager.delete_diary_entry("nonexistent_id")
        print(f"✅ 存在しないエントリ削除: {result} (期待値: False)")
        
        # 存在しないエントリの更新テスト
        result = diary_manager.update_diary_entry("nonexistent_id", {"text": "新しいテキスト"})
        print(f"✅ 存在しないエントリ更新: {result} (期待値: False)")
        
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # クリーンアップ
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
        print("✅ クリーンアップ完了")

def main():
    """メイン関数"""
    print("DiaryManagerSQLite デバッグテスト")
    print("=" * 50)
    
    # 各デバッグ関数を実行
    debug_basic_functionality()
    debug_complex_data()
    debug_error_handling()
    
    print("\n" + "=" * 50)
    print("デバッグテスト完了")

if __name__ == '__main__':
    main() 