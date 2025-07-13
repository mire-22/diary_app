import os
import json
import streamlit as st
import pandas as pd
import plotly.express as px
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from ai_analyzer import AIAnalyzer

# 分類カテゴリ
categories = [
    "自己成長・前進感情",
    "他者・環境との好意的関係",
    "自己受容・内的癒し",
    "自己評価の低下・葛藤",
    "不安・心配・迷い",
    "喪失・孤独",
    "その他"
]

def load_emotion_cache(path="data/emotion_cache.json"):
    """感情分類キャッシュを読み込み"""
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_emotion_cache(cache, path="data/emotion_cache.json"):
    """感情分類キャッシュを保存"""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def extract_emotions_with_date(data_dir):
    """dataディレクトリ内の全jsonからemotionとcreated_atを抽出"""
    emotion_records = []
    for fname in os.listdir(data_dir):
        if fname.endswith('.json'):
            with open(os.path.join(data_dir, fname), 'r', encoding='utf-8') as f:
                entries = json.load(f)
                for entry in entries:
                    # created_atから日付と時間を取得
                    created_at = entry.get('created_at', '')
                    if created_at:
                        # created_atがISO形式の場合はそのまま使用
                        for emo in entry.get('emotions', []):
                            emotion_records.append({
                                "date": created_at, 
                                "emotion": emo
                            })
                    else:
                        # created_atがない場合はdateを使用（フォールバック）
                        date = entry.get('date', '')
                        for emo in entry.get('emotions', []):
                            emotion_records.append({
                                "date": date, 
                                "emotion": emo
                            })
    return emotion_records

def classify_emotions_with_llm(emotion_records, categories, ai_analyzer: 'AIAnalyzer', cache_path="data/emotion_cache.json", use_cache=True):
    """emotionリストをLLMで7分類に分ける（キャッシュ機能付き）"""
    # キャッシュ機能の制御
    if not use_cache:
        emotion_cache = {}
    else:
        emotion_cache = load_emotion_cache(cache_path)
    
    result = {}
    for rec in emotion_records:
        date = rec['date']
        emotion = rec['emotion']
        
        # キャッシュにあれば再利用
        if emotion in emotion_cache:
            category = emotion_cache[emotion]
        else:
            # LLMに問い合わせ（1感情ずつ）
            prompt = f"""
# 役割
あなたは感情分類の専門家AIです。

# 入力
感情: 「{emotion}」
分類カテゴリ: {categories}

# 出力形式
次の形式で出力してください:
{{"分類": "カテゴリ名"}}

# 条件
- 必ずカテゴリのいずれかに分類してください
- 出力はJSON形式で正しく閉じてください
"""
            try:
                if ai_analyzer.use_gemini and ai_analyzer.model:
                    response = ai_analyzer.model.generate_content(prompt)
                    import re
                    match = re.search(r'\{[\s\S]*\}', response.text)
                    if match:
                        data = json.loads(match.group(0))
                        category = data.get('分類', categories[-1])
                    else:
                        category = categories[-1]
                else:
                    # モック分類
                    category = categories[-1]
            except Exception as e:
                print(f"分類失敗: {emotion} → {e}")
                category = categories[-1]
            
            # キャッシュに保存
            emotion_cache[emotion] = category

        # 結果に追加
        result.setdefault(date, {})[emotion] = category

    # キャッシュ保存
    save_emotion_cache(emotion_cache, cache_path)
    
    return result

def to_dataframe(classification_result):
    """分類結果をDataFrameに変換"""
    df_data = []
    for date, emotion_map in classification_result.items():
        for emotion, category in emotion_map.items():
            df_data.append({
                '日付': date,
                '感情': emotion,
                'カテゴリ': category
            })
    
    if not df_data:
        return pd.DataFrame()
    
    df = pd.DataFrame(df_data)
    
    # 日付列をdatetime型に変換（ISO形式に対応）
    try:
        df['日付'] = pd.to_datetime(df['日付'])
    except:
        # ISO形式でない場合は文字列のまま保持
        pass
    
    df = df.sort_values('日付')
    return df

def plot_emotion_trends(df):
    """感情トレンドを可視化"""
    if df.empty:
        st.warning("表示するデータがありません")
        return

    df_plot = df.copy()

    # 日付を文字列に変換し、空白を除去し、秒までで切る
    df_plot['日付'] = df_plot['日付'].astype(str).str.strip().str.slice(0, 19)

    # datetime型に変換（ここでNaTになるものを避ける）
    df_plot['日付'] = pd.to_datetime(df_plot['日付'], errors='coerce')

    # NaTの除去
    df_plot = df_plot.dropna(subset=['日付'])

    # 秒未満の情報を統一（必要なら）
    df_plot['日付'] = df_plot['日付'].dt.floor('S')


    st.subheader("変換後の日付データ例")
    st.dataframe(df_plot.head(10))

    # カテゴリごとの日付別出現件数を可視化
    fig = px.line(
        df_plot.groupby(['日付', 'カテゴリ']).size().reset_index(name='件数'),
        x='日付',
        y='件数',
        color='カテゴリ',
        markers=True,
        title='日付別感情カテゴリ出現回数'
    )
    fig.update_layout(
        xaxis_title="日付",
        yaxis_title="件数",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    # カテゴリ別集計
    st.subheader("📊 カテゴリ別集計")
    category_counts = df_plot['カテゴリ'].value_counts()

    col1, col2 = st.columns(2)
    with col1:
        fig_pie = px.pie(
            values=category_counts.values,
            names=category_counts.index,
            title="カテゴリ別分布"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        fig_bar = px.bar(
            x=category_counts.index,
            y=category_counts.values,
            title="カテゴリ別件数",
            labels={'x': 'カテゴリ', 'y': '件数'}
        )
        st.plotly_chart(fig_bar, use_container_width=True)



def test_emotion_classification_by_date():
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    ai_analyzer = AIAnalyzer()
    emotion_records = extract_emotions_with_date(data_dir)
    print('抽出された感情:', emotion_records)
    result = classify_emotions_with_llm(emotion_records, categories, ai_analyzer)
    print('分類結果:')
    for date, emo_map in result.items():
        print(f'--- {date} ---')
        for emo, cat in emo_map.items():
            print(f'{emo} → {cat}')

if __name__ == '__main__':
    test_emotion_classification_by_date() 