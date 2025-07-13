import pytest
import tempfile
import os
import sqlite3
from unittest.mock import patch, MagicMock
import json

from src.diary_manager_sqlite import DiaryManagerSQLite


@pytest.fixture
def diary_manager():
    """テスト用のDiaryManagerSQLiteインスタンスを作成"""
    # 一時的なデータベースファイルを作成
    temp_dir = tempfile.mkdtemp()
    test_db_path = os.path.join(temp_dir, "test_diary.db")

    # DiaryManagerSQLiteインスタンスを作成
    manager = DiaryManagerSQLite(test_db_path)

    yield manager  # テスト実行

    # クリーンアップ
    try:
        # データベース接続を確実に閉じる
        if hasattr(manager, '_conn') and manager._conn:
            manager._conn.close()

        # 少し待ってからファイルを削除
        import time
        time.sleep(0.1)

        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
    except (PermissionError, OSError):
        # Windowsでファイルが使用中の場合は無視
        pass


def test_ensure_database_creates_tables(diary_manager):
    """データベースとテーブルが正しく作成されることをテスト"""
    # データベースファイルが存在することを確認
    assert os.path.exists(diary_manager.db_path)

    # テーブルが作成されていることを確認
    conn = sqlite3.connect(diary_manager.db_path)
    cur = conn.cursor()

    # テーブル一覧を取得
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cur.fetchall()]

    # 基本的なテーブルが存在することを確認
    assert 'diary_entries' in tables

    # diary_entriesテーブルの構造を確認
    cur.execute("PRAGMA table_info(diary_entries)")
    columns = {row[1]: row[2] for row in cur.fetchall()}

    expected_columns = {
        'id': 'TEXT',
        'original_id': 'TEXT', 
        'created_at': 'TEXT',
        'date': 'TEXT',
        'text': 'TEXT',
        'question': 'TEXT',
        'user_id': 'TEXT'
    }

    for col_name, col_type in expected_columns.items():
        assert col_name in columns
        assert columns[col_name] == col_type

    conn.close()


def test_add_diary_entry_basic(diary_manager):
    """基本的な日記エントリの追加をテスト"""
    test_entry = {
        'id': 'test_123',
        'created_at': '2025-01-01 10:00:00',
        'date': '2025-01-01',
        'text': 'テスト日記です',
        'question': '今日はどうでしたか？',
        'user_id': 'test_user'
    }
    
    # エントリを追加
    entry_id = diary_manager.add_diary_entry(test_entry)
    
    # 戻り値がUUID形式であることを確認
    assert isinstance(entry_id, str)
    assert len(entry_id) > 0
    
    # データベースに正しく保存されていることを確認
    all_data = diary_manager.get_all_diary_data()
    assert len(all_data) == 1
    
    saved_entry = all_data[0]
    assert saved_entry['text'] == test_entry['text']
    assert saved_entry['date'] == test_entry['date']
    assert saved_entry['question'] == test_entry['question']
    assert saved_entry['user_id'] == test_entry['user_id']


def test_add_diary_entry_with_related_data(diary_manager):
    """関連データ（感情、トピック等）を含む日記エントリの追加をテスト"""
    test_entry = {
        'id': 'test_456',
        'created_at': '2025-01-02 15:30:00',
        'date': '2025-01-02',
        'text': '複雑な日記エントリ',
        'question': '今日の気分は？',
        'user_id': 'test_user',
        'emotions': ['嬉しい', '緊張'],
        'topics': ['仕事', '家族'],
        'thoughts': ['頑張ろう', '感謝'],
        'goals': ['健康維持', '学習'],
        'followup_questions': ['明日の予定は？', '週末の計画は？'],
        'qa_chain': [
            {'question': 'Q1', 'answer': 'A1', 'created_at': '2025-01-02 15:35:00'},
            {'question': 'Q2', 'answer': 'A2', 'created_at': '2025-01-02 15:40:00'}
        ]
    }
    
    # エントリを追加
    entry_id = diary_manager.add_diary_entry(test_entry)
    
    # データベースから取得して確認
    all_data = diary_manager.get_all_diary_data()
    assert len(all_data) == 1
    
    saved_entry = all_data[0]
    
    # 基本データの確認
    assert saved_entry['text'] == test_entry['text']
    # リストはアルファベット順でソートされるため、順序を考慮
    assert set(saved_entry['emotions']) == set(test_entry['emotions'])
    assert set(saved_entry['topics']) == set(test_entry['topics'])
    assert set(saved_entry['thoughts']) == set(test_entry['thoughts'])
    assert set(saved_entry['goals']) == set(test_entry['goals'])
    assert saved_entry['followup_questions'] == test_entry['followup_questions']
    
    # qa_chainの確認（order_indexでソートされる）
    assert len(saved_entry['qa_chain']) == 2
    assert saved_entry['qa_chain'][0]['question'] == 'Q1'
    assert saved_entry['qa_chain'][1]['question'] == 'Q2'


