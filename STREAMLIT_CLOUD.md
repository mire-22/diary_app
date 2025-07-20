# Streamlit Cloud デプロイガイド

## デプロイ手順

### 1. GitHubリポジトリの準備
- このリポジトリをGitHubにプッシュ
- 以下のファイルが含まれていることを確認：
  - `streamlit_app.py` (エントリーポイント)
  - `requirements.txt`
  - `.streamlit/config.toml`
  - `src/` フォルダ内のすべてのファイル

### 2. Streamlit Cloudでの設定

#### 2.1 アプリケーション設定
- **Main file path**: `streamlit_app.py`
- **Python version**: 3.9.18を選択（runtime.txtで指定）

#### 2.2 環境変数の設定
Streamlit Cloudの管理画面で以下の環境変数を設定：

```
GEMINI_API_KEY=your_gemini_api_key_here
```

#### 2.3 シークレットの設定
`.streamlit/secrets.toml`の内容をStreamlit Cloudのシークレット管理で設定：

```toml
GEMINI_API_KEY = "your_gemini_api_key_here"
```

### 3. デプロイ後の確認

#### 3.1 正常起動の確認
- アプリケーションが正常に起動することを確認
- ログイン画面が表示されることを確認

#### 3.2 機能テスト
- ユーザー登録機能
- 日記記録機能
- AI分析機能

## トラブルシューティング

### 503エラーの解決

#### 1. エントリーポイントの確認
- `streamlit_app.py`が正しく設定されているか確認
- ファイルパスが正しいか確認

#### 2. 依存関係の確認
- `requirements.txt`のバージョンが固定されているか確認
- 互換性のないパッケージがないか確認
- `runtime.txt`でPythonバージョンを指定しているか確認

#### 3. 環境変数の確認
- `GEMINI_API_KEY`が正しく設定されているか確認
- APIキーが有効か確認

#### 4. ログの確認
- Streamlit Cloudのログを確認
- エラーメッセージを確認

### よくある問題

#### 1. インポートエラー
```
ModuleNotFoundError: No module named 'src'
```
**解決方法**: `streamlit_app.py`でパス設定が正しく行われているか確認

#### 2. APIキーエラー
```
google.generativeai.types.BlockedPromptException
```
**解決方法**: `GEMINI_API_KEY`が正しく設定されているか確認

#### 3. データベースエラー
```
sqlite3.OperationalError: no such table
```
**解決方法**: データベース初期化が正常に動作しているか確認

## パフォーマンス最適化

### 1. キャッシュの活用
- Streamlitの`@st.cache_data`を使用
- 重い処理をキャッシュ

### 2. 非同期処理
- 長時間の処理は非同期で実行
- ユーザー体験を向上

### 3. エラーハンドリング
- 適切なエラーメッセージを表示
- クラッシュを防ぐ

## セキュリティ

### 1. APIキーの管理
- 環境変数で管理
- リポジトリにコミットしない

### 2. ユーザー認証
- パスワードのハッシュ化
- セッション管理

### 3. データ保護
- ユーザーデータの分離
- プライバシー保護

## 更新手順

### 1. コードの更新
```bash
git add .
git commit -m "Update for Streamlit Cloud"
git push origin main
```

### 2. Streamlit Cloudでの再デプロイ
- 自動的に再デプロイされる
- 手動で再デプロイも可能

### 3. 動作確認
- 新機能のテスト
- 既存機能の確認 