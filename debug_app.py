#!/usr/bin/env python3
"""
デバッグ用の簡易版アプリ
問題を特定するための最小限のアプリケーション
"""

import streamlit as st
import os
import sys

# パス設定
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

def main():
    """デバッグ用メイン関数"""
    st.title("🔍 デバッグ用アプリ")
    
    # 基本的なStreamlit機能のテスト
    st.write("### 1. 基本的なStreamlit機能テスト")
    st.success("✅ Streamlitは正常に動作しています")
    
    # パス設定のテスト
    st.write("### 2. パス設定テスト")
    st.write(f"現在のディレクトリ: {os.getcwd()}")
    st.write(f"srcパス: {src_path}")
    st.write(f"srcパスが存在: {os.path.exists(src_path)}")
    
    # モジュールインポートテスト
    st.write("### 3. モジュールインポートテスト")
    try:
        from diary_manager_sqlite import DiaryManagerSQLite
        st.success("✅ DiaryManagerSQLite インポート成功")
    except Exception as e:
        st.error(f"❌ DiaryManagerSQLite インポート失敗: {e}")
    
    try:
        from ai_analyzer import AIAnalyzer
        st.success("✅ AIAnalyzer インポート成功")
    except Exception as e:
        st.error(f"❌ AIAnalyzer インポート失敗: {e}")
    
    try:
        from period_analyzer import PeriodAnalyzer
        st.success("✅ PeriodAnalyzer インポート成功")
    except Exception as e:
        st.error(f"❌ PeriodAnalyzer インポート失敗: {e}")
    
    try:
        from ui_components import UIComponents
        st.success("✅ UIComponents インポート成功")
    except Exception as e:
        st.error(f"❌ UIComponents インポート失敗: {e}")
    
    # インスタンス生成テスト
    st.write("### 4. インスタンス生成テスト")
    try:
        diary_manager = DiaryManagerSQLite()
        st.success("✅ DiaryManagerSQLite インスタンス生成成功")
    except Exception as e:
        st.error(f"❌ DiaryManagerSQLite インスタンス生成失敗: {e}")
    
    try:
        ai_analyzer = AIAnalyzer()
        st.success("✅ AIAnalyzer インスタンス生成成功")
    except Exception as e:
        st.error(f"❌ AIAnalyzer インスタンス生成失敗: {e}")
    
    # 環境変数テスト
    st.write("### 5. 環境変数テスト")
    try:
        gemini_key = st.secrets.get("GEMINI_API_KEY")
        if gemini_key:
            st.success("✅ GEMINI_API_KEY 設定済み")
        else:
            st.warning("⚠️ GEMINI_API_KEY 未設定")
    except Exception as e:
        st.error(f"❌ 環境変数取得失敗: {e}")
    
    # データベーステスト
    st.write("### 6. データベーステスト")
    try:
        if 'diary_manager' in locals():
            data = diary_manager.get_all_diary_data()
            st.success(f"✅ データベース接続成功 (データ数: {len(data)})")
    except Exception as e:
        st.error(f"❌ データベース接続失敗: {e}")
    
    # 簡単なUIテスト
    st.write("### 7. UIテスト")
    if st.button("テストボタン"):
        st.success("✅ ボタンクリック成功")
    
    user_input = st.text_input("テスト入力")
    if user_input:
        st.write(f"入力内容: {user_input}")

if __name__ == "__main__":
    main() 