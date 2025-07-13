import datetime
from typing import Dict, Any, List
import os
import json
import streamlit as st
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.prompt_manager import PromptManager

class PeriodAnalyzer:
    """期間分析機能クラス"""
    
    def __init__(self, ai_analyzer=None):
        self.ai_analyzer = ai_analyzer
        self.use_gemini = False
        self.model = None
        self.prompt_manager = PromptManager()
        
        # AIアナライザーからGemini設定を取得
        if ai_analyzer:
            self.use_gemini = ai_analyzer.use_gemini
            self.model = ai_analyzer.model
    
    def analyze_period_summary(self, period_data: List[Dict[str, Any]], start_date: str, end_date: str, mode: str = "default", custom_prompt: str = "") -> Dict[str, Any]:
        """指定期間の日記データを構造化してまとめる"""
        if not period_data:
            return self._create_empty_summary(start_date, end_date, mode)
        
        # 期間データをテキストにまとめる
        combined_text = self._combine_period_data(period_data)
        
        # LLMで構造化分析
        prompt = self._create_period_analysis_prompt(combined_text, start_date, end_date, mode, custom_prompt)
        
        if self.use_gemini and self.model:
            return self._analyze_period_with_gemini(prompt, start_date, end_date, mode)
        else:
            return self._mock_period_analysis(period_data, start_date, end_date, mode)
    
    def _create_empty_summary(self, start_date: str, end_date: str, mode: str = "default") -> Dict[str, Any]:
        """空の期間まとめを作成"""
        return {
            "period": f"{start_date} 〜 {end_date}",
            "mode": mode,
            "summary": "この期間の日記データがありません。",
            "key_themes": [],
            "emotional_journey": [],
            "insights": [],
            "growth_areas": [],
            "recommendations": []
        }
    
    def _combine_period_data(self, period_data: List[Dict[str, Any]]) -> str:
        """期間データをテキストにまとめる"""
        combined_text = ""
        for entry in period_data:
            combined_text += f"\n=== {entry['date']} ===\n"
            combined_text += f"日記: {entry['text']}\n"
            
            # QAチェーンを追加
            qa_chain = entry.get('qa_chain', [])
            if qa_chain:
                combined_text += "質問と回答:\n"
                for i, qa in enumerate(qa_chain):
                    combined_text += f"Q{i+1}: {qa['question']}\n"
                    combined_text += f"A{i+1}: {qa['answer']}\n"
            
            # 分析結果も追加
            combined_text += f"トピック: {', '.join(entry.get('topics', []))}\n"
            combined_text += f"感情: {', '.join(entry.get('emotions', []))}\n"
            combined_text += f"思考: {', '.join(entry.get('thoughts', []))}\n"
            combined_text += f"目標: {', '.join(entry.get('goals', []))}\n"
            combined_text += "\n"
        
        return combined_text
    
    def _create_period_analysis_prompt(self, combined_text: str, start_date: str, end_date: str, mode: str = "default", custom_prompt: str = "") -> str:
        """期間分析用のプロンプトを作成"""
        try:
            # プロンプトマネージャーからプロンプトを取得
            prompt = self.prompt_manager.get_period_analysis_prompt(
                mode=mode,
                start_date=start_date,
                end_date=end_date,
                combined_text=combined_text,
                custom_prompt=custom_prompt
            )
            return prompt
        except Exception as e:
            # エラー時はフォールバック用のシンプルなプロンプトを返す
            print(f"プロンプト読み込みエラー: {e}")
            return f"""
# 期間分析
期間: {start_date} 〜 {end_date}
データ: {combined_text[:500]}...
分析モード: {mode}

この期間の日記データを分析してください。
"""
    
    def _analyze_period_with_gemini(self, prompt: str, start_date: str, end_date: str, mode: str = "default") -> Dict[str, Any]:
        """Gemini APIで期間分析を実行"""
        try:
            response = self.model.generate_content(prompt)
            import re
            
            if mode in ["default", "kpt", "ywt"]:
                # デフォルトモード、KPTモード、YWTモード: JSON形式を期待
                match = re.search(r'\{[\s\S]*\}', response.text)
                if match:
                    result = json.loads(match.group(0))
                    # modeフィールドを追加
                    result['mode'] = mode
                    return result
            else:
                # カスタムモード: テキスト形式で返す
                return {
                    "period": f"{start_date} 〜 {end_date}",
                    "mode": mode,
                    "custom_result": response.text,
                    "raw_response": response.text
                }
                
        except Exception as e:
            print('Period analysis error:', e)
        
        # エラー時はモックデータを返す
        return self._mock_period_analysis([], start_date, end_date, mode)
    
    def _mock_period_analysis(self, period_data: List[Dict[str, Any]], start_date: str, end_date: str, mode: str = "default") -> Dict[str, Any]:
        """モック期間分析データ"""
        if mode == "kpt":
            return {
                "period": f"{start_date} 〜 {end_date}",
                "mode": "kpt",
                "summary": f"この期間のKPT分析を行いました。{len(period_data)}件のエントリを基に分析しました。",
                "kpt_analysis": {
                    "keep": [
                        {
                            "topic": "習慣・ルーティン",
                            "items": ["継続すべき習慣1", "継続すべき習慣2"],
                            "reason": "効果的な習慣として定着している"
                        }
                    ],
                    "problem": [
                        {
                            "topic": "時間管理",
                            "items": ["改善すべき問題1", "改善すべき問題2"],
                            "impact": "効率性に影響している"
                        }
                    ],
                    "try": [
                        {
                            "topic": "新しいアプローチ",
                            "items": ["試してみたいこと1", "試してみたいこと2"],
                            "expected_effect": "改善が期待される"
                        }
                    ]
                },
                "key_themes": ["自己成長", "人間関係", "目標設定"],
                "recommendations": [
                    "毎日の振り返り習慣を継続する",
                    "感情の変化をより詳細に記録する",
                    "週次での目標見直しを行う"
                ]
            }
        elif mode == "ywt":
            return {
                "period": f"{start_date} 〜 {end_date}",
                "mode": "ywt",
                "summary": f"この期間のYWT分析を行いました。{len(period_data)}件のエントリを基に分析しました。",
                "ywt_analysis": {
                    "yatta": [
                        {
                            "topic": "学習・スキル向上",
                            "items": ["実際にやったこと1", "実際にやったこと2"],
                            "context": "学習活動の背景や状況"
                        }
                    ],
                    "wakatta": [
                        {
                            "topic": "自己理解",
                            "items": ["わかったこと1", "わかったこと2"],
                            "insight": "自己発見や学びの詳細"
                        }
                    ],
                    "tsugi": [
                        {
                            "topic": "次のステップ",
                            "items": ["次にやること1", "次にやること2"],
                            "reason": "次にやる理由や期待効果"
                        }
                    ]
                },
                "key_themes": ["自己成長", "学習", "目標設定"],
                "recommendations": [
                    "学んだことを実践に活かす",
                    "継続的な学習習慣を維持する",
                    "定期的な振り返りを行う"
                ]
            }
        else:  # default mode
            return {
                "period": f"{start_date} 〜 {end_date}",
                "mode": "default",
                "summary": f"この期間は{len(period_data)}件の日記があり、様々な出来事や感情の変化が記録されました。",
                "key_themes": ["自己成長", "人間関係", "目標設定"],
                "emotional_journey": [
                    {"date": start_date, "emotion": "期待", "context": "新しい期間の開始"},
                    {"date": end_date, "emotion": "達成感", "context": "期間の振り返り"}
                ],
                "insights": [
                    "継続的な記録の重要性",
                    "感情の変化を観察することの価値",
                    "目標設定と振り返りの効果"
                ],
                "growth_areas": [
                    "感情の自己認識",
                    "目標の具体化"
                ],
                "recommendations": [
                    "毎日の振り返り習慣を継続する",
                    "感情の変化をより詳細に記録する",
                    "週次での目標見直しを行う"
                ]
            }
    
    def analyze_weekly_trends(self, period_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """週次トレンド分析（拡張機能）"""
        if not period_data:
            return {"weekly_trends": [], "summary": "データが不足しています。"}
        
        # 週次でデータをグループ化
        weekly_groups = {}
        for entry in period_data:
            date = datetime.datetime.strptime(entry['date'], '%Y-%m-%d')
            week_start = date - datetime.timedelta(days=date.weekday())
            week_key = week_start.strftime('%Y-%m-%d')
            
            if week_key not in weekly_groups:
                weekly_groups[week_key] = []
            weekly_groups[week_key].append(entry)
        
        # 週次分析
        weekly_trends = []
        for week_start, entries in weekly_groups.items():
            week_end = (datetime.datetime.strptime(week_start, '%Y-%m-%d') + 
                       datetime.timedelta(days=6)).strftime('%Y-%m-%d')
            
            # 感情の集計
            emotions = []
            for entry in entries:
                emotions.extend(entry.get('emotions', []))
            
            # トピックの集計
            topics = []
            for entry in entries:
                topics.extend(entry.get('topics', []))
            
            weekly_trends.append({
                "week": f"{week_start} 〜 {week_end}",
                "entry_count": len(entries),
                "top_emotions": self._get_top_items(emotions, 3),
                "top_topics": self._get_top_items(topics, 3),
                "entries": entries
            })
        
        return {
            "weekly_trends": weekly_trends,
            "summary": f"{len(weekly_trends)}週間のデータを分析しました。"
        }
    
    def analyze_monthly_summary(self, period_data: List[Dict[str, Any]], year_month: str) -> Dict[str, Any]:
        """月次サマリー分析（拡張機能）"""
        if not period_data:
            return {"monthly_summary": {}, "summary": "データが不足しています。"}
        
        # 指定月のデータをフィルタ
        monthly_data = [
            entry for entry in period_data 
            if entry['date'].startswith(year_month)
        ]
        
        if not monthly_data:
            return {"monthly_summary": {}, "summary": f"{year_month}のデータがありません。"}
        
        # 月次統計
        total_entries = len(monthly_data)
        total_words = sum(len(entry['text']) for entry in monthly_data)
        
        # 感情・トピックの集計
        all_emotions = []
        all_topics = []
        all_thoughts = []
        all_goals = []
        
        for entry in monthly_data:
            all_emotions.extend(entry.get('emotions', []))
            all_topics.extend(entry.get('topics', []))
            all_thoughts.extend(entry.get('thoughts', []))
            all_goals.extend(entry.get('goals', []))
        
        return {
            "monthly_summary": {
                "period": year_month,
                "total_entries": total_entries,
                "total_words": total_words,
                "avg_words_per_entry": total_words // total_entries if total_entries > 0 else 0,
                "top_emotions": self._get_top_items(all_emotions, 5),
                "top_topics": self._get_top_items(all_topics, 5),
                "top_thoughts": self._get_top_items(all_thoughts, 3),
                "top_goals": self._get_top_items(all_goals, 3),
                "entries": monthly_data
            },
            "summary": f"{year_month}の月次サマリーを作成しました。"
        }
    
    def _get_top_items(self, items: List[str], top_n: int) -> List[tuple]:
        """アイテムの出現回数を集計して上位N個を返す"""
        item_counts = {}
        for item in items:
            item_counts[item] = item_counts.get(item, 0) + 1
        
        return sorted(item_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    def create_export_text(self, summary_result: Dict[str, Any], period_data: List[Dict[str, Any]]) -> str:
        """エクスポート用のテキストを作成"""
        mode = summary_result.get('mode', 'default')
        
        # デバッグ情報
        print(f"create_export_text called with mode: {mode}")
        print(f"summary_result keys: {list(summary_result.keys())}")
        print(f"period_data length: {len(period_data)}")
        
        export_text = f"""
# 日記期間まとめ
{summary_result.get('period', '')}
分析モード: {mode}

"""
        
        if mode == 'custom':
            # カスタム分析結果
            export_text += f"## 🎨 カスタム分析結果\n"
            custom_result = summary_result.get('custom_result', '')
            if custom_result:
                export_text += f"{custom_result}\n"
            else:
                export_text += "カスタム分析の結果がありません。\n"
        elif mode == 'kpt':
            # KPT分析結果
            export_text += f"## 🎯 KPT分析結果\n"
            export_text += f"### 概要\n"
            export_text += f"{summary_result.get('summary', '')}\n"
            
            kpt_analysis = summary_result.get('kpt_analysis', {})
            if kpt_analysis:
                export_text += f"\n### ✅ Keep（継続すべきこと）\n"
                for i, keep in enumerate(kpt_analysis.get('keep', []), 1):
                    export_text += f"{i}. トピック: {keep.get('topic', '')}\n"
                    export_text += f"   項目: {', '.join(keep.get('items', []))}\n"
                    export_text += f"   理由: {keep.get('reason', '')}\n\n"
                
                export_text += f"### ⚠️ Problem（改善すべき問題）\n"
                for i, problem in enumerate(kpt_analysis.get('problem', []), 1):
                    export_text += f"{i}. トピック: {problem.get('topic', '')}\n"
                    export_text += f"   項目: {', '.join(problem.get('items', []))}\n"
                    export_text += f"   影響: {problem.get('impact', '')}\n\n"
                
                export_text += f"### 🚀 Try（試してみたいこと）\n"
                for i, try_item in enumerate(kpt_analysis.get('try', []), 1):
                    export_text += f"{i}. トピック: {try_item.get('topic', '')}\n"
                    export_text += f"   項目: {', '.join(try_item.get('items', []))}\n"
                    export_text += f"   期待効果: {try_item.get('expected_effect', '')}\n\n"
            
            export_text += f"\n### 主要テーマ\n"
            for i, theme in enumerate(summary_result.get('key_themes', []), 1):
                export_text += f"{i}. {theme}\n"
            
            export_text += f"\n### 推奨事項\n"
            for i, rec in enumerate(summary_result.get('recommendations', []), 1):
                export_text += f"{i}. {rec}\n"
        elif mode == 'ywt':
            # YWT分析結果
            export_text += f"## 📝 YWT分析結果\n"
            export_text += f"### 概要\n"
            export_text += f"{summary_result.get('summary', '')}\n"
            
            ywt_analysis = summary_result.get('ywt_analysis', {})
            if ywt_analysis:
                export_text += f"\n### ✅ Yatta（やったこと）\n"
                for i, yatta in enumerate(ywt_analysis.get('yatta', []), 1):
                    export_text += f"{i}. トピック: {yatta.get('topic', '')}\n"
                    export_text += f"   項目: {', '.join(yatta.get('items', []))}\n"
                    export_text += f"   背景: {yatta.get('context', '')}\n\n"
                
                export_text += f"### 💡 Wakatta（わかったこと）\n"
                for i, wakatta in enumerate(ywt_analysis.get('wakatta', []), 1):
                    export_text += f"{i}. トピック: {wakatta.get('topic', '')}\n"
                    export_text += f"   項目: {', '.join(wakatta.get('items', []))}\n"
                    export_text += f"   発見: {wakatta.get('insight', '')}\n\n"
                
                export_text += f"### 🚀 Tsugi（次やること）\n"
                for i, tsugi in enumerate(ywt_analysis.get('tsugi', []), 1):
                    export_text += f"{i}. トピック: {tsugi.get('topic', '')}\n"
                    export_text += f"   項目: {', '.join(tsugi.get('items', []))}\n"
                    export_text += f"   理由: {tsugi.get('reason', '')}\n\n"
            
            export_text += f"\n### 主要テーマ\n"
            for i, theme in enumerate(summary_result.get('key_themes', []), 1):
                export_text += f"{i}. {theme}\n"
            
            export_text += f"\n### 推奨事項\n"
            for i, rec in enumerate(summary_result.get('recommendations', []), 1):
                export_text += f"{i}. {rec}\n"
        else:
            # デフォルト分析結果
            export_text += f"## 📊 デフォルト分析結果\n"
            export_text += f"### 概要\n"
            export_text += f"{summary_result.get('summary', '')}\n"
            
            export_text += f"\n### 主要テーマ\n"
            for i, theme in enumerate(summary_result.get('key_themes', []), 1):
                export_text += f"{i}. {theme}\n"
            
            export_text += f"\n### 感情の軌跡\n"
            for journey in summary_result.get('emotional_journey', []):
                export_text += f"- {journey.get('date', '')}: {journey.get('emotion', '')} - {journey.get('context', '')}\n"
            
            export_text += f"\n### 洞察\n"
            for i, insight in enumerate(summary_result.get('insights', []), 1):
                export_text += f"{i}. {insight}\n"
            
            export_text += f"\n### 成長領域\n"
            for i, area in enumerate(summary_result.get('growth_areas', []), 1):
                export_text += f"{i}. {area}\n"
            
            export_text += f"\n### 推奨事項\n"
            for i, rec in enumerate(summary_result.get('recommendations', []), 1):
                export_text += f"{i}. {rec}\n"
        
        # 元データ
        export_text += f"\n## 📊 元データ ({len(period_data)}件)\n"
        if period_data:
            for entry in period_data:
                export_text += f"\n### {entry.get('date', 'Unknown Date')}\n"
                export_text += f"内容: {entry.get('text', 'No content')}\n"
                export_text += f"トピック: {', '.join(entry.get('topics', []))}\n"
                export_text += f"感情: {', '.join(entry.get('emotions', []))}\n"
                
                qa_chain = entry.get('qa_chain', [])
                if qa_chain:
                    export_text += "質問と回答:\n"
                    for i, qa in enumerate(qa_chain):
                        export_text += f"Q{i+1}: {qa.get('question', '')}\n"
                        export_text += f"A{i+1}: {qa.get('answer', '')}\n"
        else:
            export_text += "元データがありません。\n"
        
        # デバッグ情報
        print(f"Export text length: {len(export_text)} characters")
        
        return export_text 