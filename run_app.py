#!/usr/bin/env python3
"""
AI日記アプリのエントリーポイント
プロジェクトルートから実行するためのファイル
"""

import sys
import os
import subprocess
import socket

def find_available_port(start_port=8501, max_attempts=10):
    """利用可能なポートを見つける"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None

def main():
    """アプリケーションを起動"""
    # 利用可能なポートを見つける
    port = find_available_port()
    if port is None:
        print("❌ 利用可能なポートが見つかりませんでした。")
        sys.exit(1)
    
    print("🚀 AI日記アプリを起動中...")
    print(f"📝 ブラウザで http://localhost:{port} にアクセスしてください")
    print("🛑 終了するには Ctrl+C を押してください")
    print("-" * 50)
    
    # srcフォルダをPythonパスに追加
    src_path = os.path.join(os.path.dirname(__file__), 'src')
    sys.path.insert(0, src_path)
    
    # diary_app.pyのパスを取得
    app_path = os.path.join(src_path, 'diary_app.py')
    
    # Streamlitコマンドを実行
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            app_path, f"--server.port={port}"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"アプリケーションの起動に失敗しました: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nアプリケーションを終了しました。")
        sys.exit(0)

if __name__ == "__main__":
    main() 