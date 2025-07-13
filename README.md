# AI日記アプリ

---

## 概要

このアプリは、日記データをAIで分析し、感情・トピック・Q&Aなどを安全かつ効率的に管理できる日記アプリです。

- **重複しない構造**：エントリIDによる一意管理
- **UPDATEベース**：既存データを安全に更新、データ損失リスク低減
- **専用メソッド**：フォローアップ質問やQ&A履歴も直感的に管理
- **キャッシュ・データ分離**：`data/`フォルダで一元管理
- **ユーティリティ分離**：`src/utils/`に汎用機能を整理

---

## ディレクトリ構成

```
latest_suika/
├── data/                # DB・キャッシュ・一時ファイル
│   ├── diary_normalized.db
│   ├── diary_backup.db
│   ├── example_usage.db
│   └── emotion_cache.json
├── src/                 # アプリ本体
│   ├── diary_app.py     # Streamlitアプリ本体
│   ├── diary_manager_sqlite.py
│   ├── ai_analyzer.py
│   ├── period_analyzer.py
│   ├── ui_components.py
│   ├── prompts/         # プロンプトテンプレート
│   └── utils/           # ユーティリティ群
│       ├── prompt_manager.py
│       ├── emotion_analyzer.py
│       ├── tag_analyzer.py
│       └── legacy_database.py
├── tests/               # テストコード
│   ├── test_diary_manager_sqlite.py
│   └── ...
├── run_app.py           # 実行用エントリポイント
├── example_usage.py     # サンプルスクリプト
├── requirements.txt     # 依存パッケージ
└── README.md            # このファイル
```

---

## セットアップ

1. 必要なパッケージをインストール

```bash
pip install -r requirements.txt
```

2. データベース・キャッシュ用の`data/`フォルダが存在することを確認

---

## 実行方法

### Streamlitアプリの起動

```bash
# 推奨: プロジェクトルートから
python run_app.py
# または直接
streamlit run src/diary_app.py
```

### サンプルスクリプトの実行

```bash
python example_usage.py
```

---

## 基本的な使い方（Python API例）

```python
from src.diary_manager_sqlite import DiaryManagerSQLite

diary_manager = DiaryManagerSQLite("data/diary.db")
diary_manager.ensure_database()

# 1. 新規エントリ作成
entry = {
    'id': 'diary_2025_01_01',
    'created_at': '2025-01-01 10:00:00',
    'date': '2025-01-01',
    'text': '今日は新しい年の始まりです。',
    'question': '今日の気分はどうですか？',
    'user_id': 'user123',
    'topics': ['仕事', '家族'],
    'emotions': ['嬉しい', '緊張']
}
entry_id = diary_manager.add_diary_entry(entry)

# 2. 同じIDで内容をUPDATE
updated_entry = entry.copy()
updated_entry['emotions'] = ['嬉しい']
entry_id_2 = diary_manager.add_diary_entry(updated_entry)

# 3. フォローアップ質問・Q&A履歴の管理
followup_questions = ['今年の抱負は？']
diary_manager.add_followup_questions(entry_id, followup_questions)
qa_chain = [
    {'question': '健康目標は？', 'answer': '毎日運動', 'created_at': '2025-01-01 10:30:00'}
]
diary_manager.add_qa_chain(entry_id, qa_chain)

# 4. データ取得
all_data = diary_manager.get_all_diary_data()
```

---

## テストの実行

```bash
# すべてのテスト
pytest
# 特定のテスト
pytest tests/test_diary_manager_sqlite.py -v
```
---

##　フォルダ構成と.gitignore方針

- `.env`, `data/*.json` などの**個人情報や日記データはすべて `.gitignore` で管理**
- `data/example_usage.db` などの**共有用サンプルデータは例外指定で共有**


---

## 注意事項

- エントリIDは一意である必要があります
- 同じIDで追加すると既存データが上書きされます
- フォローアップ質問やQ&A履歴も専用メソッドで管理
- キャッシュファイル（例: emotion_cache.json）は`data/`配下に保存

---

## 今後の改善点

- バッチ処理・部分更新の最適化
- データバージョン管理
- トランザクションのさらなる強化

---

## 移行ガイド（旧構造→新構造）

- 重複チェックやDELETEベースの処理は不要
- エントリIDを明示的に指定し、同じIDでUPDATE
- フォローアップやQ&Aは専用メソッドで管理

---

## ライセンス

本プロジェクトはMITライセンスです。 