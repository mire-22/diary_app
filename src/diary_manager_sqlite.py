import sqlite3
import json
import uuid
import datetime
import hashlib
import os
from typing import Any, Optional

class DiaryManagerSQLite:
    """SQLite対応の日記データ管理クラス"""
    
    def __init__(self, db_path: str = "data/diary_normalized.db"):
        # Streamlit Cloud対応: 絶対パスを使用
        if not os.path.isabs(db_path):
            import tempfile
            # Streamlit Cloudでは一時ディレクトリを使用
            if os.environ.get('STREAMLIT_SERVER_RUN_ON_SAVE', ''):
                # Streamlit Cloud環境
                self.db_path = os.path.join(tempfile.gettempdir(), "diary_normalized.db")
            else:
                # ローカル環境
                self.db_path = db_path
        else:
            self.db_path = db_path
        
        self.ensure_database()
    
    def ensure_database(self) -> None:
        """データベースが存在しない場合は作成"""
        import os
        
        # ディレクトリが存在しない場合は作成（絶対パスの場合のみ）
        if not os.path.isabs(self.db_path):
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
        except Exception as e:
            print(f"データベース接続エラー: {e}")
            # フォールバック: メモリ内データベースを使用
            import tempfile
            self.db_path = os.path.join(tempfile.gettempdir(), "diary_normalized.db")
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
        
        try:
            # メインテーブルを作成
            cur.execute('''
                CREATE TABLE IF NOT EXISTS diary_entries (
                    id TEXT PRIMARY KEY,
                    original_id TEXT,
                    created_at TEXT,
                    date TEXT,
                    text TEXT,
                    question TEXT,
                    user_id TEXT DEFAULT 'default_user'
                )
            ''')
            
            # 関連テーブルを作成
            cur.execute('''
                CREATE TABLE IF NOT EXISTS topics (
                    id TEXT PRIMARY KEY,
                    diary_entry_id TEXT,
                    topic TEXT,
                    FOREIGN KEY (diary_entry_id) REFERENCES diary_entries (id)
                )
            ''')
            
            cur.execute('''
                CREATE TABLE IF NOT EXISTS emotions (
                    id TEXT PRIMARY KEY,
                    diary_entry_id TEXT,
                    emotion TEXT,
                    FOREIGN KEY (diary_entry_id) REFERENCES diary_entries (id)
                )
            ''')
            
            cur.execute('''
                CREATE TABLE IF NOT EXISTS thoughts (
                    id TEXT PRIMARY KEY,
                    diary_entry_id TEXT,
                    thought TEXT,
                    FOREIGN KEY (diary_entry_id) REFERENCES diary_entries (id)
                )
            ''')
            
            cur.execute('''
                CREATE TABLE IF NOT EXISTS goals (
                    id TEXT PRIMARY KEY,
                    diary_entry_id TEXT,
                    goal TEXT,
                    FOREIGN KEY (diary_entry_id) REFERENCES diary_entries (id)
                )
            ''')
            
            cur.execute('''
                CREATE TABLE IF NOT EXISTS followup_questions (
                    id TEXT PRIMARY KEY,
                    diary_entry_id TEXT,
                    question TEXT,
                    order_index INTEGER,
                    FOREIGN KEY (diary_entry_id) REFERENCES diary_entries (id)
                )
            ''')
            
            cur.execute('''
                CREATE TABLE IF NOT EXISTS qa_chain (
                    id TEXT PRIMARY KEY,
                    diary_entry_id TEXT,
                    question TEXT,
                    answer TEXT,
                    created_at TEXT,
                    order_index INTEGER,
                    FOREIGN KEY (diary_entry_id) REFERENCES diary_entries (id)
                )
            ''')
            
            # ユーザー管理テーブルを作成
            cur.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    last_login TEXT
                )
            ''')
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def add_diary_entry(self, entry: dict[str, Any]) -> str:
        """新しい日記エントリを追加（重複しない構造）"""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            # エントリIDを決定（original_idがあれば使用、なければ生成）
            entry_id = entry.get('id') or str(uuid.uuid4())
            
            # メインエントリをUPSERT（INSERT OR UPDATE）
            cur.execute('''
                INSERT OR REPLACE INTO diary_entries (
                    id, original_id, created_at, date, text, question, user_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                entry_id,
                entry.get('id', ''),
                entry.get('created_at', ''),
                entry.get('date', ''),
                entry.get('text', ''),
                entry.get('question', ''),
                entry.get('user_id', 'default_user')
            ))
            
            # 関連データを挿入（既存データは削除して再挿入）
            self._upsert_related_data(cur, entry_id, entry)
            
            conn.commit()
            return entry_id
            
        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
            raise e
        finally:
            if 'conn' in locals():
                conn.close()
    
    def add_diary_entries_batch(self, entries: list[dict[str, Any]]) -> list[str]:
        """複数の日記エントリを一括追加（重複しない構造）"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        added_ids = []
        
        try:
            for entry in entries:
                # エントリIDを決定（original_idがあれば使用、なければ生成）
                entry_id = entry.get('id') or str(uuid.uuid4())
                
                # メインエントリをUPSERT（INSERT OR UPDATE）
                cur.execute('''
                    INSERT OR REPLACE INTO diary_entries (
                        id, original_id, created_at, date, text, question, user_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    entry_id,
                    entry.get('id', ''),
                    entry.get('created_at', ''),
                    entry.get('date', ''),
                    entry.get('text', ''),
                    entry.get('question', ''),
                    entry.get('user_id', 'default_user')
                ))
                
                # 関連データを挿入（既存データは削除して再挿入）
                self._upsert_related_data(cur, entry_id, entry)
                
                added_ids.append(entry_id)
            
            conn.commit()
            return added_ids
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _upsert_related_data(self, cur: sqlite3.Cursor, diary_id: str, entry: dict[str, Any]) -> None:
        """関連データをUPSERT（既存データを更新または追加）"""
        
        # トピックを更新または追加
        topics = entry.get('topics', [])
        self._upsert_topics(cur, diary_id, topics)
        
        # 感情を更新または追加
        emotions = entry.get('emotions', [])
        self._upsert_emotions(cur, diary_id, emotions)
        
        # 思考を更新または追加
        thoughts = entry.get('thoughts', [])
        self._upsert_thoughts(cur, diary_id, thoughts)
        
        # 目標を更新または追加
        goals = entry.get('goals', [])
        self._upsert_goals(cur, diary_id, goals)
        
        # 追加質問を更新または追加
        followup_questions = entry.get('followup_questions', [])
        self._upsert_followup_questions(cur, diary_id, followup_questions)
        
        # Q&A履歴を更新または追加
        qa_chain = entry.get('qa_chain', [])
        self._upsert_qa_chain(cur, diary_id, qa_chain)
    
    def _upsert_topics(self, cur: sqlite3.Cursor, diary_id: str, topics: list[str]) -> None:
        """トピックを更新または追加"""
        # 既存のトピックを取得
        cur.execute('SELECT id, topic FROM topics WHERE diary_entry_id = ? ORDER BY topic', (diary_id,))
        existing_topics = cur.fetchall()
        
        # 新しいトピックを処理
        for i, topic in enumerate(topics):
            if i < len(existing_topics):
                # 既存のレコードを更新
                cur.execute('''
                    UPDATE topics SET topic = ? WHERE id = ?
                ''', (topic, existing_topics[i][0]))
            else:
                # 新しいレコードを追加
                topic_id = str(uuid.uuid4())
                cur.execute('''
                    INSERT INTO topics (id, diary_entry_id, topic)
                    VALUES (?, ?, ?)
                ''', (topic_id, diary_id, topic))
        
        # 余分な既存レコードを削除（新しいリストより多い場合）
        if len(existing_topics) > len(topics):
            for i in range(len(topics), len(existing_topics)):
                cur.execute('DELETE FROM topics WHERE id = ?', (existing_topics[i][0],))
    
    def _upsert_emotions(self, cur: sqlite3.Cursor, diary_id: str, emotions: list[str]) -> None:
        """感情を更新または追加"""
        # 既存の感情を取得
        cur.execute('SELECT id, emotion FROM emotions WHERE diary_entry_id = ? ORDER BY emotion', (diary_id,))
        existing_emotions = cur.fetchall()
        
        # 新しい感情を処理
        for i, emotion in enumerate(emotions):
            if i < len(existing_emotions):
                # 既存のレコードを更新
                cur.execute('''
                    UPDATE emotions SET emotion = ? WHERE id = ?
                ''', (emotion, existing_emotions[i][0]))
            else:
                # 新しいレコードを追加
                emotion_id = str(uuid.uuid4())
                cur.execute('''
                    INSERT INTO emotions (id, diary_entry_id, emotion)
                    VALUES (?, ?, ?)
                ''', (emotion_id, diary_id, emotion))
        
        # 余分な既存レコードを削除（新しいリストより多い場合）
        if len(existing_emotions) > len(emotions):
            for i in range(len(emotions), len(existing_emotions)):
                cur.execute('DELETE FROM emotions WHERE id = ?', (existing_emotions[i][0],))
    
    def _upsert_thoughts(self, cur: sqlite3.Cursor, diary_id: str, thoughts: list[str]) -> None:
        """思考を更新または追加"""
        # 既存の思考を取得
        cur.execute('SELECT id, thought FROM thoughts WHERE diary_entry_id = ? ORDER BY thought', (diary_id,))
        existing_thoughts = cur.fetchall()
        
        # 新しい思考を処理
        for i, thought in enumerate(thoughts):
            if i < len(existing_thoughts):
                # 既存のレコードを更新
                cur.execute('''
                    UPDATE thoughts SET thought = ? WHERE id = ?
                ''', (thought, existing_thoughts[i][0]))
            else:
                # 新しいレコードを追加
                thought_id = str(uuid.uuid4())
                cur.execute('''
                    INSERT INTO thoughts (id, diary_entry_id, thought)
                    VALUES (?, ?, ?)
                ''', (thought_id, diary_id, thought))
        
        # 余分な既存レコードを削除（新しいリストより多い場合）
        if len(existing_thoughts) > len(thoughts):
            for i in range(len(thoughts), len(existing_thoughts)):
                cur.execute('DELETE FROM thoughts WHERE id = ?', (existing_thoughts[i][0],))
    
    def _upsert_goals(self, cur: sqlite3.Cursor, diary_id: str, goals: list[str]) -> None:
        """目標を更新または追加"""
        # 既存の目標を取得
        cur.execute('SELECT id, goal FROM goals WHERE diary_entry_id = ? ORDER BY goal', (diary_id,))
        existing_goals = cur.fetchall()
        
        # 新しい目標を処理
        for i, goal in enumerate(goals):
            if i < len(existing_goals):
                # 既存のレコードを更新
                cur.execute('''
                    UPDATE goals SET goal = ? WHERE id = ?
                ''', (goal, existing_goals[i][0]))
            else:
                # 新しいレコードを追加
                goal_id = str(uuid.uuid4())
                cur.execute('''
                    INSERT INTO goals (id, diary_entry_id, goal)
                    VALUES (?, ?, ?)
                ''', (goal_id, diary_id, goal))
        
        # 余分な既存レコードを削除（新しいリストより多い場合）
        if len(existing_goals) > len(goals):
            for i in range(len(goals), len(existing_goals)):
                cur.execute('DELETE FROM goals WHERE id = ?', (existing_goals[i][0],))
    
    def _upsert_followup_questions(self, cur: sqlite3.Cursor, diary_id: str, followup_questions: list[str]) -> None:
        """フォローアップ質問を更新または追加"""
        # 既存のフォローアップ質問を取得
        cur.execute('SELECT id, question, order_index FROM followup_questions WHERE diary_entry_id = ? ORDER BY order_index', (diary_id,))
        existing_questions = cur.fetchall()
        
        # 新しいフォローアップ質問を処理
        for i, question in enumerate(followup_questions):
            if i < len(existing_questions):
                # 既存のレコードを更新
                cur.execute('''
                    UPDATE followup_questions SET question = ? WHERE id = ?
                ''', (question, existing_questions[i][0]))
            else:
                # 新しいレコードを追加
                question_id = str(uuid.uuid4())
                cur.execute('''
                    INSERT INTO followup_questions (id, diary_entry_id, question, order_index)
                    VALUES (?, ?, ?, ?)
                ''', (question_id, diary_id, question, i))
        
        # 余分な既存レコードを削除（新しいリストより多い場合）
        if len(existing_questions) > len(followup_questions):
            for i in range(len(followup_questions), len(existing_questions)):
                cur.execute('DELETE FROM followup_questions WHERE id = ?', (existing_questions[i][0],))
    
    def _upsert_qa_chain(self, cur: sqlite3.Cursor, diary_id: str, qa_chain: list[dict[str, Any]]) -> None:
        """Q&A履歴を更新または追加"""
        # 既存のQ&A履歴を取得
        cur.execute('''
            SELECT id, question, answer, created_at, order_index
            FROM qa_chain 
            WHERE diary_entry_id = ? 
            ORDER BY order_index
        ''', (diary_id,))
        existing_qa_chain = cur.fetchall()
        
        # 新しいQ&A履歴を処理
        for i, qa in enumerate(qa_chain):
            if i < len(existing_qa_chain):
                # 既存のレコードを更新
                cur.execute('''
                    UPDATE qa_chain 
                    SET question = ?, answer = ?, created_at = ?
                    WHERE id = ?
                ''', (qa.get('question', ''), qa.get('answer', ''), qa.get('created_at', ''), existing_qa_chain[i][0]))
            else:
                # 新しいレコードを追加
                qa_id = str(uuid.uuid4())
                cur.execute('''
                    INSERT INTO qa_chain (id, diary_entry_id, question, answer, created_at, order_index)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (qa_id, diary_id, qa.get('question', ''), qa.get('answer', ''), qa.get('created_at', ''), i))
        
        # 余分な既存レコードを削除（新しいリストより多い場合）
        if len(existing_qa_chain) > len(qa_chain):
            for i in range(len(qa_chain), len(existing_qa_chain)):
                cur.execute('DELETE FROM qa_chain WHERE id = ?', (existing_qa_chain[i][0],))
    
    def add_followup_questions(self, diary_id: str, followup_questions: list[str]) -> bool:
        """既存の日記エントリにフォローアップ質問を追加（UPDATEベース）"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        try:
            # 既存のフォローアップ質問を取得
            cur.execute('SELECT id, question, order_index FROM followup_questions WHERE diary_entry_id = ? ORDER BY order_index', (diary_id,))
            existing_questions = cur.fetchall()
            
            # 新しいフォローアップ質問を処理
            for i, question in enumerate(followup_questions):
                if i < len(existing_questions):
                    # 既存のレコードを更新
                    cur.execute('''
                        UPDATE followup_questions SET question = ? WHERE id = ?
                    ''', (question, existing_questions[i][0]))
                else:
                    # 新しいレコードを追加
                    question_id = str(uuid.uuid4())
                    cur.execute('''
                        INSERT INTO followup_questions (id, diary_entry_id, question, order_index)
                        VALUES (?, ?, ?, ?)
                    ''', (question_id, diary_id, question, i))
            
            # 余分な既存レコードを削除（新しいリストより多い場合）
            if len(existing_questions) > len(followup_questions):
                for i in range(len(followup_questions), len(existing_questions)):
                    cur.execute('DELETE FROM followup_questions WHERE id = ?', (existing_questions[i][0],))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def add_qa_chain(self, diary_id: str, qa_chain: list[dict[str, Any]]) -> bool:
        """既存の日記エントリにQ&A履歴を追加（UPDATEベース）"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        try:
            # 既存のQ&A履歴を取得
            cur.execute('''
                SELECT id, question, answer, created_at, order_index
                FROM qa_chain 
                WHERE diary_entry_id = ? 
                ORDER BY order_index
            ''', (diary_id,))
            existing_qa_chain = cur.fetchall()
            
            # 新しいQ&A履歴を処理
            for i, qa in enumerate(qa_chain):
                if i < len(existing_qa_chain):
                    # 既存のレコードを更新
                    cur.execute('''
                        UPDATE qa_chain 
                        SET question = ?, answer = ?, created_at = ?
                        WHERE id = ?
                    ''', (qa.get('question', ''), qa.get('answer', ''), qa.get('created_at', ''), existing_qa_chain[i][0]))
                else:
                    # 新しいレコードを追加
                    qa_id = str(uuid.uuid4())
                    cur.execute('''
                        INSERT INTO qa_chain (id, diary_entry_id, question, answer, created_at, order_index)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (qa_id, diary_id, qa.get('question', ''), qa.get('answer', ''), qa.get('created_at', ''), i))
            
            # 余分な既存レコードを削除（新しいリストより多い場合）
            if len(existing_qa_chain) > len(qa_chain):
                for i in range(len(qa_chain), len(existing_qa_chain)):
                    cur.execute('DELETE FROM qa_chain WHERE id = ?', (existing_qa_chain[i][0],))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_all_diary_data(self) -> list[dict[str, Any]]:
        """全ての日記データを取得（JSON形式に変換）"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # メインエントリを取得
        cur.execute('''
            SELECT id, original_id, created_at, date, text, question, user_id
            FROM diary_entries
            ORDER BY created_at DESC
        ''')
        entries = cur.fetchall()
        
        result = []
        for entry in entries:
            diary_id = entry[0]
            
            # 関連データを取得
            topics = self._get_topics(cur, diary_id)
            emotions = self._get_emotions(cur, diary_id)
            thoughts = self._get_thoughts(cur, diary_id)
            goals = self._get_goals(cur, diary_id)
            followup_questions = self._get_followup_questions(cur, diary_id)
            qa_chain = self._get_qa_chain(cur, diary_id)
            
            # JSON形式に変換
            diary_entry = {
                'id': entry[1] or entry[0],  # original_idがあれば使用、なければUUID
                'created_at': entry[2],
                'date': entry[3],
                'text': entry[4],
                'question': entry[5],
                'user_id': entry[6],
                'topics': topics,
                'emotions': emotions,
                'thoughts': thoughts,
                'goals': goals,
                'followup_questions': followup_questions,
                'qa_chain': qa_chain
            }
            
            result.append(diary_entry)
        
        conn.close()
        return result
    
    def _get_topics(self, cur: sqlite3.Cursor, diary_id: str) -> list[str]:
        """トピックを取得"""
        cur.execute('SELECT topic FROM topics WHERE diary_entry_id = ? ORDER BY topic', (diary_id,))
        return [row[0] for row in cur.fetchall()]
    
    def _get_emotions(self, cur: sqlite3.Cursor, diary_id: str) -> list[str]:
        """感情を取得"""
        cur.execute('SELECT emotion FROM emotions WHERE diary_entry_id = ? ORDER BY emotion', (diary_id,))
        return [row[0] for row in cur.fetchall()]
    
    def _get_thoughts(self, cur: sqlite3.Cursor, diary_id: str) -> list[str]:
        """思考を取得"""
        cur.execute('SELECT thought FROM thoughts WHERE diary_entry_id = ? ORDER BY thought', (diary_id,))
        return [row[0] for row in cur.fetchall()]
    
    def _get_goals(self, cur: sqlite3.Cursor, diary_id: str) -> list[str]:
        """目標を取得"""
        cur.execute('SELECT goal FROM goals WHERE diary_entry_id = ? ORDER BY goal', (diary_id,))
        return [row[0] for row in cur.fetchall()]
    
    def _get_followup_questions(self, cur: sqlite3.Cursor, diary_id: str) -> list[str]:
        """追加質問を取得"""
        cur.execute('SELECT question FROM followup_questions WHERE diary_entry_id = ? ORDER BY order_index', (diary_id,))
        return [row[0] for row in cur.fetchall()]
    
    def _get_qa_chain(self, cur: sqlite3.Cursor, diary_id: str) -> list[dict[str, Any]]:
        """Q&A履歴を取得"""
        cur.execute('''
            SELECT question, answer, created_at, order_index
            FROM qa_chain 
            WHERE diary_entry_id = ? 
            ORDER BY order_index
        ''', (diary_id,))
        
        return [
            {
                'question': row[0],
                'answer': row[1],
                'created_at': row[2]
            }
            for row in cur.fetchall()
        ]
    
    def get_diary_by_date_range(self, start_date: str, end_date: str) -> list[dict[str, Any]]:
        """日付範囲で日記データを取得"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        cur.execute('''
            SELECT id, original_id, created_at, date, text, question, user_id
            FROM diary_entries
            WHERE date BETWEEN ? AND ?
            ORDER BY created_at DESC
        ''', (start_date, end_date))
        
        entries = cur.fetchall()
        result = []
        
        for entry in entries:
            diary_id = entry[0]
            
            # 関連データを取得
            topics = self._get_topics(cur, diary_id)
            emotions = self._get_emotions(cur, diary_id)
            thoughts = self._get_thoughts(cur, diary_id)
            goals = self._get_goals(cur, diary_id)
            followup_questions = self._get_followup_questions(cur, diary_id)
            qa_chain = self._get_qa_chain(cur, diary_id)
            
            diary_entry = {
                'id': entry[1] or entry[0],
                'created_at': entry[2],
                'date': entry[3],
                'text': entry[4],
                'question': entry[5],
                'user_id': entry[6],
                'topics': topics,
                'emotions': emotions,
                'thoughts': thoughts,
                'goals': goals,
                'followup_questions': followup_questions,
                'qa_chain': qa_chain
            }
            
            result.append(diary_entry)
        
        conn.close()
        return result
    
    def delete_diary_entry(self, entry_id: str) -> bool:
        """指定IDの日記エントリを削除"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        try:
            # まずUUIDを取得
            cur.execute('SELECT id FROM diary_entries WHERE original_id = ? OR id = ?', (entry_id, entry_id))
            result = cur.fetchone()
            
            if not result:
                return False
            
            uuid_id = result[0]
            
            # 関連データを削除（CASCADE制約により自動削除されるはずだが、念のため）
            cur.execute('DELETE FROM topics WHERE diary_entry_id = ?', (uuid_id,))
            cur.execute('DELETE FROM emotions WHERE diary_entry_id = ?', (uuid_id,))
            cur.execute('DELETE FROM thoughts WHERE diary_entry_id = ?', (uuid_id,))
            cur.execute('DELETE FROM goals WHERE diary_entry_id = ?', (uuid_id,))
            cur.execute('DELETE FROM followup_questions WHERE diary_entry_id = ?', (uuid_id,))
            cur.execute('DELETE FROM qa_chain WHERE diary_entry_id = ?', (uuid_id,))
            
            # メインエントリを削除
            cur.execute('DELETE FROM diary_entries WHERE id = ?', (uuid_id,))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def update_diary_entry(self, entry_id: str, updated_data: dict[str, Any]) -> bool:
        """日記エントリを更新"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        try:
            # UUIDを取得
            cur.execute('SELECT id FROM diary_entries WHERE original_id = ? OR id = ?', (entry_id, entry_id))
            result = cur.fetchone()
            
            if not result:
                return False
            
            uuid_id = result[0]
            
            # メインデータを更新
            cur.execute('''
                UPDATE diary_entries 
                SET text = ?, question = ?, created_at = ?, date = ?
                WHERE id = ?
            ''', (
                updated_data.get('text', ''),
                updated_data.get('question', ''),
                updated_data.get('created_at', ''),
                updated_data.get('date', ''),
                uuid_id
            ))
            
            # 関連データを削除して再挿入
            cur.execute('DELETE FROM topics WHERE diary_entry_id = ?', (uuid_id,))
            cur.execute('DELETE FROM emotions WHERE diary_entry_id = ?', (uuid_id,))
            cur.execute('DELETE FROM thoughts WHERE diary_entry_id = ?', (uuid_id,))
            cur.execute('DELETE FROM goals WHERE diary_entry_id = ?', (uuid_id,))
            cur.execute('DELETE FROM followup_questions WHERE diary_entry_id = ?', (uuid_id,))
            cur.execute('DELETE FROM qa_chain WHERE diary_entry_id = ?', (uuid_id,))
            
            # 新しい関連データを挿入
            self._upsert_related_data(cur, uuid_id, updated_data)
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    # ===== ユーザー認証機能 =====
    
    def _hash_password(self, password: str) -> str:
        """パスワードをハッシュ化"""
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return salt.hex() + key.hex()
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """パスワードを検証"""
        try:
            salt = bytes.fromhex(hashed[:64])
            key = bytes.fromhex(hashed[64:])
            new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
            return key == new_key
        except:
            return False
    
    def create_user(self, username: str, password: str) -> bool:
        """新規ユーザーを作成"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        try:
            # ユーザー名の重複チェック
            cur.execute('SELECT id FROM users WHERE username = ?', (username,))
            if cur.fetchone():
                return False
            
            # パスワードをハッシュ化
            password_hash = self._hash_password(password)
            user_id = str(uuid.uuid4())
            
            # ユーザーを作成
            cur.execute('''
                INSERT INTO users (id, username, password_hash)
                VALUES (?, ?, ?)
            ''', (user_id, username, password_hash))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"ユーザー作成エラー: {e}")
            return False
        finally:
            conn.close()
    
    def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """ユーザー認証"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        try:
            # ユーザー情報を取得
            cur.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
            result = cur.fetchone()
            
            if not result:
                return None
            
            user_id, password_hash = result
            
            # パスワードを検証
            if self._verify_password(password, password_hash):
                # 最終ログイン時刻を更新
                cur.execute('''
                    UPDATE users SET last_login = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (user_id,))
                conn.commit()
                return user_id
            
            return None
            
        except Exception as e:
            print(f"認証エラー: {e}")
            return None
        finally:
            conn.close()
    
    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """ユーザーIDからユーザー情報を取得"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        try:
            cur.execute('''
                SELECT id, username, created_at, last_login
                FROM users WHERE id = ?
            ''', (user_id,))
            
            result = cur.fetchone()
            if result:
                return {
                    'id': result[0],
                    'username': result[1],
                    'created_at': result[2],
                    'last_login': result[3]
                }
            return None
            
        except Exception as e:
            print(f"ユーザー取得エラー: {e}")
            return None
        finally:
            conn.close()
    
    def get_user_diary_data(self, user_id: str) -> list[dict[str, Any]]:
        """特定ユーザーの日記データを取得"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        try:
            # ユーザーの日記エントリを取得
            cur.execute('''
                SELECT id, original_id, created_at, date, text, question
                FROM diary_entries 
                WHERE user_id = ?
                ORDER BY created_at DESC
            ''', (user_id,))
            
            entries = []
            for row in cur.fetchall():
                entry = {
                    'id': row[0],
                    'original_id': row[1],
                    'created_at': row[2],
                    'date': row[3],
                    'text': row[4],
                    'question': row[5],
                    'user_id': user_id,
                    'topics': self._get_topics(cur, row[0]),
                    'emotions': self._get_emotions(cur, row[0]),
                    'thoughts': self._get_thoughts(cur, row[0]),
                    'goals': self._get_goals(cur, row[0]),
                    'followup_questions': self._get_followup_questions(cur, row[0]),
                    'qa_chain': self._get_qa_chain(cur, row[0])
                }
                entries.append(entry)
            
            return entries
            
        except Exception as e:
            print(f"ユーザーデータ取得エラー: {e}")
            return []
        finally:
            conn.close() 