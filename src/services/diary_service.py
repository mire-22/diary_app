"""
日記関連のビジネスロジックを管理するクラス
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from diary_manager_sqlite import DiaryManagerSQLite
from ai_analyzer import AIAnalyzer
from utils.validators import Validator

class DiaryService:
    """日記関連のビジネスロジックを管理するクラス"""
    
    def __init__(self, diary_manager: DiaryManagerSQLite, ai_analyzer: AIAnalyzer):
        self.diary_manager = diary_manager
        self.ai_analyzer = ai_analyzer
    
    def create_diary_entry(self, text: str, date: str, user_id: str) -> Dict[str, Any]:
        """日記エントリを作成"""
        # バリデーション
        is_valid, error = Validator.validate_diary_content(text)
        if not is_valid:
            raise ValueError(error)
        
        # AI分析で日記エントリを作成
        diary_entry = self.ai_analyzer.create_diary_entry(text)
        diary_entry['date'] = date
        diary_entry['user_id'] = user_id
        
        # データベースに保存
        entry_id = self.diary_manager.add_diary_entry(diary_entry)
        diary_entry['id'] = entry_id
        
        return diary_entry
    
    def get_user_diary_data(self, user_id: str) -> List[Dict[str, Any]]:
        """ユーザーの日記データを取得"""
        return self.diary_manager.get_user_diary_data(user_id)
    
    def get_diary_by_date(self, user_id: str, date: str) -> List[Dict[str, Any]]:
        """指定日付の日記データを取得"""
        all_data = self.get_user_diary_data(user_id)
        return [entry for entry in all_data if entry.get('date') == date]
    
    def update_diary_entry(self, entry_id: str, updated_data: Dict[str, Any]) -> bool:
        """日記エントリを更新"""
        # バリデーション
        if 'text' in updated_data:
            is_valid, error = Validator.validate_diary_content(updated_data['text'])
            if not is_valid:
                raise ValueError(error)
        
        return self.diary_manager.update_diary_entry(entry_id, updated_data)
    
    def delete_diary_entry(self, entry_id: str) -> bool:
        """日記エントリを削除"""
        return self.diary_manager.delete_diary_entry(entry_id)
    
    def reanalyze_entry(self, entry_id: str, user_id: str) -> Dict[str, Any]:
        """日記エントリを再分析"""
        # 元のエントリを取得
        all_data = self.get_user_diary_data(user_id)
        original_entry = None
        for entry in all_data:
            if entry.get('id') == entry_id:
                original_entry = entry
                break
        
        if not original_entry:
            raise ValueError("日記エントリが見つかりません")
        
        # 再分析実行
        analysis_result = self.ai_analyzer.analyze_diary(original_entry['text'])
        
        # 更新データを準備
        updated_data = {
            'topics': analysis_result.get('topics', []),
            'emotions': analysis_result.get('emotions', []),
            'thoughts': analysis_result.get('thoughts', []),
            'goals': analysis_result.get('goals', []),
            'question': analysis_result.get('question', ''),
            'followup_questions': analysis_result.get('followup_questions', [])
        }
        
        # データベースを更新
        success = self.update_diary_entry(entry_id, updated_data)
        if not success:
            raise ValueError("再分析の保存に失敗しました")
        
        return updated_data
    
    def save_qa_chain(self, entry_id: str, question: str, answer: str) -> bool:
        """Q&Aチェーンを保存"""
        # バリデーション
        is_valid, error = Validator.validate_answer_content(answer)
        if not is_valid:
            raise ValueError(error)
        
        # Q&Aチェーンを作成
        qa_entry = {
            'question': question,
            'answer': answer,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return self.diary_manager.add_qa_chain(entry_id, [qa_entry])
    
    def update_entry_date(self, entry_id: str, new_date: str) -> bool:
        """日記エントリの日付を更新"""
        # 日付形式のバリデーション
        try:
            datetime.strptime(new_date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("日付形式が正しくありません")
        
        updated_data = {'date': new_date}
        return self.update_diary_entry(entry_id, updated_data)
    
    def get_diary_statistics(self, user_id: str) -> Dict[str, Any]:
        """日記統計情報を取得"""
        diary_data = self.get_user_diary_data(user_id)
        
        if not diary_data:
            return {
                'total_entries': 0,
                'date_range': None,
                'top_topics': [],
                'top_emotions': [],
                'average_entries_per_day': 0
            }
        
        # 統計情報を計算
        total_entries = len(diary_data)
        
        # 日付範囲
        dates = [entry.get('date', '') for entry in diary_data if entry.get('date')]
        date_range = {
            'start': min(dates) if dates else None,
            'end': max(dates) if dates else None
        }
        
        # トピック・感情の集計
        topic_counts = {}
        emotion_counts = {}
        
        for entry in diary_data:
            for topic in entry.get('topics', []):
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
            for emotion in entry.get('emotions', []):
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        top_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # 1日あたりの平均エントリ数
        if date_range['start'] and date_range['end']:
            start_date = datetime.strptime(date_range['start'], '%Y-%m-%d')
            end_date = datetime.strptime(date_range['end'], '%Y-%m-%d')
            days_diff = (end_date - start_date).days + 1
            avg_entries_per_day = total_entries / days_diff if days_diff > 0 else 0
        else:
            avg_entries_per_day = 0
        
        return {
            'total_entries': total_entries,
            'date_range': date_range,
            'top_topics': top_topics,
            'top_emotions': top_emotions,
            'average_entries_per_day': round(avg_entries_per_day, 2)
        } 