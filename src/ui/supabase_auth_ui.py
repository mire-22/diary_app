"""
Supabase認証用UIコンポーネント
"""

import streamlit as st
from typing import Optional, Dict, Any
from config.supabase_config import get_supabase_config

def render_auth_ui() -> Optional[Dict[str, Any]]:
    """
    Supabase認証UIを表示し、認証結果を返す
    
    Returns:
        Optional[Dict[str, Any]]: 認証成功時はユーザー情報、失敗時はNone
    """
    
    # セッション状態の初期化
    if 'auth_mode' not in st.session_state:
        st.session_state.auth_mode = 'signin'  # 'signin' or 'signup'
    
    if 'auth_error' not in st.session_state:
        st.session_state.auth_error = None
    
    # Supabase設定を取得
    try:
        supabase = get_supabase_config()
    except ValueError as e:
        st.error(f"Supabase設定エラー: {e}")
        st.info("環境変数 SUPABASE_URL と SUPABASE_ANON_KEY を設定してください")
        return None
    
    # 現在のユーザーを確認
    current_user = supabase.get_current_user()
    if current_user:
        return current_user
    
    # 認証UIの表示
    st.markdown("## 🔐 ログイン")
    
    # タブ切り替え
    tab1, tab2, tab3 = st.tabs(["📧 メールログイン", "📝 新規登録", "🔑 パスワードリセット"])
    
    with tab1:
        user = _render_signin_tab(supabase)
        if user:
            return user
    
    with tab2:
        user = _render_signup_tab(supabase)
        if user:
            return user
    
    with tab3:
        _render_password_reset_tab(supabase)
    
    return None

def _render_signin_tab(supabase) -> Optional[Dict[str, Any]]:
    """サインインタブを表示"""
    
    st.markdown("### メールアドレスでログイン")
    
    with st.form("signin_form"):
        email = st.text_input("メールアドレス", type="default")
        password = st.text_input("パスワード", type="password")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            submit_button = st.form_submit_button("ログイン", type="primary")
        
        with col2:
            google_button = st.form_submit_button("Googleでログイン")
        
        if submit_button and email and password:
            with st.spinner("ログイン中..."):
                result = supabase.sign_in_with_email(email, password)
                
                if result["success"]:
                    st.success("ログインに成功しました！")
                    st.rerun()
                else:
                    st.error(f"ログインに失敗しました: {result['error']}")
        
        elif google_button:
            with st.spinner("Google認証を開始中..."):
                result = supabase.sign_in_with_google()
                
                if result["success"]:
                    st.success("Google認証ページにリダイレクトします...")
                    st.markdown(f"[Googleでログイン]({result['url']})")
                else:
                    st.error(f"Google認証に失敗しました: {result['error']}")
    
    return None

def _render_signup_tab(supabase) -> Optional[Dict[str, Any]]:
    """サインアップタブを表示"""
    
    st.markdown("### 新規アカウント作成")
    
    with st.form("signup_form"):
        email = st.text_input("メールアドレス", key="signup_email", type="default")
        password = st.text_input("パスワード", key="signup_password", type="password")
        password_confirm = st.text_input("パスワード（確認）", key="signup_password_confirm", type="password")
        
        submit_button = st.form_submit_button("アカウント作成", type="primary")
        
        if submit_button:
            if not email or not password:
                st.error("メールアドレスとパスワードを入力してください")
            elif password != password_confirm:
                st.error("パスワードが一致しません")
            elif len(password) < 6:
                st.error("パスワードは6文字以上で入力してください")
            else:
                with st.spinner("アカウント作成中..."):
                    result = supabase.sign_up_with_email(email, password)
                    
                    if result["success"]:
                        st.success("アカウントが作成されました！確認メールをチェックしてください。")
                        st.info("メールの確認リンクをクリックしてからログインしてください。")
                    else:
                        st.error(f"アカウント作成に失敗しました: {result['error']}")
    
    return None

def _render_password_reset_tab(supabase):
    """パスワードリセットタブを表示"""
    
    st.markdown("### パスワードリセット")
    st.info("メールアドレスを入力すると、パスワードリセットリンクが送信されます。")
    
    with st.form("password_reset_form"):
        email = st.text_input("メールアドレス", key="reset_email", type="default")
        submit_button = st.form_submit_button("リセットリンクを送信", type="primary")
        
        if submit_button and email:
            with st.spinner("リセットリンクを送信中..."):
                result = supabase.reset_password(email)
                
                if result["success"]:
                    st.success("パスワードリセットリンクを送信しました！")
                    st.info("メールをチェックしてリンクをクリックしてください。")
                else:
                    st.error(f"リセットリンクの送信に失敗しました: {result['error']}")

def render_user_profile(user: Dict[str, Any]):
    """ユーザープロフィール表示"""
    
    st.markdown("## 👤 ユーザープロフィール")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.write(f"**メールアドレス:** {user.get('email', 'N/A')}")
        st.write(f"**ユーザーID:** {user.get('id', 'N/A')}")
        
        if user.get('email_confirmed_at'):
            st.success("✅ メールアドレス確認済み")
        else:
            st.warning("⚠️ メールアドレス未確認")
    
    with col2:
        if st.button("ログアウト", type="secondary"):
            supabase = get_supabase_config()
            result = supabase.sign_out()
            
            if result["success"]:
                st.success("ログアウトしました")
                st.rerun()
            else:
                st.error(f"ログアウトに失敗しました: {result['error']}")

def render_auth_status():
    """認証状態の表示"""
    
    try:
        supabase = get_supabase_config()
        current_user = supabase.get_current_user()
        
        if current_user:
            st.sidebar.success(f"✅ {current_user.get('email', 'ログイン中')}")
            
            if st.sidebar.button("ログアウト", key="sidebar_logout"):
                result = supabase.sign_out()
                if result["success"]:
                    st.rerun()
        else:
            st.sidebar.info("🔐 ログインしてください")
            
    except Exception as e:
        st.sidebar.error("⚠️ 認証エラー")
        st.sidebar.error(str(e)) 