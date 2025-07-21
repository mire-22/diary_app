import streamlit as st
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv

# 環境切り替え（local or cloud）
ENV = os.getenv("APP_ENV", "local")
if ENV == "local":
    load_dotenv()

# Supabase専用
from diary_manager_supabase import DiaryManagerSupabase as DiaryManager
from ui_components import UIComponents
from ai_analyzer import AIAnalyzer
from period_analyzer import PeriodAnalyzer
from ui.supabase_auth_ui import render_auth_ui, render_user_profile, render_auth_status
from utils.emotion_analyzer import (
    extract_emotions_with_date,
    classify_emotions_with_llm,
    to_dataframe,
    plot_emotion_trends,
    categories
)

ui = None

def show_login_page():
    """ログインページを表示（Supabase専用）"""
    user = render_auth_ui()
    if user:
        st.session_state.logged_in = True
        st.session_state.user_id = getattr(user, 'id', None)
        st.session_state.username = getattr(user, 'email', 'ユーザー')
        st.success(f"{st.session_state.username} さん、ログイン成功！")
        st.rerun()

def logout():
    """ログアウト処理（Supabase専用）"""
    from config.supabase_config import get_supabase_config
    supabase = get_supabase_config()
    result = supabase.sign_out()
    if result["success"]:
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.username = ""
        st.success("ログアウトしました")
        st.rerun()

# ===== 感情分類画面（ユーザー別） =====
def show_emotion_analysis():
    st.title("📊 感情分類ダッシュボード")
    force_reload = st.checkbox("🔁 分類キャッシュを無視して再分類する", value=False)
    if st.button("▶ 分析スタート"):
        with st.spinner("感情データを抽出しています..."):
            diary_data = st.session_state.diary_manager.get_diary_entries()
            emotion_records = extract_emotions_with_date(diary_data)
            st.success(f"{len(emotion_records)} 件の感情タグを抽出しました")
            # ここで感情分類やグラフ描画などを実装

# ===== サイドバーメニュー =====
def show_sidebar_menu():
    st.sidebar.title("📖 AI日記アプリ")
    render_auth_status()
    menu_options = [
        "🏠 ホーム",
        "✍️ 日記を書く",
        "📚 履歴一覧",
        "📊 統計情報",
        "🎭 感情分析",
        "📅 期間まとめ",
        "🔐 ログアウト"
    ]
    selected_menu = st.sidebar.selectbox("メニュー", menu_options, key="menu_select")
    if selected_menu == "🔐 ログアウト":
        logout()
    return selected_menu

def main():
    global ui
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
    try:
        if 'diary_manager' not in st.session_state:
            st.session_state.diary_manager = DiaryManager()
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
    if not st.session_state.logged_in:
        show_login_page()
    else:
        selected_menu = show_sidebar_menu()
        if selected_menu == "🏠 ホーム":
            ui.show_home()
        elif selected_menu == "✍️ 日記を書く":
            ui.show_write()
        elif selected_menu == "📚 履歴一覧":
            ui.show_history()
        elif selected_menu == "📊 統計情報":
            ui.show_stats()
        elif selected_menu == "🎭 感情分析":
            ui.show_emotion()
        elif selected_menu == "📅 期間まとめ":
            ui.show_period_summary()

if __name__ == "__main__":
    main()
