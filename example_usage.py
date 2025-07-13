#!/usr/bin/env python3
"""
UPDATEベースの重複しない構造の使用例

このスクリプトは、最初の日記エントリをIDとして使用し、
フォローアップ質問をそれに紐づけて管理する方法を示します。
DELETEではなくUPDATEを使用して、より安全なデータ管理を実現します。
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from diary_manager_sqlite import DiaryManagerSQLite

def main():
    """UPDATEベースの構造の使用例"""
    
    # データベースマネージャーを初期化
    diary_manager = DiaryManagerSQLite("data/example_usage.db")
    diary_manager.ensure_database()
    
    print("=== UPDATEベースの重複しない構造の使用例 ===\n")
    
    # 1. 最初の日記エントリを作成
    print("1. 最初の日記エントリを作成")
    initial_entry = {
        'id': 'diary_2025_01_01',  # 最初のエントリのID
        'created_at': '2025-01-01 10:00:00',
        'date': '2025-01-01',
        'text': '今日は新しい年の始まりです。今年は健康に気をつけて過ごしたいと思います。',
        'question': '今日の気分はどうですか？',
        'user_id': 'user123',
        'topics': ['仕事', '家族'],
        'emotions': ['嬉しい', '緊張']
    }
    
    entry_id = diary_manager.add_diary_entry(initial_entry)
    print(f"   エントリID: {entry_id}")
    print(f"   テキスト: {initial_entry['text']}")
    print(f"   トピック: {initial_entry['topics']}")
    print(f"   感情: {initial_entry['emotions']}")
    
    # 2. 同じIDで内容を更新（安全なUPDATE）
    print("\n2. 同じIDで内容を更新（安全なUPDATE）")
    updated_entry = {
        'id': 'diary_2025_01_01',  # 同じID
        'created_at': '2025-01-01 11:00:00',
        'date': '2025-01-01',
        'text': '今日は新しい年の始まりです。今年は健康に気をつけて過ごしたいと思います。',
        'question': '今日の気分はどうですか？',
        'user_id': 'user123',
        'topics': ['仕事', '家族', '健康'],  # 1つ追加
        'emotions': ['嬉しい'],  # 1つ削除
        'followup_questions': ['具体的にどのような健康目標がありますか？', '今年の抱負は何ですか？'],
        'qa_chain': [
            {'question': '健康目標について教えてください', 'answer': '毎日30分の運動を続けたいです', 'created_at': '2025-01-01 10:30:00'}
        ]
    }
    
    entry_id_2 = diary_manager.add_diary_entry(updated_entry)
    print(f"   エントリID: {entry_id_2}")
    print(f"   トピック（更新後）: {updated_entry['topics']}")
    print(f"   感情（更新後）: {updated_entry['emotions']}")
    print(f"   フォローアップ質問数: {len(updated_entry['followup_questions'])}")
    print(f"   Q&A履歴数: {len(updated_entry['qa_chain'])}")
    
    # 3. 専用メソッドでフォローアップ質問を追加
    print("\n3. 専用メソッドでフォローアップ質問を追加")
    new_followup_questions = [
        '具体的にどのような健康目標がありますか？',
        '今年の抱負は何ですか？',
        '週末の予定はありますか？'
    ]
    
    result = diary_manager.add_followup_questions(entry_id, new_followup_questions)
    print(f"   追加結果: {result}")
    print(f"   新しいフォローアップ質問数: {len(new_followup_questions)}")
    
    # 4. フォローアップ質問を更新（1つ削除）
    print("\n4. フォローアップ質問を更新（1つ削除）")
    updated_followup_questions = [
        '具体的にどのような健康目標がありますか？',
        '今年の抱負は何ですか？'
    ]
    
    result = diary_manager.add_followup_questions(entry_id, updated_followup_questions)
    print(f"   更新結果: {result}")
    print(f"   更新後のフォローアップ質問数: {len(updated_followup_questions)}")
    
    # 5. 専用メソッドでQ&A履歴を追加
    print("\n5. 専用メソッドでQ&A履歴を追加")
    new_qa_chain = [
        {'question': '健康目標について教えてください', 'answer': '毎日30分の運動を続けたいです', 'created_at': '2025-01-01 10:30:00'},
        {'question': '運動の種類は何を考えていますか？', 'answer': 'ウォーキングと筋トレを組み合わせたいです', 'created_at': '2025-01-01 10:35:00'},
        {'question': '週末の予定はありますか？', 'answer': '家族と一緒に公園で運動する予定です', 'created_at': '2025-01-01 10:40:00'}
    ]
    
    result = diary_manager.add_qa_chain(entry_id, new_qa_chain)
    print(f"   追加結果: {result}")
    print(f"   新しいQ&A履歴数: {len(new_qa_chain)}")
    
    # 6. Q&A履歴を更新（1つ変更、1つ削除）
    print("\n6. Q&A履歴を更新（1つ変更、1つ削除）")
    updated_qa_chain = [
        {'question': '健康目標について教えてください', 'answer': '毎日30分の運動と食事管理を続けたいです', 'created_at': '2025-01-01 10:30:00'},
        {'question': '週末の予定はありますか？', 'answer': '家族と一緒に公園で運動する予定です', 'created_at': '2025-01-01 10:40:00'}
    ]
    
    result = diary_manager.add_qa_chain(entry_id, updated_qa_chain)
    print(f"   更新結果: {result}")
    print(f"   更新後のQ&A履歴数: {len(updated_qa_chain)}")
    
    # 7. 最終的なデータを確認
    print("\n7. 最終的なデータを確認")
    all_data = diary_manager.get_all_diary_data()
    assert len(all_data) == 1  # 重複がないことを確認
    
    final_entry = all_data[0]
    print(f"   エントリID: {final_entry['id']}")
    print(f"   テキスト: {final_entry['text']}")
    print(f"   トピック: {final_entry['topics']}")
    print(f"   感情: {final_entry['emotions']}")
    print(f"   フォローアップ質問数: {len(final_entry['followup_questions'])}")
    print(f"   Q&A履歴数: {len(final_entry['qa_chain'])}")
    
    # 8. 別の日記エントリを追加（重複しない）
    print("\n8. 別の日記エントリを追加（重複しない）")
    second_entry = {
        'id': 'diary_2025_01_02',  # 異なるID
        'created_at': '2025-01-02 09:00:00',
        'date': '2025-01-02',
        'text': '今日は仕事が忙しかったですが、充実していました。',
        'question': '今日の仕事はどうでしたか？',
        'user_id': 'user123'
    }
    
    second_entry_id = diary_manager.add_diary_entry(second_entry)
    print(f"   エントリID: {second_entry_id}")
    print(f"   テキスト: {second_entry['text']}")
    
    # 9. 最終確認
    print("\n9. 最終確認")
    all_data = diary_manager.get_all_diary_data()
    print(f"   総エントリ数: {len(all_data)}")
    print(f"   エントリ1: {all_data[0]['id']} - {all_data[0]['text'][:30]}...")
    print(f"   エントリ2: {all_data[1]['id']} - {all_data[1]['text'][:30]}...")
    
    print("\n=== UPDATEベース構造の利点 ===")
    print("✓ 同じIDで複数回追加しても重複しない")
    print("✓ 既存データを安全に更新（DELETEではなくUPDATE）")
    print("✓ フォローアップ質問は専用メソッドで管理可能")
    print("✓ Q&A履歴は専用メソッドで管理可能")
    print("✓ データの整合性が保たれる")
    print("✓ パフォーマンスが向上する")
    print("✓ データ損失のリスクが低減")

if __name__ == "__main__":
    main() 