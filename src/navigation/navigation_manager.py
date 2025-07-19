"""
ナビゲーション管理機能を提供するクラス
"""

import streamlit as st
from typing import Dict, Any, List
from session.session_manager import SessionManager

class NavigationManager:
    """ナビゲーション管理機能を提供するクラス"""
    
    def __init__(self):
        self.menu_items = self._get_menu_items()
    
    def _get_menu_items(self) -> List[Dict[str, Any]]:
        """メニュー項目を定義"""
        return [
            {
                'id': 'home',
                'label': '🏠 ホーム',
                'icon': '🏠',
                'description': 'アプリの概要と最近の日記'
            },
            {
                'id': 'write',
                'label': '✍️ 日記を書く',
                'icon': '✍️',
                'description': '新しい日記を書いてAI分析'
            },
            {
                'id': 'history',
                'label': '📚 履歴一覧',
                'icon': '📚',
                'description': '過去の日記を確認・編集'
            },
            {
                'id': 'stats',
                'label': '📊 統計情報',
                'icon': '📊',
                'description': '感情・トピックの傾向分析'
            },
            {
                'id': 'period_summary',
                'label': '📈 期間まとめ',
                'icon': '📈',
                'description': '指定期間の分析まとめ'
            },
            {
                'id': 'emotion_analysis',
                'label': '🎭 感情分析',
                'icon': '🎭',
                'description': '感情の詳細分析とグラフ'
            }
        ]
    
    def show_sidebar_menu(self) -> str:
        """サイドバーメニューを表示"""
        st.sidebar.title("📝 AI日記アプリ")
        
        # ユーザー情報表示
        username = SessionManager.get_username()
        if username:
            st.sidebar.markdown(f"**👤 {username}**")
        
        st.sidebar.markdown("---")
        
        # メニュー項目を表示
        current_page = SessionManager.get_page()
        
        for item in self.menu_items:
            if st.sidebar.button(
                item['label'],
                key=f"menu_{item['id']}",
                use_container_width=True,
                type="primary" if current_page == item['id'] else "secondary"
            ):
                SessionManager.set_page(item['id'])
                st.rerun()
        
        st.sidebar.markdown("---")
        
        # 設定ボタン
        if st.sidebar.button("⚙️ 設定", use_container_width=True):
            SessionManager.set_page("settings")
            st.rerun()
        
        # ログアウトボタン
        if st.sidebar.button("🚪 ログアウト", use_container_width=True):
            SessionManager.logout()
            st.success("ログアウトしました")
            st.rerun()
        
        return current_page
    
    def get_current_page_info(self) -> Dict[str, Any]:
        """現在のページ情報を取得"""
        current_page = SessionManager.get_page()
        for item in self.menu_items:
            if item['id'] == current_page:
                return item
        return {
            'id': current_page,
            'label': current_page,
            'icon': '📄',
            'description': ''
        }
    
    def get_menu_items(self) -> List[Dict[str, Any]]:
        """メニュー項目一覧を取得"""
        return self.menu_items
    
    def is_valid_page(self, page: str) -> bool:
        """ページが有効かどうかを確認"""
        return any(item['id'] == page for item in self.menu_items) or page == "settings"
    
    def get_page_title(self, page: str) -> str:
        """ページタイトルを取得"""
        for item in self.menu_items:
            if item['id'] == page:
                return item['label']
        return page
    
    def get_page_description(self, page: str) -> str:
        """ページ説明を取得"""
        for item in self.menu_items:
            if item['id'] == page:
                return item['description']
        return "" 