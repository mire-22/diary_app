# テストガイド

このディレクトリには、`DiaryManagerSQLite`クラスの単体テストが含まれています。

## 注意事項（パス設定）

- テストコード内で`sys.path`は使いません。
- `src`ディレクトリのimportは、
  - `PYTHONPATH`環境変数を使う
  - もしくは`tests/conftest.py`で自動設定されます
- もしimportエラーが出る場合は、以下のように実行してください：

```bash
PYTHONPATH=src pytest -svv tests
```
（Windowsの場合）
```bat
set PYTHONPATH=src
pytest -svv tests
```

## ファイル構成

- `test_diary_manager_sqlite.py` - メインの単体テストファイル
- `__init__.py` - テストパッケージの初期化ファイル
- `conftest.py` - importパス自動調整用

## テストの実行方法

### 1. pytestでの全テスト実行（推奨）

プロジェクトのルートディレクトリで以下のコマンドを実行：

```bash
pytest -svv tests
```

### 2. 詳細出力でのテスト実行

```bash
pytest -svv --tb=long tests
```

### 3. カバレッジ付きテスト実行

```bash
pytest -svv --cov=src tests
```

### 4. 特定のテストのみ実行

```bash
# 特定のテストファイル
pytest -svv tests/test_diary_manager_sqlite.py

# 特定のテスト関数
pytest -svv tests/test_diary_manager_sqlite.py::test_add_diary_entry_basic

# 特定のパターンにマッチするテスト
pytest -svv -k "basic" tests
```

### 5. 従来のunittestでの実行

```bash
python run_tests.py
```

### 6. デバッグテストの実行

デバッグ用のスクリプトを実行：

```bash
python debug_test.py
```

## テストケース一覧

### 基本機能テスト
- `test_ensure_database_creates_tables()` - データベースとテーブルの作成
- `test_add_diary_entry_basic()` - 基本的な日記エントリの追加
- `test_get_all_diary_data_empty()` - 空データベースからの取得
- `test_get_all_diary_data_multiple_entries()` - 複数エントリの取得

### 複雑データテスト
- `test_add_diary_entry_with_related_data()` - 関連データ（感情、トピック等）を含むエントリ
- `test_get_diary_by_date_range()` - 日付範囲でのデータ取得

### CRUD操作テスト
- `test_delete_diary_entry()` - エントリの削除
- `test_delete_nonexistent_entry()` - 存在しないエントリの削除
- `test_update_diary_entry()` - エントリの更新
- `test_update_nonexistent_entry()` - 存在しないエントリの更新

### エラーハンドリングテスト
- `test_database_connection_error()` - データベース接続エラー
- `test_sql_error_handling()` - SQLエラーの処理
- `test_empty_related_data()` - 空の関連データの処理

## デバッグのヒント

### 1. 特定のテストのみ実行

```bash
# 特定のテスト関数のみ実行
pytest -svv tests/test_diary_manager_sqlite.py::test_add_diary_entry_basic
```

### 2. テストデータベースの確認

テストでは一時的なSQLiteデータベースファイルが作成されます。デバッグ時に実際のデータベースファイルを確認したい場合：

```python
import sqlite3

# テストデータベースに接続
conn = sqlite3.connect("path/to/test.db")
cur = conn.cursor()

# テーブル一覧を確認
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()
print(tables)

# 特定のテーブルの内容を確認
cur.execute("SELECT * FROM diary_entries")
entries = cur.fetchall()
print(entries)

conn.close()
```

### 3. ログ出力の追加

テスト中にデバッグ情報を出力したい場合：

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_debug_example(self):
    logger.debug("デバッグ情報を出力")
    # テストコード
```

## テストの追加方法

新しいテストケースを追加する場合：

1. ファイルに新しいテスト関数を追加
2. 関数名は`test_`で始める
3. `diary_manager` fixtureを引数に取る
4. 一時ファイルはfixtureで自動的にクリーンアップされる

```python
def test_new_feature(diary_manager):
    """新しい機能のテスト"""
    # テストコード
    pass
```

## 注意事項

- テストでは一時的なデータベースファイルを使用します
- テスト実行後は自動的にクリーンアップされます
- 本番データベースは影響を受けません
- テストは独立して実行できるように設計されています 