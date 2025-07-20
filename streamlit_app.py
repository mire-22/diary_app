#!/usr/bin/env python3
"""
Streamlit Cloud用エントリーポイント
"""

import sys
import os

# srcフォルダをPythonパスに追加
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

# メインアプリケーションをインポートして実行
from diary_app import main

if __name__ == "__main__":
    main() 