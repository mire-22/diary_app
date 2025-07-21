"""
Supabase用データベースマネージャー
"""

import uuid
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from config.supabase_config import get_supabase_config

class DiaryManagerSupabase:
    """Supabase用日記データベースマネージャー"""
    
    def __init__(self):
        self.supabase = get_supabase_config()
        self.client = self.supabase.get_client()
    
    def get_current_user_id(self) -> Optional[str]:
        """現在のユーザーIDを取得"""
        user = self.supabase.get_current_user()
        return user.get('id') if user else None
    
    def create_diary_entry(self, text: str, entry_date: date, question: str = None) -> Optional[str]:
        """日記エントリを作成"""
        user_id = self.get_current_user_id()
        if not user_id:
            raise ValueError("ユーザーが認証されていません")
        
        entry_id = str(uuid.uuid4())
        
        try:
            response = self.client.table('diary_entries').insert({
                'id': entry_id,
                'original_id': f"entry_{entry_date.strftime('%Y%m%d')}_{datetime.now().strftime('%H%M%S')}",
                'date': entry_date.isoformat(),
                'text': text,
                'question': question,
                'user_id': user_id
            }).execute()
            
            if response.data:
                return entry_id
            return None
            
        except Exception as e:
            print(f"日記エントリ作成エラー: {e}")
            return None
    
    def get_diary_entries(self, start_date: date = None, end_date: date = None) -> List[Dict[str, Any]]:
        """日記エントリを取得"""
        user_id = self.get_current_user_id()
        if not user_id:
            return []
        
        try:
            query = self.client.table('diary_entries').select('*').eq('user_id', user_id)
            
            if start_date:
                query = query.gte('date', start_date.isoformat())
            if end_date:
                query = query.lte('date', end_date.isoformat())
            
            response = query.order('date', desc=True).execute()
            return response.data if response.data else []
            
        except Exception as e:
            print(f"日記エントリ取得エラー: {e}")
            return []
    
    def get_diary_entry(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """特定の日記エントリを取得"""
        user_id = self.get_current_user_id()
        if not user_id:
            return None
        
        try:
            response = self.client.table('diary_entries').select('*').eq('id', entry_id).eq('user_id', user_id).execute()
            return response.data[0] if response.data else None
            
        except Exception as e:
            print(f"日記エントリ取得エラー: {e}")
            return None
    
    def update_diary_entry(self, entry_id: str, text: str, question: str = None) -> bool:
        """日記エントリを更新"""
        user_id = self.get_current_user_id()
        if not user_id:
            return False
        
        try:
            update_data = {'text': text}
            if question:
                update_data['question'] = question
            
            response = self.client.table('diary_entries').update(update_data).eq('id', entry_id).eq('user_id', user_id).execute()
            return bool(response.data)
            
        except Exception as e:
            print(f"日記エントリ更新エラー: {e}")
            return False
    
    def delete_diary_entry(self, entry_id: str) -> bool:
        """日記エントリを削除"""
        user_id = self.get_current_user_id()
        if not user_id:
            return False
        
        try:
            response = self.client.table('diary_entries').delete().eq('id', entry_id).eq('user_id', user_id).execute()
            return bool(response.data)
            
        except Exception as e:
            print(f"日記エントリ削除エラー: {e}")
            return False
    
    def add_emotion(self, diary_entry_id: str, emotion: str) -> bool:
        """感情データを追加"""
        user_id = self.get_current_user_id()
        if not user_id:
            return False
        
        try:
            response = self.client.table('emotions').insert({
                'id': str(uuid.uuid4()),
                'diary_entry_id': diary_entry_id,
                'emotion': emotion,
                'user_id': user_id
            }).execute()
            return bool(response.data)
            
        except Exception as e:
            print(f"感情データ追加エラー: {e}")
            return False
    
    def add_topic(self, diary_entry_id: str, topic: str) -> bool:
        """トピックデータを追加"""
        user_id = self.get_current_user_id()
        if not user_id:
            return False
        
        try:
            response = self.client.table('topics').insert({
                'id': str(uuid.uuid4()),
                'diary_entry_id': diary_entry_id,
                'topic': topic,
                'user_id': user_id
            }).execute()
            return bool(response.data)
            
        except Exception as e:
            print(f"トピックデータ追加エラー: {e}")
            return False
    
    def add_thought(self, diary_entry_id: str, thought: str) -> bool:
        """思考データを追加"""
        user_id = self.get_current_user_id()
        if not user_id:
            return False
        
        try:
            response = self.client.table('thoughts').insert({
                'id': str(uuid.uuid4()),
                'diary_entry_id': diary_entry_id,
                'thought': thought,
                'user_id': user_id
            }).execute()
            return bool(response.data)
            
        except Exception as e:
            print(f"思考データ追加エラー: {e}")
            return False
    
    def add_goal(self, diary_entry_id: str, goal: str) -> bool:
        """目標データを追加"""
        user_id = self.get_current_user_id()
        if not user_id:
            return False
        
        try:
            response = self.client.table('goals').insert({
                'id': str(uuid.uuid4()),
                'diary_entry_id': diary_entry_id,
                'goal': goal,
                'user_id': user_id
            }).execute()
            return bool(response.data)
            
        except Exception as e:
            print(f"目標データ追加エラー: {e}")
            return False
    
    def get_emotions_for_entry(self, diary_entry_id: str) -> List[Dict[str, Any]]:
        """日記エントリの感情データを取得"""
        user_id = self.get_current_user_id()
        if not user_id:
            return []
        
        try:
            response = self.client.table('emotions').select('*').eq('diary_entry_id', diary_entry_id).eq('user_id', user_id).execute()
            return response.data if response.data else []
            
        except Exception as e:
            print(f"感情データ取得エラー: {e}")
            return []
    
    def get_topics_for_entry(self, diary_entry_id: str) -> List[Dict[str, Any]]:
        """日記エントリのトピックデータを取得"""
        user_id = self.get_current_user_id()
        if not user_id:
            return []
        
        try:
            response = self.client.table('topics').select('*').eq('diary_entry_id', diary_entry_id).eq('user_id', user_id).execute()
            return response.data if response.data else []
            
        except Exception as e:
            print(f"トピックデータ取得エラー: {e}")
            return []
    
    def get_thoughts_for_entry(self, diary_entry_id: str) -> List[Dict[str, Any]]:
        """日記エントリの思考データを取得"""
        user_id = self.get_current_user_id()
        if not user_id:
            return []
        
        try:
            response = self.client.table('thoughts').select('*').eq('diary_entry_id', diary_entry_id).eq('user_id', user_id).execute()
            return response.data if response.data else []
            
        except Exception as e:
            print(f"思考データ取得エラー: {e}")
            return []
    
    def get_goals_for_entry(self, diary_entry_id: str) -> List[Dict[str, Any]]:
        """日記エントリの目標データを取得"""
        user_id = self.get_current_user_id()
        if not user_id:
            return []
        
        try:
            response = self.client.table('goals').select('*').eq('diary_entry_id', diary_entry_id).eq('user_id', user_id).execute()
            return response.data if response.data else []
            
        except Exception as e:
            print(f"目標データ取得エラー: {e}")
            return []
    
    def get_statistics(self, start_date: date = None, end_date: date = None) -> Dict[str, Any]:
        """統計情報を取得"""
        user_id = self.get_current_user_id()
        if not user_id:
            return {}
        
        try:
            # 日記エントリ数
            entries_query = self.client.table('diary_entries').select('id', count='exact').eq('user_id', user_id)
            if start_date:
                entries_query = entries_query.gte('date', start_date.isoformat())
            if end_date:
                entries_query = entries_query.lte('date', end_date.isoformat())
            
            entries_response = entries_query.execute()
            total_entries = entries_response.count if entries_response.count else 0
            
            # 感情データ
            emotions_query = self.client.table('emotions').select('emotion').eq('user_id', user_id)
            emotions_response = emotions_query.execute()
            emotions = [item['emotion'] for item in emotions_response.data] if emotions_response.data else []
            
            # トピックデータ
            topics_query = self.client.table('topics').select('topic').eq('user_id', user_id)
            topics_response = topics_query.execute()
            topics = [item['topic'] for item in topics_response.data] if topics_response.data else []
            
            return {
                'total_entries': total_entries,
                'emotions': emotions,
                'topics': topics
            }
            
        except Exception as e:
            print(f"統計情報取得エラー: {e}")
            return {} 