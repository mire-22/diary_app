import os
import json
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict
from ..ai_analyzer import AIAnalyzer

# 分類カテゴリ（固定）
CATEGORIES = [
    "自己成長・前進感情",
    "他者・環境との好意的関係",
    "自己受容・内的癒し",
    "自己評価の低下・葛藤",
    "不安・心配・迷い",
    "喪失・孤独",
    "その他"
]

# -----------------------
# 感情タグの抽出
# -----------------------
def extract_emotions_with_date(data_dir: str) -> List[Dict[str, str]]:
    """dataディレクトリ内の全jsonからemotionと日付を抽出"""
    emotion_records = []
    for fname in os.listdir(data_dir):
        if fname.endswith('.json'):
            with open(os.path.join(data_dir, fname), 'r', encoding='utf-8') as f:
                entries = json.load(f)
                for entry in entries:
                    date = entry.get('date', '')
                    for emo in entry.get('emotions', []):
                        emotion_records.append({"date": date, "emotion": emo})
    return emotion_records

# -----------------------
# LLMによる分類
# -----------------------
def classify_emotions_with_llm(emotion_records: List[Dict[str, str]],
                                categories: List[str],
                                ai_analyzer: AIAnalyzer,
                                use_cache: bool = True,
                                cache_path: str = "data/emotion_classification_cache.json") -> Dict[str, Dict[str, str]]:
    """emotionリストをLLMで7分類に分ける（日付情報も保持）"""

    if use_cache and os.path.exists(cache_path):
        return load_classification_cache(cache_path)

    date_to_emotions = {}
    for rec in emotion_records:
        date_to_emotions.setdefault(rec['date'], []).append(rec['emotion'])

    result = {}
    for date, emotions in date_to_emotions.items():
        prompt = f"""
# 役割
あなたは感情分類の専門家AIです。

# 入力
感情リスト: {emotions}
分類カテゴリ: {categories}

# 出力形式
各感情がどのカテゴリに属するかを、次のJSON形式で出力してください。
{{
  "分類": {{
    "感情1": "カテゴリ名",
    "感情2": "カテゴリ名",
    ...
  }}
}}

# 条件
- 必ず上記のカテゴリのいずれかに分類すること
- JSON形式は正確に閉じてください
"""
        if ai_analyzer.use_gemini and ai_analyzer.model:
            try:
                response = ai_analyzer.model.generate_content(prompt)
                match = re.search(r'\{[\s\S]*\}', response.text)
                if match:
                    data = json.loads(match.group(0))
                    result[date] = data.get('分類', {})
                    continue
            except Exception as e:
                print(f'[ERROR] LLM解析失敗 ({date}):', e)

        # fallback
        result[date] = {emo: categories[-1] for emo in emotions}

    if use_cache:
        save_classification_cache(result, cache_path)

    return result

# -----------------------
# キャッシュ保存／読み込み
# -----------------------
def save_classification_cache(result: Dict, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

def load_classification_cache(path: str) -> Dict:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# -----------------------
# DataFrame変換
# -----------------------
def to_dataframe(classification_result: Dict[str, Dict[str, str]]) -> pd.DataFrame:
    records = []
    for date, emo_map in classification_result.items():
        for emo, cat in emo_map.items():
            records.append({"date": pd.to_datetime(date), "emotion": emo, "category": cat})
    return pd.DataFrame(records)

# -----------------------
# 可視化（週次トレンド）
# -----------------------
def plot_emotion_trends(df: pd.DataFrame):
    """週ごとのカテゴリ別感情出現数を折れ線グラフとヒートマップで可視化"""
    df['week'] = df['date'].dt.to_period("W").apply(lambda r: r.start_time)
    weekly_counts = df.groupby(['week', 'category']).size().unstack(fill_value=0)

    # 折れ線グラフ
    plt.figure(figsize=(10, 6))
    weekly_counts.plot(marker='o')
    plt.title("週ごとの感情カテゴリ別出現回数")
    plt.ylabel("出現回数")
    plt.xlabel("週")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend(title="感情カテゴリ")
    plt.tight_layout()
    plt.show()

    # ヒートマップ
    plt.figure(figsize=(10, 6))
    sns.heatmap(weekly_counts.T, cmap="YlGnBu", annot=True, fmt="d")
    plt.title("感情カテゴリの週次ヒートマップ")
    plt.xlabel("週")
    plt.ylabel("感情カテゴリ")
    plt.tight_layout()
    plt.show()
