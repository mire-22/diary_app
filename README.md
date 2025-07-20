# AI日記アプリ v2.0

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📝 概要

AI日記アプリは、日記データをAIで分析し、感情・トピック・思考・目標を構造化して管理できるWebアプリケーションです。ユーザー認証機能とセキュアなデータ管理により、個人の日記を安全に記録・分析できます。

### ✨ 主な機能

- **🤖 AI分析**: Google Gemini APIを使用した高度な日記分析
- **👤 ユーザー認証**: セキュアなパスワード認証とゲストログイン
- **📊 感情分析**: 感情の傾向分析とグラフ表示
- **📈 統計情報**: トピック・感情の統計と時系列分析
- **📅 期間まとめ**: KPT・YWT・カスタム分析による期間振り返り
- **💬 対話形式**: チャット形式での日記記録と深掘り質問
- **⚙️ 設定管理**: パスワード変更とデータ管理機能

---

## 🏗️ アーキテクチャ

### 設計原則

- **単一責任原則（SRP）**: 各クラスが明確な責任を持つ
- **DRY原則**: コード重複の排除と汎用メソッドの活用
- **セキュリティ**: パスワードハッシュ化とユーザー分離
- **保守性**: モジュラー設計とテスタブルな構造

### ディレクトリ構成

```
latest_suika/
├── data/                    # データベース・キャッシュ
│   ├── diary_normalized.db  # メインデータベース
│   └── example_usage.db     # サンプルデータ
├── src/                     # アプリケーション本体
│   ├── diary_app.py         # Streamlitアプリエントリーポイント
│   ├── diary_manager_sqlite.py  # データベース管理
│   ├── ai_analyzer.py       # AI分析機能
│   ├── period_analyzer.py   # 期間分析機能
│   ├── ui_components.py     # UIコンポーネント
│   ├── constants.py         # 定数管理
│   ├── auth/                # 認証機能
│   │   └── user_manager.py  # ユーザー認証・認可
│   ├── session/             # セッション管理
│   │   └── session_manager.py  # セッション状態管理
│   ├── navigation/          # ナビゲーション
│   │   └── navigation_manager.py  # ナビゲーション制御
│   ├── services/            # ビジネスロジック
│   │   └── diary_service.py # 日記関連サービス
│   ├── config/              # 設定管理
│   │   └── app_config.py    # アプリケーション設定
│   ├── utils/               # ユーティリティ
│   │   ├── validators.py    # バリデーション機能
│   │   ├── config_manager.py # 設定管理
│   │   ├── emotion_analyzer.py # 感情分析
│   │   ├── prompt_manager.py # プロンプト管理
│   │   └── tag_analyzer.py  # タグ分析
│   └── prompts/             # プロンプトテンプレート
│       ├── analyze_diary_prompt.txt
│       ├── kpt_analysis_prompt.txt
│       └── ywt_analysis_prompt.txt
├── tests/                   # テストコード
│   ├── test_diary_manager_sqlite.py
│   ├── test_period_summary.py
│   └── ...
├── run_app.py               # アプリケーション起動スクリプト
├── requirements.txt         # 依存パッケージ
├── pytest.ini              # テスト設定
└── README.md               # このファイル
```

---

## 🚀 セットアップ

### 1. 環境要件

- Python 3.8以上
- Streamlit 1.28以上
- SQLite3

### 2. インストール

```bash
# リポジトリをクローン
git clone https://github.com/mire-22/diary_app.git
cd diary_app

# 仮想環境を作成（推奨）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存パッケージをインストール
pip install -r requirements.txt
```

### 3. 環境変数の設定

`.env`ファイルを作成して以下の設定を追加：

```env
# AI設定
GEMINI_API_KEY=your_gemini_api_key_here

# アプリケーション設定
DEBUG=False
DB_PATH=data/diary_normalized.db

# セキュリティ設定
PASSWORD_MIN_LENGTH=6
SESSION_TIMEOUT=3600
```

### 4. データベースの初期化

```bash
# アプリケーションを一度起動すると自動的にデータベースが作成されます
python run_app.py
```

---

## 🎯 使用方法

### アプリケーションの起動

```bash
# 推奨方法
python run_app.py

# または直接Streamlitで起動
streamlit run src/diary_app.py
```

### 基本的な使い方

1. **ログイン**
   - 新規ユーザー登録または既存ユーザーログイン
   - ゲストログインも可能

2. **日記を書く**
   - 日付を選択して日記を入力
   - AIが自動で分析を実行
   - 感情・トピック・思考・目標を抽出

3. **対話形式の記録**
   - 深掘り質問に回答
   - Q&Aチェーンで内省を深める

4. **分析結果の確認**
   - 統計情報で傾向を把握
   - 感情分析でグラフ表示
   - 期間まとめで振り返り

---

## 🔧 開発者向け情報

