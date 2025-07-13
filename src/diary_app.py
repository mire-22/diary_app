import streamlit as st
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
import os

# インスタンス生成
if 'diary_manager' not in st.session_state:
    st.session_state.diary_manager = DiaryManagerSQLite()
if 'ai_analyzer' not in st.session_state:
    st.session_state.ai_analyzer = AIAnalyzer()
if 'period_analyzer' not in st.session_state:
    st.session_state.period_analyzer = PeriodAnalyzer(st.session_state.ai_analyzer)
if 'ui' not in st.session_state:
    st.session_state.ui = UIComponents(st.session_state.diary_manager, st.session_state.ai_analyzer, st.session_state.period_analyzer)

# ページ状態初期化
if "page" not in st.session_state:
    st.session_state.page = "home"
if "analysis" not in st.session_state:
    st.session_state.analysis = {}

ui = st.session_state.ui

# ------------------ 感情分類画面 ------------------

def show_emotion_analysis():
    """感情分類ダッシュボードを表示"""
    st.title("📊 感情分類ダッシュボード")
    
    # 分類再実行オプション
    force_reload = st.checkbox("🔁 分類キャッシュを無視して再分類する", value=False)
    
    # 実行ボタン
    if st.button("▶ 分析スタート"):
        
        with st.spinner("感情データを抽出しています..."):
            # SQLiteデータベースから感情データを抽出
            emotion_records = extract_emotions_from_sqlite(st.session_state.diary_manager)
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

def extract_emotions_from_sqlite(diary_manager):
    """SQLiteデータベースから感情データを抽出"""
    all_data = diary_manager.get_all_diary_data()
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

# ------------------ サイドバーメニュー ------------------

def show_sidebar_menu():
    """サイドバーメニューを表示"""
    st.sidebar.title("📖 AI日記アプリ")
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
    
    # 統計情報
    st.sidebar.markdown("---")
    st.sidebar.markdown("**📈 統計情報**")
    diary_data = st.session_state.diary_manager.get_all_diary_data()
    st.sidebar.metric("総日記数", len(diary_data))
    
    if diary_data:
        # 最新の日記日付
        latest_date = max(entry.get('date', '') for entry in diary_data)
        st.sidebar.metric("最新日記", latest_date)
    
    # アプリ情報
    st.sidebar.markdown("---")
    st.sidebar.markdown("**📱 アプリ情報**")
    st.sidebar.markdown("AI日記アプリ v2.0")
    st.sidebar.markdown("SQLite対応版")
    st.sidebar.markdown("左のメニューから各機能にアクセスできます")

# ------------------ ページ表示 ------------------

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
