import datetime
from typing import Dict, Any, List
import os
import json
import streamlit as st

class AIAnalyzer:
    """AI分析機能クラス"""
    
    def __init__(self):
        self.prompt_path = os.path.join(os.path.dirname(__file__), 'prompts', 'analyze_diary_prompt.txt')
        self.prompt_template = self._load_prompt()
        self.use_gemini = False
        self.model = None
        # st.secretsからAPIキー取得
        gemini_api_key = st.secrets.get("GEMINI_API_KEY")
        if gemini_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_api_key)
                self.model = genai.GenerativeModel("gemini-1.5-flash")
                self.use_gemini = True
            except ImportError:
                st.error("google-generativeaiパッケージがインストールされていません。pip install google-generativeai でインストールしてください。")
                st.stop()
        else:
            st.error("GEMINI_API_KEYが設定されていません。.streamlit/secrets.tomlファイルにGEMINI_API_KEYを追加してください。")
            st.stop()
    
    def _load_prompt(self) -> str:
        try:
            with open(self.prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return ""
    
    def analyze_diary(self, text: str, qa_chain: list = None) -> Dict[str, Any]:
        """日記テキストとqa_chainをGemini APIで分析（APIキーがなければモック）"""
        # プロンプト組み立て
        prompt = self.prompt_template.replace("{{user_input}}", text)
        if qa_chain:
            prompt += "\n\n# これまでの質問と回答\n"
            for i, qa in enumerate(qa_chain):
                prompt += f"Q{i+1}: {qa['question']}\nA{i+1}: {qa['answer']}\n"
        if self.use_gemini and self.model:
            return self._analyze_with_gemini_prompt(prompt)
        else:
            return self._mock_analyze(text)
    
    def _analyze_with_gemini_prompt(self, prompt: str) -> Dict[str, Any]:
        response = self.model.generate_content(prompt)
        print('Gemini response:', response.text)
        import re
        match = re.search(r'\{[\s\S]*\}', response.text)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception as e:
                print('JSON parse error:', e)
        return self._mock_analyze("")
    
    def _mock_analyze(self, text: str) -> Dict[str, Any]:
        analysis_result = {
            "date": datetime.date.today().strftime("%Y-%m-%d"),
            "text": text,
            "topics": ["AI", "習慣化"],
            "emotions": ["前向き"],
            "thoughts": ["もっと記録したい"],
            "goals": ["毎日書きたい"],
            "question": "なぜAIに関心があると感じたのですか？",
            "followup_questions": [
                "なぜそう思ったのか？",
                "それはいつからそう感じていた？",
                "それを実現するために何ができそう？"
            ]
        }
        return analysis_result
    
    def create_diary_entry(self, text: str) -> Dict[str, Any]:
        llm_result = self.analyze_diary(text)
        now = datetime.datetime.now()
        entry = {
            "id": f"entry_{now.strftime('%Y%m%d_%H%M%S_%f')}",
            "created_at": now.strftime("%Y-%m-%d %H:%M:%S"),
            "date": now.strftime("%Y-%m-%d"),
            "text": text,
        }
        # LLM出力のid, created_at, date, textは無視し、他のフィールドのみマージ
        for k, v in llm_result.items():
            if k not in ["id", "created_at", "date", "text"]:
                entry[k] = v
        return entry
    
    def analyze_trends(self, diary_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not diary_data:
            return {}
        topic_counts = {}
        emotion_counts = {}
        for entry in diary_data:
            for topic in entry.get('topics', []):
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
            for emotion in entry.get('emotions', []):
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        top_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        top_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        return {
            "total_entries": len(diary_data),
            "top_topics": top_topics,
            "top_emotions": top_emotions,
            "date_range": {
                "start": min(entry.get('date', '') for entry in diary_data),
                "end": max(entry.get('date', '') for entry in diary_data)
            }
        }
    
    def generate_next_question(self, text: str, qa_chain: list) -> str:
        """元テキストとqa_chainをもとに次の深掘り質問をLLMで生成"""
        # プロンプト組み立て
        prompt = """
# 役割
あなたはユーザーの内省を深めるAIです。

# 入力
日記本文:
"""
        prompt += text + "\n"
        if qa_chain:
            prompt += "\n# これまでの質問と回答\n"
            for i, qa in enumerate(qa_chain):
                prompt += f"Q{i+1}: {qa['question']}\nA{i+1}: {qa['answer']}\n"
        prompt += """

# 出力形式
次の深掘り質問を1つだけJSONで返してください。
{"next_question": "..."}

# 条件
- これまでの質問・回答と重複しないこと
- ユーザーの思考や感情をさらに深める内容にすること
- JSON形式は正確に閉じてください
"""
        if self.use_gemini and self.model:
            response = self.model.generate_content(prompt)
            import re
            match = re.search(r'\{[\s\S]*\}', response.text)
            if match:
                try:
                    data = json.loads(match.group(0))
                    return data.get('next_question', '')
                except Exception as e:
                    print('JSON parse error (next_question):', e)
        # モック
        return "この出来事から学べることは何ですか？"
    
 