def test_get_all_diary_data_empty(diary_manager):
    """空のデータベースからのデータ取得をテスト"""
    data = diary_manager.get_all_diary_data()
    assert len(data) == 0
    assert isinstance(data, list)


def test_get_all_diary_data_multiple_entries(diary_manager):
    """複数のエントリがある場合のデータ取得をテスト"""
    # 複数のエントリを追加
    entries = [
        {
            'id': 'entry1',
            'created_at': '2025-01-01 10:00:00',
            'date': '2025-01-01',
            'text': '1番目の日記',
            'question': 'Q1',
            'user_id': 'user1'
        },
        {
            'id': 'entry2', 
            'created_at': '2025-01-02 15:00:00',
            'date': '2025-01-02',
            'text': '2番目の日記',
            'question': 'Q2',
            'user_id': 'user2'
        }
    ]
    
    for entry in entries:
        diary_manager.add_diary_entry(entry)
    
    # データを取得して確認
    all_data = diary_manager.get_all_diary_data()
    assert len(all_data) == 2
    
    # created_atの降順でソートされていることを確認
    assert all_data[0]['text'] == '2番目の日記'  # 新しい方が先
    assert all_data[1]['text'] == '1番目の日記'  # 古い方が後


def test_get_diary_by_date_range(diary_manager):
    """日付範囲でのデータ取得をテスト"""
    # 異なる日付のエントリを追加
    entries = [
        {
            'id': 'entry1',
            'created_at': '2025-01-01 10:00:00',
            'date': '2025-01-01',
            'text': '1月1日の日記',
            'question': 'Q1',
            'user_id': 'user1'
        },
        {
            'id': 'entry2',
            'created_at': '2025-01-15 15:00:00', 
            'date': '2025-01-15',
            'text': '1月15日の日記',
            'question': 'Q2',
            'user_id': 'user2'
        },
        {
            'id': 'entry3',
            'created_at': '2025-02-01 20:00:00',
            'date': '2025-02-01', 
            'text': '2月1日の日記',
            'question': 'Q3',
            'user_id': 'user3'
        }
    ]
    
    for entry in entries:
        diary_manager.add_diary_entry(entry)
    
    # 1月のデータを取得
    jan_data = diary_manager.get_diary_by_date_range('2025-01-01', '2025-01-31')
    assert len(jan_data) == 2
    
    # 1月10日から1月20日のデータを取得
    mid_jan_data = diary_manager.get_diary_by_date_range('2025-01-10', '2025-01-20')
    assert len(mid_jan_data) == 1
    assert mid_jan_data[0]['text'] == '1月15日の日記'


def test_delete_diary_entry(diary_manager):
    """日記エントリの削除をテスト"""
    # エントリを追加
    test_entry = {
        'id': 'delete_test',
        'created_at': '2025-01-01 10:00:00',
        'date': '2025-01-01',
        'text': '削除対象の日記',
        'question': '削除しますか？',
        'user_id': 'test_user'
    }
    
    entry_id = diary_manager.add_diary_entry(test_entry)
    
    # 削除前の確認
    all_data = diary_manager.get_all_diary_data()
    assert len(all_data) == 1
    
    # 削除を実行
    result = diary_manager.delete_diary_entry(entry_id)
    assert result is True
    
    # 削除後の確認
    all_data = diary_manager.get_all_diary_data()
    assert len(all_data) == 0


def test_delete_nonexistent_entry(diary_manager):
    """存在しないエントリの削除をテスト"""
    result = diary_manager.delete_diary_entry('nonexistent_id')
    assert result is False


def test_update_diary_entry(diary_manager):
    """日記エントリの更新をテスト"""
    # 元のエントリを追加
    original_entry = {
        'id': 'update_test',
        'created_at': '2025-01-01 10:00:00',
        'date': '2025-01-01',
        'text': '元のテキスト',
        'question': '元の質問',
        'user_id': 'test_user'
    }
    
    entry_id = diary_manager.add_diary_entry(original_entry)
    
    # 更新データ
    update_data = {
        'text': '更新されたテキスト',
        'question': '更新された質問'
    }
    
    # 更新を実行
    result = diary_manager.update_diary_entry(entry_id, update_data)
    assert result is True
    
    # 更新後の確認
    all_data = diary_manager.get_all_diary_data()
    assert len(all_data) == 1
    updated_entry = all_data[0]
    assert updated_entry['text'] == '更新されたテキスト'
    assert updated_entry['question'] == '更新された質問'
    # 更新されていないフィールドは元のまま
    assert updated_entry['date'] == '2025-01-01'


