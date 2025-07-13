#!/usr/bin/env python3
"""
AI日記アプリのエントリーポイント
プロジェクトルートから実行するためのファイル
"""

import sys
import os

# srcフォルダをPythonパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# diary_appをインポートして実行
if __name__ == "__main__":
    import streamlit.web.cli as stcli
    import sys
    
    sys.argv = ["streamlit", "run", "src/diary_app.py", "--server.port=8501"]
    sys.exit(stcli.main()) 