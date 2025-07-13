import sqlite3
import sys
import traceback
from src.diary_manager_sqlite import DiaryManagerSQLite

def test_date_update():
    """日付更新機能をテスト"""
    print("=== 日付更新機能テスト ===")
    
    try:
        # DiaryManagerSQLiteのインスタンスを作成
        diary_manager = DiaryManagerSQLite()
        
        # 全データを取得
        all_data = diary_manager.get_all_diary_data()
        print(f"総エントリ数: {len(all_data)}")
        
        if all_data:
            # 最初のエントリをテスト対象とする
            test_entry = all_data[0]
            test_id = test_entry['id']
            current_date = test_entry['date']
            
            print(f"テスト対象エントリ:")
            print(f"  ID: {test_id}")
            print(f"  現在の日付: {current_date}")
            print(f"  テキスト: {test_entry['text'][:50]}...")
            
            # 新しい日付を設定（現在の日付を1日前に変更）
            from datetime import datetime, timedelta
            current_dt = datetime.strptime(current_date, '%Y-%m-%d')
            new_dt = current_dt - timedelta(days=1)
            new_date = new_dt.strftime('%Y-%m-%d')
            
            print(f"  新しい日付: {new_date}")
            
            # 日付を更新
            print("\n日付更新を実行...")
            result = diary_manager.update_diary_entry(test_id, {'date': new_date, **test_entry})
            
            if result:
                print("✅ 更新成功")
                
                # 更新後のデータを確認
                updated_data = diary_manager.get_all_diary_data()
                updated_entry = None
                for entry in updated_data:
                    if entry['id'] == test_id:
                        updated_entry = entry
                        break
                
                if updated_entry:
                    print(f"更新後の日付: {updated_entry['date']}")
                    if updated_entry['date'] == new_date:
                        print("✅ 日付が正しく更新されました")
                    else:
                        print("❌ 日付の更新が反映されていません")
                else:
                    print("❌ 更新後のエントリが見つかりません")
            else:
                print("❌ 更新失敗")
        
        # データベースの直接確認
        print("\n=== データベース直接確認 ===")
        conn = sqlite3.connect('data/diary_normalized.db')
        cur = conn.cursor()
        
        cur.execute('SELECT id, original_id, date, text FROM diary_entries LIMIT 5')
        entries = cur.fetchall()
        
        print("データベース内のエントリ:")
        for entry in entries:
            print(f"  UUID: {entry[0][:8]}...")
            print(f"  Original ID: {entry[1]}")
            print(f"  日付: {entry[2]}")
            print(f"  テキスト: {entry[3][:30]}...")
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    test_date_update() 