def test_update_nonexistent_entry(diary_manager):
    """存在しないエントリの更新をテスト"""
    update_data = {'text': '新しいテキスト'}
    result = diary_manager.update_diary_entry('nonexistent_id', update_data)
    assert result is False


def test_database_connection_error():
    """データベース接続エラーのテスト"""
    # Windowsでは無効なパスでもエラーが発生しない場合があるため、
    # より確実にエラーを発生させるテストに変更
    with pytest.raises(Exception):
        # 存在しないディレクトリのパスを使用
        invalid_db_path = "/invalid/path/test.db"
        DiaryManagerSQLite(invalid_db_path)
    
    # または、権限のないディレクトリを使用
    with pytest.raises(Exception):
        # Windowsのシステムディレクトリを使用（権限エラーが発生するはず）
        system_db_path = "C:/Windows/System32/test.db"
        DiaryManagerSQLite(system_db_path)


def test_sql_error_handling(diary_manager):
    """SQLエラーのハンドリングをテスト"""
    # 無効なSQLを実行しようとする
            with patch.object(diary_manager, '_upsert_related_data') as mock_insert:
        mock_insert.side_effect = sqlite3.Error("SQL error")
        
        test_entry = {
            'id': 'error_test',
            'created_at': '2025-01-01 10:00:00',
            'date': '2025-01-01',
            'text': 'エラーテスト',
            'question': 'エラーが発生しますか？',
            'user_id': 'test_user'
        }
        
        with pytest.raises(sqlite3.Error):
            diary_manager.add_diary_entry(test_entry)


def test_empty_related_data(diary_manager):
    """空の関連データの処理をテスト"""
    test_entry = {
        'id': 'empty_test',
        'created_at': '2025-01-01 10:00:00',
        'date': '2025-01-01',
        'text': '空の関連データテスト',
        'question': '空のデータは大丈夫？',
        'user_id': 'test_user',
        'emotions': [],
        'topics': [],
        'thoughts': [],
        'goals': [],
        'followup_questions': [],
        'qa_chain': []
    }
    
    # エラーが発生しないことを確認
    entry_id = diary_manager.add_diary_entry(test_entry)
    assert isinstance(entry_id, str)
    
    # データが正しく保存されていることを確認
    all_data = diary_manager.get_all_diary_data()
    assert len(all_data) == 1
    saved_entry = all_data[0]
    assert saved_entry['emotions'] == []
    assert saved_entry['topics'] == []
    assert saved_entry['thoughts'] == []
    assert saved_entry['goals'] == []
    assert saved_entry['followup_questions'] == []
    assert saved_entry['qa_chain'] == []


def test_upsert_behavior(diary_manager):
    """UPSERT動作をテスト"""
    # 最初のエントリを追加
    test_entry = {
        'id': 'upsert_test',
        'created_at': '2025-01-01 10:00:00',
        'date': '2025-01-01',
        'text': '最初のテキスト',
        'question': '最初の質問',
        'user_id': 'test_user'
    }
    
    entry_id_1 = diary_manager.add_diary_entry(test_entry)
    assert entry_id_1 == 'upsert_test'  # 指定したIDが使用される
    
    # 同じIDで異なる内容を追加（UPDATEされる）
    updated_entry = {
        'id': 'upsert_test',
        'created_at': '2025-01-01 11:00:00',
        'date': '2025-01-01',
        'text': '更新されたテキスト',
        'question': '更新された質問',
        'user_id': 'test_user'
    }
    
    entry_id_2 = diary_manager.add_diary_entry(updated_entry)
    assert entry_id_2 == 'upsert_test'  # 同じIDが返される
    
    # データベースに1件しか存在しないことを確認
    all_data = diary_manager.get_all_diary_data()
    assert len(all_data) == 1
    
    # 更新された内容が保存されていることを確認
    saved_entry = all_data[0]
    assert saved_entry['text'] == '更新されたテキスト'
    assert saved_entry['question'] == '更新された質問'


