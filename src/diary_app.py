import streamlit as st
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from diary_manager_sqlite import DiaryManagerSQLite
from ai_analyzer import AIAnalyzer
from period_analyzer import PeriodAnalyzer
from ui_components import UIComponents
from utils.emotion_analyzer import (
    extract_emotions_with_date,
    classify_emotions_with_llm,
    to_dataframe,
    plot_emotion_trends,
    categories
)

# グローバル変数
ui = None

# ===== 認証機能 =====

def show_login_page():
    """ログインページを表示"""
    st.title("🔐 AI日記アプリ - ログイン")
    
    # タブでログインと新規登録を切り替え
    tab1, tab2 = st.tabs(["ログイン", "新規登録"])
    
    with tab1:
        st.subheader("ログイン")
        username = st.text_input("ユーザー名", key="login_username")
        password = st.text_input("パスワード", type="password", key="login_password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("ログイン", use_container_width=True):
                if username and password:
                    user_id = st.session_state.diary_manager.authenticate_user(username, password)
                    if user_id:
                        st.session_state.logged_in = True
                        st.session_state.user_id = user_id
                        st.session_state.username = username
                        st.success(f"{username} さん、ログイン成功！")
                        st.rerun()
                    else:
                        st.error("ユーザー名またはパスワードが違います")
                else:
                    st.warning("ユーザー名とパスワードを入力してください")
        
        with col2:
            if st.button("ゲストログイン", use_container_width=True):
                st.session_state.logged_in = True
                st.session_state.user_id = "guest"
                st.session_state.username = "ゲスト"
                st.success("ゲストとしてログインしました")
                st.rerun()
    
    with tab2:
        st.subheader("新規登録")
        new_username = st.text_input("ユーザー名", key="register_username")
        new_password = st.text_input("パスワード", type="password", key="register_password")
        confirm_password = st.text_input("パスワード（確認）", type="password", key="confirm_password")
        
        if st.button("登録", use_container_width=True):
            if new_username and new_password and confirm_password:
                if new_password == confirm_password:
                    if len(new_password) >= 6:
                        success = st.session_state.diary_manager.create_user(new_username, new_password)
                        if success:
                            st.success("ユーザー登録が完了しました！ログインしてください。")
                        else:
                            st.error("ユーザー名が既に使用されています")
                    else:
                        st.warning("パスワードは6文字以上で入力してください")
                else:
                    st.error("パスワードが一致しません")
            else:
                st.warning("すべての項目を入力してください")

def logout():
    """ログアウト処理"""
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = ""
    st.success("ログアウトしました")
    st.rerun()

# ===== 感情分類画面（ユーザー別） =====

def show_emotion_analysis():
    """感情分類ダッシュボードを表示（ユーザー別）"""
    st.title("📊 感情分類ダッシュボード")
    
    # 分類再実行オプション
    force_reload = st.checkbox("🔁 分類キャッシュを無視して再分類する", value=False)
    
    # 実行ボタン
    if st.button("▶ 分析スタート"):
        
        with st.spinner("感情データを抽出しています..."):
            # ユーザー別の感情データを抽出
            emotion_records = extract_emotions_from_sqlite_user(st.session_state.diary_manager, st.session_state.user_id)
            st.success(f"{len(emotion_records)} 件の感情タグを抽出しました")
        
        with st.spinner("LLMで分類しています..."):
            classification_result = classify_emotions_with_llm(
                emotion_records,
                categories=categories,
                ai_analyzer=st.session_state.ai_analyzer,
                use_cache=not force_reload
            )
            st.success(f"{len(classification_result)} つの内容の分類が完了しました")
        
        with st.spinner("データを整形中..."):
            df = to_dataframe(classification_result)
            st.dataframe(df, use_container_width=True)
        
        st.subheader("📈 感情カテゴリの週次変化")
        plot_emotion_trends(df)
        
    else:
        st.info("左のチェックを確認し、「分析スタート」ボタンを押してください。")

def extract_emotions_from_sqlite_user(diary_manager, user_id):
    """ユーザー別のSQLiteデータベースから感情データを抽出"""
    if user_id == "guest":
        # ゲストユーザーは自分の日記のみ（user_idが'guest'のもの）
        all_data = diary_manager.get_user_diary_data("guest")
    else:
        all_data = diary_manager.get_user_diary_data(user_id)
    
    emotion_records = []
    
    for entry in all_data:
        emotions = entry.get('emotions', [])
        created_at = entry.get('created_at', '')
        date = entry.get('date', '')
        
        for emotion in emotions:
            emotion_records.append({
                'emotion': emotion,
                'created_at': created_at,
                'date': date
            })
    
    return emotion_records

# ===== サイドバーメニュー（ユーザー別） =====

def show_sidebar_menu():
    """サイドバーメニューを表示（ユーザー別）"""
    st.sidebar.title("📖 AI日記アプリ")
    
    # ユーザー情報表示
    if st.session_state.logged_in:
        st.sidebar.markdown(f"**👤 {st.session_state.username} さん**")
        if st.sidebar.button("🚪 ログアウト", use_container_width=True):
            logout()
    
    st.sidebar.markdown("---")
    
    # メニュー項目
    menu_options = {
        "🏠 ホーム": "home",
        "✍️ 日記を書く": "write", 
        "📚 履歴一覧": "history",
        "📊 統計情報": "stats",
        "🎭 感情分析": "emotion",
        "📅 期間まとめ": "period_summary"
    }
    
    # メニューボタンを表示（現在のページをハイライト）
    for label, page in menu_options.items():
        is_current = st.session_state.page == page
        button_style = "primary" if is_current else "secondary"
        
        if st.sidebar.button(
            label, 
            key=f"menu_{page}", 
            use_container_width=True,
            type=button_style
        ):
            st.session_state.page = page
            st.rerun()
    
    # 統計情報（ユーザー別）
    if st.session_state.logged_in:
        st.sidebar.markdown("---")
        st.sidebar.markdown("**📈 統計情報**")
        
        if st.session_state.user_id == "guest":
            diary_data = st.session_state.diary_manager.get_user_diary_data("guest")
        else:
            diary_data = st.session_state.diary_manager.get_user_diary_data(st.session_state.user_id)
        
        st.sidebar.metric("総日記数", len(diary_data))
        
        if diary_data:
            # 最新の日記日付
            latest_date = max(entry.get('date', '') for entry in diary_data)
            st.sidebar.metric("最新日記", latest_date)
    
    # アプリ情報
    st.sidebar.markdown("---")
    st.sidebar.markdown("**📱 アプリ情報**")
    st.sidebar.markdown("AI日記アプリ v2.0")
    st.sidebar.markdown("ユーザー管理対応版")
    st.sidebar.markdown("左のメニューから各機能にアクセスできます")

# ===== メインアプリケーション =====

def main():
    """メインアプリケーション関数"""
    global ui
    
    # ===== セッション状態初期化 =====
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "page" not in st.session_state:
        st.session_state.page = "home"
    if "analysis" not in st.session_state:
        st.session_state.analysis = {}

    # ===== インスタンス生成 =====
    try:
        if 'diary_manager' not in st.session_state:
            st.session_state.diary_manager = DiaryManagerSQLite()
        if 'ai_analyzer' not in st.session_state:
            st.session_state.ai_analyzer = AIAnalyzer()
        if 'period_analyzer' not in st.session_state:
            st.session_state.period_analyzer = PeriodAnalyzer(st.session_state.ai_analyzer)
        if 'ui' not in st.session_state:
            st.session_state.ui = UIComponents(st.session_state.diary_manager, st.session_state.ai_analyzer, st.session_state.period_analyzer)
        
        ui = st.session_state.ui
    except Exception as e:
        st.error(f"アプリケーションの初期化に失敗しました: {e}")
        st.stop()

    # ===== メイン処理 =====
    # ログイン状態で表示を分岐
    if not st.session_state.logged_in:
        show_login_page()
    else:
        # サイドバーメニューを表示
        show_sidebar_menu()
        
        # ページ表示
        if st.session_state.page == "home":
            ui.show_home()
        elif st.session_state.page == "write":
            ui.show_write()
        elif st.session_state.page == "history":
            ui.show_history()
        elif st.session_state.page == "stats":
            ui.show_stats()
        elif st.session_state.page == "emotion":
            show_emotion_analysis()
        elif st.session_state.page == "period_summary":
            ui.show_period_summary()

if __name__ == "__main__":
    main()
