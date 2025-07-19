"""
セッション状態管理機能を提供するクラス
"""

import streamlit as st
from typing import Optional, Dict, Any
from constants import GUEST_USER_ID, GUEST_USERNAME

class SessionManager:
    """Streamlitセッション状態を管理するクラス"""
    
    @staticmethod
    def initialize_session() -> None:
        """セッション状態を初期化"""
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
    
    @staticmethod
    def login_user(user_id: str, username: str) -> None:
        """ユーザーログイン"""
        st.session_state.logged_in = True
        st.session_state.user_id = user_id
        st.session_state.username = username
    
    @staticmethod
    def login_guest() -> None:
        """ゲストログイン"""
        st.session_state.logged_in = True
        st.session_state.user_id = GUEST_USER_ID
        st.session_state.username = GUEST_USERNAME
    
    @staticmethod
    def logout() -> None:
        """ログアウト"""
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.username = ""
        st.session_state.page = "home"
        st.session_state.analysis = {}
    
    @staticmethod
    def is_logged_in() -> bool:
        """ログイン状態を確認"""
        return st.session_state.get('logged_in', False)
    
    @staticmethod
    def get_user_id() -> Optional[str]:
        """ユーザーIDを取得"""
        return st.session_state.get('user_id')
    
    @staticmethod
    def get_username() -> str:
        """ユーザー名を取得"""
        return st.session_state.get('username', '')
    
    @staticmethod
    def is_guest() -> bool:
        """ゲストユーザーかどうかを確認"""
        return st.session_state.get('user_id') == GUEST_USER_ID
    
    @staticmethod
    def set_page(page: str) -> None:
        """ページを設定"""
        st.session_state.page = page
    
    @staticmethod
    def get_page() -> str:
        """現在のページを取得"""
        return st.session_state.get('page', 'home')
    
    @staticmethod
    def set_analysis(analysis: Dict[str, Any]) -> None:
        """分析結果を設定"""
        st.session_state.analysis = analysis
    
    @staticmethod
    def get_analysis() -> Dict[str, Any]:
        """分析結果を取得"""
        return st.session_state.get('analysis', {})
    
    @staticmethod
    def clear_analysis() -> None:
        """分析結果をクリア"""
        st.session_state.analysis = {}
    
    @staticmethod
    def get_session_info() -> Dict[str, Any]:
        """セッション情報を取得"""
        return {
            'logged_in': st.session_state.get('logged_in', False),
            'user_id': st.session_state.get('user_id'),
            'username': st.session_state.get('username', ''),
            'page': st.session_state.get('page', 'home'),
            'is_guest': st.session_state.get('user_id') == GUEST_USER_ID
        } 