"""
アプリケーション全体で使用する定数
"""

# パスワード関連
MIN_PASSWORD_LENGTH = 6

# ユーザー関連
DEFAULT_USER_ID = "default_user"
GUEST_USER_ID = "guest_user"
GUEST_USERNAME = "ゲスト"

# データベース関連
DEFAULT_DB_PATH = "data/diary_normalized.db"

# アプリケーション情報
APP_NAME = "AI日記アプリ"
APP_VERSION = "v2.0"
APP_DESCRIPTION = "ユーザー管理対応版"

# エラーメッセージ
ERROR_MESSAGES = {
    "PASSWORD_TOO_SHORT": "パスワードは6文字以上で入力してください",
    "PASSWORD_MISMATCH": "パスワードが一致しません",
    "PASSWORD_SAME": "新しいパスワードは現在のパスワードと異なるものを入力してください",
    "USERNAME_EXISTS": "ユーザー名が既に使用されています",
    "INVALID_CREDENTIALS": "ユーザー名またはパスワードが違います",
    "MISSING_FIELDS": "すべての項目を入力してください",
    "GUEST_NO_SETTINGS": "ゲストユーザーは設定を変更できません"
}

# 成功メッセージ
SUCCESS_MESSAGES = {
    "LOGIN_SUCCESS": "さん、ログイン成功！",
    "GUEST_LOGIN": "ゲストとしてログインしました",
    "REGISTER_SUCCESS": "ユーザー登録が完了しました！ログインしてください。",
    "PASSWORD_CHANGED": "パスワードが正常に変更されました！",
    "LOGOUT_SUCCESS": "ログアウトしました",
    "ENTRY_SAVED": "記録を保存しました！",
    "ANSWER_SAVED": "回答を保存しました！",
    "REANALYZE_SUCCESS": "再分析しました！",
    "DATE_UPDATED": "日付を更新しました！",
    "ENTRY_DELETED": "削除しました"
}

# 情報メッセージ
INFO_MESSAGES = {
    "NO_DIARY": "まだ日記がありません。左のメニューから「日記を書く」を選択して、最初の日記を書いてみましょう！",
    "NO_HISTORY": "履歴がまだありません。",
    "NO_STATS": "統計データがありません。",
    "NO_ENTRIES_FOR_DATE": "の記録はまだありません。新しい記録を追加してみましょう！",
    "NO_QA": "まだ質問への回答がありません。",
    "PASSWORD_CHANGE_INFO": "次回ログイン時から新しいパスワードが有効になります。",
    "ANALYSIS_START": "左のチェックを確認し、「分析スタート」ボタンを押してください。"
}

# 警告メッセージ
WARNING_MESSAGES = {
    "ENTER_CREDENTIALS": "ユーザー名とパスワードを入力してください",
    "ENTER_ALL_FIELDS": "すべての項目を入力してください",
    "ENTER_DIARY_CONTENT": "日記の内容を入力してください。",
    "ENTER_ANSWER": "回答を入力してください。",
    "ENTER_PROMPT": "カスタム分析を選択した場合は、プロンプトを入力してください。",
    "DANGEROUS_OPERATIONS": "以下の操作は取り消しできません。十分注意して実行してください。"
} 