def test_followup_questions_management(diary_manager):
    """フォローアップ質問の管理をテスト"""
    # 基本エントリを追加
    test_entry = {
        'id': 'followup_test',
        'created_at': '2025-01-01 10:00:00',
        'date': '2025-01-01',
        'text': 'フォローアップテスト',
        'question': '基本質問',
        'user_id': 'test_user'
    }
    
    entry_id = diary_manager.add_diary_entry(test_entry)
    
    # フォローアップ質問を追加
    followup_questions = ['追加質問1', '追加質問2', '追加質問3']
    result = diary_manager.add_followup_questions(entry_id, followup_questions)
    assert result is True
    
    # データを取得して確認
    all_data = diary_manager.get_all_diary_data()
    assert len(all_data) == 1
    saved_entry = all_data[0]
    assert saved_entry['followup_questions'] == followup_questions
    
    # フォローアップ質問を更新
    new_followup_questions = ['新しい質問1', '新しい質問2']
    result = diary_manager.add_followup_questions(entry_id, new_followup_questions)
    assert result is True
    
    # 更新されたデータを確認
    all_data = diary_manager.get_all_diary_data()
    saved_entry = all_data[0]
    assert saved_entry['followup_questions'] == new_followup_questions


def test_qa_chain_management(diary_manager):
    """Q&A履歴の管理をテスト"""
    # 基本エントリを追加
    test_entry = {
        'id': 'qa_test',
        'created_at': '2025-01-01 10:00:00',
        'date': '2025-01-01',
        'text': 'Q&Aテスト',
        'question': '基本質問',
        'user_id': 'test_user'
    }
    
    entry_id = diary_manager.add_diary_entry(test_entry)
    
    # Q&A履歴を追加
    qa_chain = [
        {'question': 'Q1', 'answer': 'A1', 'created_at': '2025-01-01 10:05:00'},
        {'question': 'Q2', 'answer': 'A2', 'created_at': '2025-01-01 10:10:00'}
    ]
    result = diary_manager.add_qa_chain(entry_id, qa_chain)
    assert result is True
    
    # データを取得して確認
    all_data = diary_manager.get_all_diary_data()
    assert len(all_data) == 1
    saved_entry = all_data[0]
    assert len(saved_entry['qa_chain']) == 2
    assert saved_entry['qa_chain'][0]['question'] == 'Q1'
    assert saved_entry['qa_chain'][1]['question'] == 'Q2'
    
    # Q&A履歴を更新
    new_qa_chain = [
        {'question': '新しいQ1', 'answer': '新しいA1', 'created_at': '2025-01-01 11:00:00'}
    ]
    result = diary_manager.add_qa_chain(entry_id, new_qa_chain)
    assert result is True
    
    # 更新されたデータを確認
    all_data = diary_manager.get_all_diary_data()
    saved_entry = all_data[0]
    assert len(saved_entry['qa_chain']) == 1
    assert saved_entry['qa_chain'][0]['question'] == '新しいQ1'


def test_update_based_upsert_behavior(diary_manager):
    """UPDATEベースのUPSERT動作をテスト"""
    # 最初のエントリを追加
    test_entry = {
        'id': 'update_test',
        'created_at': '2025-01-01 10:00:00',
        'date': '2025-01-01',
        'text': '最初のテキスト',
        'question': '最初の質問',
        'user_id': 'test_user',
        'topics': ['仕事', '家族'],
        'emotions': ['嬉しい', '緊張'],
        'followup_questions': ['質問1', '質問2'],
        'qa_chain': [
            {'question': 'Q1', 'answer': 'A1', 'created_at': '2025-01-01 10:05:00'}
        ]
    }
    
    entry_id = diary_manager.add_diary_entry(test_entry)
    assert entry_id == 'update_test'
    
    # 同じIDで異なる内容を追加（UPDATEされる）
    updated_entry = {
        'id': 'update_test',
        'created_at': '2025-01-01 11:00:00',
        'date': '2025-01-01',
        'text': '更新されたテキスト',
        'question': '更新された質問',
        'user_id': 'test_user',
        'topics': ['仕事', '家族', '健康'],  # 1つ追加
        'emotions': ['嬉しい'],  # 1つ削除
        'followup_questions': ['新しい質問1', '新しい質問2', '新しい質問3'],  # 全て変更
        'qa_chain': [
            {'question': '新しいQ1', 'answer': '新しいA1', 'created_at': '2025-01-01 10:05:00'},
            {'question': '新しいQ2', 'answer': '新しいA2', 'created_at': '2025-01-01 10:10:00'}
        ]
    }
    
    entry_id_2 = diary_manager.add_diary_entry(updated_entry)
    assert entry_id_2 == 'update_test'
    
    # データベースに1件しか存在しないことを確認
    all_data = diary_manager.get_all_diary_data()
    assert len(all_data) == 1
    
    # 更新された内容が保存されていることを確認
    saved_entry = all_data[0]
    assert saved_entry['text'] == '更新されたテキスト'
    assert saved_entry['question'] == '更新された質問'
    assert set(saved_entry['topics']) == {'仕事', '家族', '健康'}
    assert set(saved_entry['emotions']) == {'嬉しい'}
    assert saved_entry['followup_questions'] == ['新しい質問1', '新しい質問2', '新しい質問3']
    assert len(saved_entry['qa_chain']) == 2
    assert saved_entry['qa_chain'][0]['question'] == '新しいQ1'
    assert saved_entry['qa_chain'][1]['question'] == '新しいQ2'