### アーキテクチャの詳細

#### レイヤー構造

```
┌─────────────────────────────────────┐
│           Presentation Layer        │
│         (Streamlit UI)              │
├─────────────────────────────────────┤
│           Business Layer            │
│         (Services)                  │
├─────────────────────────────────────┤
│           Data Access Layer         │
│         (Managers)                  │
├─────────────────────────────────────┤
│           Infrastructure Layer      │
│         (Database, AI APIs)         │
└─────────────────────────────────────┘
```

#### 主要クラスの責任

| クラス | 責任 | 説明 |
|--------|------|------|
| `UserManager` | 認証・認可 | ユーザー登録・ログイン・パスワード管理 |
| `SessionManager` | セッション管理 | Streamlitセッション状態の管理 |
| `NavigationManager` | ナビゲーション | ページ遷移とメニュー管理 |
| `DiaryService` | ビジネスロジック | 日記関連のビジネスルール |
| `DiaryManagerSQLite` | データアクセス | SQLiteデータベース操作 |
| `AIAnalyzer` | AI分析 | Gemini API連携と分析実行 |

### テストの実行

```bash
# すべてのテストを実行
pytest

# 特定のテストファイルを実行
pytest tests/test_diary_manager_sqlite.py -v

# カバレッジ付きでテスト実行
pytest --cov=src tests/
```

### コード品質チェック

```bash
# リンター実行
flake8 src/
black src/
isort src/

# 型チェック
mypy src/
```

---

## 🔒 セキュリティ

### 実装されているセキュリティ機能

- **パスワードハッシュ化**: PBKDF2-SHA256を使用
- **ユーザー分離**: 各ユーザーのデータは完全に分離
- **セッション管理**: セキュアなセッション状態管理
- **入力バリデーション**: 全入力に対する適切なバリデーション
- **SQLインジェクション対策**: パラメータ化クエリの使用

### セキュリティベストプラクティス

- 環境変数での機密情報管理
- 最小権限の原則
- 定期的なセキュリティアップデート
- ログ監視と監査

---

## 📊 機能詳細

### AI分析機能

- **感情分析**: 8つの基本感情カテゴリでの分類
- **トピック抽出**: 日記内容から主要トピックを自動抽出
- **思考分析**: 深層的な思考パターンの分析
- **目標設定**: 日記から目標を自動抽出・提案

### 統計・分析機能

- **時系列分析**: 感情・トピックの変化をグラフ表示
- **傾向分析**: 週次・月次の統計情報
- **KPT分析**: Keep-Problem-Try形式での振り返り
- **YWT分析**: やった-わかった-次にやること形式での振り返り

### データ管理機能

- **バックアップ**: 自動データベースバックアップ
- **エクスポート**: 期間指定でのデータエクスポート
- **検索・フィルタ**: 日付・キーワードでの検索機能
- **データ可視化**: 各種グラフ・チャート表示

---

## 🐛 トラブルシューティング

### よくある問題

#### 1. Gemini APIキーエラー
```
解決方法: .envファイルにGEMINI_API_KEYを正しく設定
```

#### 2. データベースエラー
```
解決方法: data/フォルダの権限を確認し、アプリを再起動
```

#### 3. ポート競合
```
解決方法: 別のポートで起動
streamlit run src/diary_app.py --server.port 8502
```

### ログの確認

```bash
# Streamlitログの確認
streamlit run src/diary_app.py --logger.level debug
```

---

## 🤝 コントリビューション

### 開発環境のセットアップ

1. フォークしてリポジトリをクローン
2. 仮想環境を作成
3. 依存パッケージをインストール
4. テストを実行して環境を確認

### コーディング規約

- PEP 8に準拠
- 型ヒントの使用
- ドキュメント文字列の記述
- 単体テストの作成

### プルリクエスト

1. 機能ブランチを作成
2. 変更を実装
3. テストを追加・実行
4. プルリクエストを作成

---

## 📈 今後の開発予定

### v2.1 予定機能

- [ ] データエクスポート機能の強化
- [ ] モバイル対応の改善
- [ ] 複数言語対応
- [ ] テーマカスタマイズ機能

### v2.2 予定機能

- [ ] 音声入力機能
- [ ] 画像分析機能
- [ ] ソーシャル機能
- [ ] API提供

---

## 📄 ライセンス

このプロジェクトは [MIT License](LICENSE) の下で公開されています。

---

## 🙏 謝辞

- [Streamlit](https://streamlit.io/) - Webアプリケーションフレームワーク
- [Google Gemini](https://ai.google.dev/) - AI分析API
- [SQLite](https://www.sqlite.org/) - データベースエンジン

---

## 📞 サポート

問題や質問がある場合は、[Issues](https://github.com/mire-22/diary_app/issues) でお知らせください。

**Happy Diary Writing! 📝✨** 