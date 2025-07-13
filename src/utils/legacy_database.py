import streamlit as st
import datetime
import sqlite3
import os
import json

# データベースファイルのパス
DB_FILE = "diary.db"

# 初期状態の設定
if "page" not in st.session_state:
    st.session_state.page = "home"
if "diary" not in st.session_state:
    st.session_state.diary = ""
if "analysis" not in st.session_state:
    st.session_state.analysis = {}

# ------------------ データベース管理関数 ------------------

def init_database():
    """データベースを初期化"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS diary_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            text TEXT NOT NULL,
            topics TEXT,
            emotions TEXT,
            thoughts TEXT,
            goals TEXT,
            question TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def add_diary_entry(entry):
    """新しい日記エントリを追加"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO diary_entries (date, text, topics, emotions, thoughts, goals, question)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        entry['date'],
        entry['text'],
        json.dumps(entry['topics']),
        json.dumps(entry['emotions']),
        json.dumps(entry['thoughts']),
        json.dumps(entry['goals']),
        entry['question']
    ))
    
    conn.commit()
    conn.close()

def get_all_entries():
    """全ての日記エントリを取得"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM diary_entries ORDER BY created_at DESC')
    rows = cursor.fetchall()
    
    entries = []
    for row in rows:
        entries.append({
            'id': row[0],
            'date': row[1],
            'text': row[2],
            'topics': json.loads(row[3]) if row[3] else [],
            'emotions': json.loads(row[4]) if row[4] else [],
            'thoughts': json.loads(row[5]) if row[5] else [],
            'goals': json.loads(row[6]) if row[6] else [],
            'question': row[7],
            'created_at': row[8]
        })
    
    conn.close()
    return entries

# データベース初期化
init_database()

# ------------------ 画面定義 ------------------

def show_home():
    st.title("📝 AI日記アプリ")
    st.write("あなたの日記をAIが分析し、興味・感情・思考を構造化します。")

    st.markdown("### メニュー")
    if st.button("✍️ 今日の日記を書く"):
        st.session_state.page = "write"
        st.rerun()
    if st.button("📚 履歴を見る"):
        st.session_state.page = "history"
        st.rerun()

def show_write():
    st.title("✍️ 日記を書く")
    diary_input = st.text_area("今日の出来事や思ったことを自由に書いてください", height=200)

    if st.button("送信して分析する"):
        st.session_state.diary = diary_input

        # モック分析（APIで置き換え可能）
        analysis_result = {
            "date": str(datetime.date.today()),
            "text": diary_input,
            "topics": ["AI", "習慣化"],
            "emotions": ["前向き"],
            "thoughts": ["もっと記録したい"],
            "goals": ["毎日書きたい"],
            "question": "なぜAIに関心があると感じたのですか？"
        }

        # データベースに保存
        add_diary_entry(analysis_result)
        
        st.session_state.analysis = analysis_result
        st.session_state.page = "result"
        st.rerun()

    if st.button("← ホームに戻る"):
        st.session_state.page = "home"
        st.rerun()

def show_result():
    st.title("🔍 分析結果")
    a = st.session_state.analysis

    st.write(f"📅 **日付:** {a['date']}")
    st.write(f"📖 **日記:** {a['text']}")
    st.write(f"🧠 **トピック:** {', '.join(a['topics'])}")
    st.write(f"🎭 **感情:** {', '.join(a['emotions'])}")
    st.write(f"💭 **思考:** {', '.join(a['thoughts'])}")
    st.write(f"🎯 **目標:** {', '.join(a['goals'])}")
    st.write(f"🧩 **質問:** {a['question']}")

    st.text_input("💬 この質問についてどう思いましたか？（任意）")

    if st.button("📚 履歴を見る"):
        st.session_state.page = "history"
        st.rerun()
    if st.button("← ホームに戻る"):
        st.session_state.page = "home"
        st.rerun()

def show_history():
    st.title("📚 履歴一覧")

    entries = get_all_entries()
    
    if entries:
        for entry in entries:
            with st.expander(f"📅 {entry['date']} - {entry['text'][:50]}..."):
                st.write(f"**📖 日記:** {entry['text']}")
                st.write(f"**🧠 トピック:** {', '.join(entry['topics'])}")
                st.write(f"**🎭 感情:** {', '.join(entry['emotions'])}")
                st.write(f"**💭 思考:** {', '.join(entry['thoughts'])}")
                st.write(f"**🎯 目標:** {', '.join(entry['goals'])}")
                st.write(f"**🧩 質問:** {entry['question']}")
    else:
        st.info("履歴がまだありません。")

    if st.button("← ホームに戻る"):
        st.session_state.page = "home"
        st.rerun()

# ------------------ 表示処理 ------------------

if st.session_state.page == "home":
    show_home()
elif st.session_state.page == "write":
    show_write()
elif st.session_state.page == "result":
    show_result()
elif st.session_state.page == "history":
    show_history() 