def test_update_based_followup_questions(diary_manager):
    """UPDATEベースのフォローアップ質問管理をテスト"""
    # 基本エントリを追加
    test_entry = {
        'id': 'update_followup_test',
        'created_at': '2025-01-01 10:00:00',
        'date': '2025-01-01',
        'text': 'UPDATEベーステスト',
        'question': '基本質問',
        'user_id': 'test_user'
    }
    
    entry_id = diary_manager.add_diary_entry(test_entry)
    
    # 最初のフォローアップ質問を追加
    followup_questions_1 = ['質問1', '質問2']
    result = diary_manager.add_followup_questions(entry_id, followup_questions_1)
    assert result is True
    
    # データを取得して確認
    all_data = diary_manager.get_all_diary_data()
    saved_entry = all_data[0]
    assert saved_entry['followup_questions'] == followup_questions_1
    
    # フォローアップ質問を更新（1つ削除、1つ変更、1つ追加）
    followup_questions_2 = ['変更された質問1', '新しい質問3']
    result = diary_manager.add_followup_questions(entry_id, followup_questions_2)
    assert result is True
    
    # 更新されたデータを確認
    all_data = diary_manager.get_all_diary_data()
    saved_entry = all_data[0]
    assert saved_entry['followup_questions'] == followup_questions_2
    
    # フォローアップ質問をさらに更新（全て削除）
    followup_questions_3 = []
    result = diary_manager.add_followup_questions(entry_id, followup_questions_3)
    assert result is True
    
    # 空のデータを確認
    all_data = diary_manager.get_all_diary_data()
    saved_entry = all_data[0]
    assert saved_entry['followup_questions'] == []


def test_update_based_qa_chain(diary_manager):
    """UPDATEベースのQ&A履歴管理をテスト"""
    # 基本エントリを追加
    test_entry = {
        'id': 'update_qa_test',
        'created_at': '2025-01-01 10:00:00',
        'date': '2025-01-01',
        'text': 'UPDATEベースQ&Aテスト',
        'question': '基本質問',
        'user_id': 'test_user'
    }
    
    entry_id = diary_manager.add_diary_entry(test_entry)
    
    # 最初のQ&A履歴を追加
    qa_chain_1 = [
        {'question': 'Q1', 'answer': 'A1', 'created_at': '2025-01-01 10:05:00'},
        {'question': 'Q2', 'answer': 'A2', 'created_at': '2025-01-01 10:10:00'}
    ]
    result = diary_manager.add_qa_chain(entry_id, qa_chain_1)
    assert result is True
    
    # データを取得して確認
    all_data = diary_manager.get_all_diary_data()
    saved_entry = all_data[0]
    assert len(saved_entry['qa_chain']) == 2
    assert saved_entry['qa_chain'][0]['question'] == 'Q1'
    assert saved_entry['qa_chain'][1]['question'] == 'Q2'
    
    # Q&A履歴を更新（1つ変更、1つ削除、1つ追加）
    qa_chain_2 = [
        {'question': '変更されたQ1', 'answer': '変更されたA1', 'created_at': '2025-01-01 10:05:00'},
        {'question': '新しいQ3', 'answer': '新しいA3', 'created_at': '2025-01-01 10:15:00'}
    ]
    result = diary_manager.add_qa_chain(entry_id, qa_chain_2)
    assert result is True
    
    # 更新されたデータを確認
    all_data = diary_manager.get_all_diary_data()
    saved_entry = all_data[0]
    assert len(saved_entry['qa_chain']) == 2
    assert saved_entry['qa_chain'][0]['question'] == '変更されたQ1'
    assert saved_entry['qa_chain'][1]['question'] == '新しいQ3'
    
    # Q&A履歴をさらに更新（全て削除）
    qa_chain_3 = []
    result = diary_manager.add_qa_chain(entry_id, qa_chain_3)
    assert result is True
    
    # 空のデータを確認
    all_data = diary_manager.get_all_diary_data()
    saved_entry = all_data[0]
    assert saved_entry['qa_chain'] == []
