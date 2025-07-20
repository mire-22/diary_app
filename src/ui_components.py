import streamlit as st
from typing import Dict, Any, List
import datetime
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from diary_manager_sqlite import DiaryManagerSQLite
from ai_analyzer import AIAnalyzer
from period_analyzer import PeriodAnalyzer

class UIComponents:
    """UIコンポーネントクラス"""
    
    def __init__(self, diary_manager: DiaryManagerSQLite, ai_analyzer: AIAnalyzer, period_analyzer=None):
        self.diary_manager = diary_manager
        self.ai_analyzer = ai_analyzer
        self.period_analyzer = period_analyzer if period_analyzer else PeriodAnalyzer(ai_analyzer)
    
    def _get_user_diary_data(self, user_id: str = None):
        """ユーザー別の日記データを取得"""
        if user_id:
            return self.diary_manager.get_user_diary_data(user_id)
        else:
            return self.diary_manager.get_all_diary_data()
    
    def show_home(self) -> None:
        """ホーム画面を表示"""
        st.title("📝 AI日記アプリ")
        st.write("あなたの日記をAIが分析し、興味・感情・思考を構造化します。")

        # アプリの概要
        st.markdown("### 🚀 主な機能")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **✍️ 日記を書く**
            - AIが自動で分析
            - 感情・トピック・思考を抽出
            - チャット形式で対話
            
            **📚 履歴一覧**
            - 過去の日記を確認
            - 日付変更機能
            - 検索・フィルタリング
            """)
        
        with col2:
            st.markdown("""
            **📊 統計情報**
            - 感情の傾向分析
            - よく書くトピック
            - 時系列での変化
            
            **🎭 感情分析**
            - 感情の詳細分類
            - 週次変化グラフ
            - データ可視化
            """)
        
        # 最近の日記を表示
        st.markdown("### 📅 最近の日記")
        user_id = st.session_state.get('user_id')
        diary_data = self._get_user_diary_data(user_id)
        if diary_data:
            recent_entries = sorted(diary_data, key=lambda x: x.get('created_at', ''), reverse=True)[:3]
            for entry in recent_entries:
                with st.expander(f"📝 {entry['date']} - {entry['text'][:50]}..."):
                    st.write(f"**内容:** {entry['text']}")
                    st.write(f"**トピック:** {', '.join(entry.get('topics', []))}")
                    st.write(f"**感情:** {', '.join(entry.get('emotions', []))}")
        else:
            st.info("まだ日記がありません。左のメニューから「日記を書く」を選択して、最初の日記を書いてみましょう！")
    
    def show_write(self) -> None:
        """日記投稿画面を表示（チャット形式、入力欄は一番上）"""
        st.title("✍️ 日記を書く")
        
        # 新しい入力フォーム（ページ最上部）
        st.markdown("### 💭 新しい記録を追加")
        with st.form("diary_form"):
            # 日付選択フィールド
            selected_date = st.date_input(
                "📅 日付を選択",
                value=datetime.date.today(),
                help="この日記の日付を選択してください"
            )
            
            diary_input = st.text_area(
                "今日の出来事や思ったことを自由に書いてください", 
                height=100,
                placeholder="ここに日記を書いてください...",
                help="エンターキーで改行、Ctrl+Enterで送信できます"
            )
            submit_button = st.form_submit_button("送信して分析する", type="primary")

        if submit_button:
            if diary_input.strip():
                # AI分析で日記エントリを作成
                diary_entry = self.ai_analyzer.create_diary_entry(diary_input)
                # 選択された日付を設定
                diary_entry['date'] = selected_date.strftime('%Y-%m-%d')
                # ユーザーIDを設定
                user_id = st.session_state.get('user_id')
                if user_id:
                    diary_entry['user_id'] = user_id
                
                # データベースに保存
                try:
                    entry_id = self.diary_manager.add_diary_entry(diary_entry)
                    st.success("✅ 記録を保存しました！")
                    st.rerun()
                except Exception as e:
                    st.error(f"保存エラー: {e}")
            else:
                st.error("日記の内容を入力してください。")

        # 選択された日付の日記データを取得（SQLite対応）
        selected_date_str = selected_date.strftime('%Y-%m-%d')
        user_id = st.session_state.get('user_id')
        all_entries = self._get_user_diary_data(user_id)
        selected_date_entries = [entry for entry in all_entries if entry.get('date') == selected_date_str]
        # チャット履歴を表示
        if selected_date_entries:
            st.markdown(f"### 📅 {selected_date_str} の記録")
            for idx, entry in enumerate(selected_date_entries):
                self._display_chat_entry_with_followups(entry, idx)
        else:
            st.info(f"{selected_date_str} の記録はまだありません。新しい記録を追加してみましょう！")
    
    def _display_chat_entry_with_followups(self, entry: Dict[str, Any], idx: int) -> None:
        # ユーザー入力部分
        with st.chat_message("user"):
            st.write(f"**📝 {entry['created_at'][11:16]} {entry['date']} の日記**")
            st.write(entry['text'])
        # QAチェーン（質問と回答の連なり）
        qa_chain = entry.get('qa_chain', [])
        for i, qa in enumerate(qa_chain):
            with st.container():
                st.markdown(f"<div style='margin:8px 0;padding:12px;border-radius:8px;background:#f7f7fa;'>"
                            f"<b>👤 Q{i+1}:</b> {qa['question']}<br>"
                            f"<b>🗨️ A{i+1}:</b> {qa['answer']}"
                            "</div>", unsafe_allow_html=True)
        # 分析まとめボックス
        with st.expander("🔍 分析まとめを見る", expanded=True):
            st.markdown(self._render_analysis_summary(entry), unsafe_allow_html=True)
            if st.button("再分析", key=f"reanalyze_{entry['id']}_{idx}"):
                self._reanalyze_entry(entry['id'])
                st.success("再分析しました！")
                st.rerun()
        # 次の質問（未回答）
        next_question = None
        if qa_chain:
            followups = entry.get('followup_questions', [])
            if len(qa_chain) < len(followups):
                next_question = followups[len(qa_chain)]
        else:
            next_question = entry.get('question')
        if next_question:
            with st.container():
                st.markdown(f"**【{len(qa_chain)+1}問目】**")
                st.markdown(f"**Q.** {next_question}")
                with st.form(f"followup_form_{entry['id']}_{idx}_{len(qa_chain)}"):
                    followup_input = st.text_area(
                        "この質問についてどう思いましたか？",
                        height=100,
                        placeholder="ここに回答を書いてください...",
                        key=f"followup_{entry['id']}_{idx}_{len(qa_chain)}"
                    )
                    if st.form_submit_button("回答を保存", type="secondary"):
                        if followup_input.strip():
                            self._save_qa_chain(entry['id'], next_question, followup_input)
                            st.success("回答を保存しました！")
                            st.rerun()
                        else:
                            st.error("回答を入力してください。")

    def _render_analysis_summary(self, entry: Dict[str, Any]) -> str:
        # Pill UI用の色分け関数
        def pill(text, color):
            return f"<span style='display:inline-block;padding:2px 10px;margin:2px 4px 2px 0;border-radius:12px;background:{color};color:#fff;font-size:90%;'>{text}</span>"
        # 色リスト
        topic_color = "#4caf50"
        emotion_color = "#2196f3"
        thought_color = "#9c27b0"
        goal_color = "#ff9800"
        # 分析まとめHTML
        html = "<div style='padding:10px 0;'>"
        html += "<b>📌 トピック:</b> " + ''.join([pill(t, topic_color) for t in entry.get('topics', [])]) + "<br>"
        html += "<b>🎭 感情:</b> " + ''.join([pill(e, emotion_color) for e in entry.get('emotions', [])]) + "<br>"
        html += "<b>💭 思考:</b> " + ''.join([pill(t, thought_color) for t in entry.get('thoughts', [])]) + "<br>"
        html += "<b>🎯 目標:</b> " + ''.join([pill(g, goal_color) for g in entry.get('goals', [])]) + "<br>"
        html += f"<b>🧩 最終質問:</b> {entry.get('question', '')}"
        html += "</div>"
        return html

    def _reanalyze_entry(self, entry_id: str) -> None:
        # 再分析（LLMで再実行）
        user_id = st.session_state.get('user_id')
        all_data = self._get_user_diary_data(user_id)
        for entry in all_data:
            if entry.get('id') == entry_id:
                new_analysis = self.ai_analyzer.analyze_diary(entry['text'])
                # 更新データを準備
                updated_data = entry.copy()
                for k in ["topics", "emotions", "thoughts", "goals", "question", "followup_questions"]:
                    if k in new_analysis:
                        updated_data[k] = new_analysis[k]
                # SQLiteで更新
                self.diary_manager.update_diary_entry(entry_id, updated_data)
                break

    def _save_qa_chain(self, entry_id: str, question: str, answer: str) -> None:
        """追加入力を保存（SQLite対応）"""
        user_id = st.session_state.get('user_id')
        all_data = self._get_user_diary_data(user_id)
        for entry in all_data:
            if entry.get('id') == entry_id:
                # 新しいQ&Aを追加
                if 'qa_chain' not in entry:
                    entry['qa_chain'] = []
                entry['qa_chain'].append({
                    'question': question,
                    'answer': answer,
                    'created_at': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                # SQLiteで更新
                self.diary_manager.update_diary_entry(entry_id, entry)
                break
    
    def _update_entry_date(self, entry_id: str, new_date: str) -> None:
        """日記エントリの日付を更新（SQLite対応）"""
        all_data = self.diary_manager.get_all_diary_data()
        for entry in all_data:
            if entry.get('id') == entry_id:
                # 日付を更新
                entry['date'] = new_date
                # SQLiteで更新
                self.diary_manager.update_diary_entry(entry_id, entry)
                break
    

    
    def show_history(self) -> None:
        st.title("📚 履歴一覧")
        user_id = st.session_state.get('user_id')
        diary_data = self._get_user_diary_data(user_id)
        if diary_data:
            search_term = st.text_input("🔍 検索（日記の内容で検索）")
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("開始日", value=None)
            with col2:
                end_date = st.date_input("終了日", value=None)
            filtered_data = diary_data
            if search_term:
                filtered_data = [entry for entry in filtered_data if search_term.lower() in entry.get('text', '').lower()]
            if start_date and end_date:
                start_str = start_date.strftime("%Y-%m-%d")
                end_str = end_date.strftime("%Y-%m-%d")
                filtered_data = [entry for entry in filtered_data if start_str <= entry.get('date', '') <= end_str]
            st.write(f"**表示件数:** {len(filtered_data)}件")
            for idx, entry in enumerate(filtered_data):
                with st.expander(f"📅 {entry['date']} - {entry['text'][:50]}..."):
                    # 日記内容と日付編集
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**📖 日記内容:**")
                        st.write(entry['text'])
                    with col2:
                        # 現在の日付をdatetime.dateオブジェクトに変換
                        current_date = datetime.datetime.strptime(entry['date'], '%Y-%m-%d').date()
                        new_date = st.date_input(
                            "📅 日付変更",
                            value=current_date,
                            key=f"date_edit_{entry['id']}_{idx}",
                            help="日付を変更して保存ボタンを押してください"
                        )
                        if st.button("💾 保存", key=f"save_date_{entry['id']}_{idx}"):
                            if new_date != current_date:
                                self._update_entry_date(entry['id'], new_date.strftime('%Y-%m-%d'))
                                st.success("日付を更新しました！")
                                st.rerun()
                    
                    # 分析結果の表示
                    st.markdown("**🔍 分析結果:**")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**🧠 トピック:** {', '.join(entry['topics'])}")
                        st.write(f"**🎭 感情:** {', '.join(entry['emotions'])}")
                    with col2:
                        st.write(f"**💭 思考:** {', '.join(entry['thoughts'])}")
                        st.write(f"**🎯 目標:** {', '.join(entry['goals'])}")
                    
                    st.write(f"**🧩 最終質問:** {entry['question']}")
                    
                    # QAチェーンの表示
                    qa_chain = entry.get('qa_chain', [])
                    if qa_chain:
                        st.markdown("**💬 質問と回答:**")
                        for i, qa in enumerate(qa_chain):
                            with st.container():
                                st.markdown(f"""
                                <div style='margin:8px 0;padding:12px;border-radius:8px;background:#f7f7fa;border-left:4px solid #2196f3;'>
                                    <b>👤 Q{i+1}:</b> {qa['question']}<br>
                                    <b>🗨️ A{i+1}:</b> {qa['answer']}
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.info("まだ質問への回答がありません。")
                    
                    # 次の質問（未回答）の表示と回答入力
                    next_question = None
                    if qa_chain:
                        followups = entry.get('followup_questions', [])
                        if len(qa_chain) < len(followups):
                            next_question = followups[len(qa_chain)]
                    else:
                        next_question = entry.get('question')
                    
                    if next_question:
                        st.markdown("**📝 次の質問:**")
                        st.markdown(f"**Q{len(qa_chain)+1}:** {next_question}")
                        with st.form(f"history_followup_form_{entry['id']}_{idx}_{len(qa_chain)}"):
                            followup_input = st.text_area(
                                "この質問についてどう思いましたか？",
                                height=100,
                                placeholder="ここに回答を書いてください...",
                                key=f"history_followup_{entry['id']}_{idx}_{len(qa_chain)}"
                            )
                            if st.form_submit_button("回答を保存", type="secondary"):
                                if followup_input.strip():
                                    self._save_qa_chain(entry['id'], next_question, followup_input)
                                    st.success("回答を保存しました！")
                                    st.rerun()
                                else:
                                    st.error("回答を入力してください。")
                    
                    # 削除ボタン
                    if st.button(f"🗑️ 削除", key=f"delete_{entry['id']}_{idx}"):
                        if self.diary_manager.delete_diary_entry(entry['id']):
                            st.success("削除しました")
                            st.rerun()
        else:
            st.info("履歴がまだありません。")
    
    def show_stats(self) -> None:
        st.title("📊 統計情報")
        user_id = st.session_state.get('user_id')
        diary_data = self._get_user_diary_data(user_id)
        trends = self.ai_analyzer.analyze_trends(diary_data)
        if trends:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("総日記数", trends['total_entries'])
                st.write(f"**期間:** {trends['date_range']['start']} 〜 {trends['date_range']['end']}")
            with col2:
                st.write("**📈 よく書くトピック**")
                for topic, count in trends['top_topics']:
                    st.write(f"- {topic}: {count}回")
            st.write("**🎭 よく出てくる感情**")
            for emotion, count in trends['top_emotions']:
                st.write(f"- {emotion}: {count}回")
        else:
            st.info("統計データがありません。")
    
    def show_period_summary(self) -> None:
        """期間まとめ機能を表示"""
        st.title("📅 期間まとめ")
        st.markdown("指定した期間の日記データを構造化してまとめます。")
        
        # 期間選択
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "開始日",
                value=datetime.date.today() - datetime.timedelta(days=7),
                help="まとめたい期間の開始日を選択してください"
            )
        with col2:
            end_date = st.date_input(
                "終了日",
                value=datetime.date.today(),
                help="まとめたい期間の終了日を選択してください"
            )
        
        # 期間の検証
        if start_date > end_date:
            st.error("開始日は終了日より前の日付を選択してください。")
            return
        
        # 分析モード選択
        st.markdown("### 🔧 分析モード")
        analysis_mode = st.radio(
            "分析モードを選択してください",
            ["default", "kpt", "ywt", "custom"],
            format_func=lambda x: {
                "default": "📊 デフォルト分析",
                "kpt": "🎯 KPT分析",
                "ywt": "📝 YWT分析",
                "custom": "🎨 カスタム分析"
            }[x],
            help="デフォルト分析は構造化されたJSON形式、KPT分析はKeep/Problem/Try形式、YWT分析はやったこと/わかったこと/次やること形式、カスタム分析は自由な形式で出力します"
        )
        
        # カスタムプロンプト入力
        custom_prompt = ""
        if analysis_mode == "custom":
            st.markdown("### 📝 カスタムプロンプト")
            custom_prompt = st.text_area(
                "分析の指示を自由に記述してください",
                height=150,
                placeholder="例: この期間の感情の変化を時系列で分析し、最も印象的な出来事を3つ挙げてください。",
                help="AIにどのような分析をしてほしいか具体的に指示してください"
            )
            
            if not custom_prompt.strip():
                st.warning("カスタム分析を選択した場合は、プロンプトを入力してください。")
                return
        
        # 実行ボタン
        button_texts = {
            "default": "🚀 デフォルト分析を実行",
            "kpt": "🎯 KPT分析を実行",
            "ywt": "📝 YWT分析を実行",
            "custom": "🎨 カスタム分析を実行"
        }
        button_text = button_texts.get(analysis_mode, "🚀 分析を実行")
        if st.button(button_text, type="primary"):
            with st.spinner("期間データを分析中..."):
                # 期間データを取得
                start_str = start_date.strftime('%Y-%m-%d')
                end_str = end_date.strftime('%Y-%m-%d')
                
                user_id = st.session_state.get('user_id')
                all_data = self._get_user_diary_data(user_id)
                period_data = [
                    entry for entry in all_data 
                    if start_str <= entry.get('date', '') <= end_str
                ]
                
                if not period_data:
                    st.warning(f"{start_str} 〜 {end_str} の期間に日記データがありません。")
                    return
                
                # AIで期間分析を実行
                summary_result = self.period_analyzer.analyze_period_summary(
                    period_data, start_str, end_str, analysis_mode, custom_prompt
                )
                
                # 結果を表示
                self._display_period_summary(summary_result, period_data)
    
    def _display_period_summary(self, summary_result: Dict[str, Any], period_data: List[Dict[str, Any]]) -> None:
        """期間まとめ結果を表示"""
        st.success(f"✅ {len(period_data)}件の日記データを分析しました！")
        
        # 分析モードの表示
        mode = summary_result.get('mode', 'default')
        if mode == 'custom':
            st.markdown("## 🎨 カスタム分析結果")
            custom_result = summary_result.get('custom_result', '')
            if custom_result:
                st.markdown(custom_result)
            else:
                st.info("カスタム分析の結果がありません。")
        elif mode == 'kpt':
            # KPT分析結果の表示
            st.markdown("## 🎯 KPT分析結果")
            
            # 期間概要
            st.markdown("### 📋 期間概要")
            st.info(summary_result.get('summary', ''))
            
            # KPT分析結果
            kpt_analysis = summary_result.get('kpt_analysis', {})
            if kpt_analysis:
                # Keep
                st.markdown("### ✅ Keep（継続すべきこと）")
                keep_items = kpt_analysis.get('keep', [])
                if keep_items:
                    for i, keep in enumerate(keep_items, 1):
                        with st.container():
                            st.markdown(f"""
                            <div style='margin:8px 0;padding:12px;border-radius:8px;background:#e8f5e8;border-left:4px solid #4caf50;'>
                                <b>🎯 トピック {i}: {keep.get('topic', '')}</b><br>
                                <b>📝 項目:</b> {', '.join(keep.get('items', []))}<br>
                                <b>💡 理由:</b> {keep.get('reason', '')}
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("Keep項目が見つかりませんでした。")
                
                # Problem
                st.markdown("### ⚠️ Problem（改善すべき問題）")
                problem_items = kpt_analysis.get('problem', [])
                if problem_items:
                    for i, problem in enumerate(problem_items, 1):
                        with st.container():
                            st.markdown(f"""
                            <div style='margin:8px 0;padding:12px;border-radius:8px;background:#fff3e0;border-left:4px solid #ff9800;'>
                                <b>🎯 トピック {i}: {problem.get('topic', '')}</b><br>
                                <b>📝 項目:</b> {', '.join(problem.get('items', []))}<br>
                                <b>💡 影響:</b> {problem.get('impact', '')}
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("Problem項目が見つかりませんでした。")
                
                # Try
                st.markdown("### 🚀 Try（試してみたいこと）")
                try_items = kpt_analysis.get('try', [])
                if try_items:
                    for i, try_item in enumerate(try_items, 1):
                        with st.container():
                            st.markdown(f"""
                            <div style='margin:8px 0;padding:12px;border-radius:8px;background:#e3f2fd;border-left:4px solid #2196f3;'>
                                <b>🎯 トピック {i}: {try_item.get('topic', '')}</b><br>
                                <b>📝 項目:</b> {', '.join(try_item.get('items', []))}<br>
                                <b>💡 期待効果:</b> {try_item.get('expected_effect', '')}
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("Try項目が見つかりませんでした。")
            else:
                st.info("KPT分析結果がありません。")
            
            # 主要テーマ
            st.markdown("### 🎯 主要テーマ")
            key_themes = summary_result.get('key_themes', [])
            if key_themes:
                for i, theme in enumerate(key_themes, 1):
                    st.markdown(f"**{i}.** {theme}")
            else:
                st.info("主要テーマが見つかりませんでした。")
            
            # 推奨事項
            st.markdown("### 📝 推奨事項")
            recommendations = summary_result.get('recommendations', [])
            if recommendations:
                for i, rec in enumerate(recommendations, 1):
                    st.markdown(f"**{i}.** {rec}")
            else:
                st.info("推奨事項が見つかりませんでした。")
        elif mode == 'ywt':
            # YWT分析結果の表示
            st.markdown("## 📝 YWT分析結果")
            
            # 期間概要
            st.markdown("### 📋 期間概要")
            st.info(summary_result.get('summary', ''))
            
            # YWT分析結果
            ywt_analysis = summary_result.get('ywt_analysis', {})
            if ywt_analysis:
                # Yatta（やったこと）
                st.markdown("### ✅ Yatta（やったこと）")
                yatta_items = ywt_analysis.get('yatta', [])
                if yatta_items:
                    for i, yatta in enumerate(yatta_items, 1):
                        with st.container():
                            st.markdown(f"""
                            <div style='margin:8px 0;padding:12px;border-radius:8px;background:#e8f5e8;border-left:4px solid #4caf50;'>
                                <b>🎯 トピック {i}: {yatta.get('topic', '')}</b><br>
                                <b>📝 項目:</b> {', '.join(yatta.get('items', []))}<br>
                                <b>💡 背景:</b> {yatta.get('context', '')}
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("Yatta項目が見つかりませんでした。")
                
                # Wakatta（わかったこと）
                st.markdown("### 💡 Wakatta（わかったこと）")
                wakatta_items = ywt_analysis.get('wakatta', [])
                if wakatta_items:
                    for i, wakatta in enumerate(wakatta_items, 1):
                        with st.container():
                            st.markdown(f"""
                            <div style='margin:8px 0;padding:12px;border-radius:8px;background:#fff3e0;border-left:4px solid #ff9800;'>
                                <b>🎯 トピック {i}: {wakatta.get('topic', '')}</b><br>
                                <b>📝 項目:</b> {', '.join(wakatta.get('items', []))}<br>
                                <b>💡 発見:</b> {wakatta.get('insight', '')}
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("Wakatta項目が見つかりませんでした。")
                
                # Tsugi（次やること）
                st.markdown("### 🚀 Tsugi（次やること）")
                tsugi_items = ywt_analysis.get('tsugi', [])
                if tsugi_items:
                    for i, tsugi in enumerate(tsugi_items, 1):
                        with st.container():
                            st.markdown(f"""
                            <div style='margin:8px 0;padding:12px;border-radius:8px;background:#e3f2fd;border-left:4px solid #2196f3;'>
                                <b>🎯 トピック {i}: {tsugi.get('topic', '')}</b><br>
                                <b>📝 項目:</b> {', '.join(tsugi.get('items', []))}<br>
                                <b>💡 理由:</b> {tsugi.get('reason', '')}
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("Tsugi項目が見つかりませんでした。")
            else:
                st.info("YWT分析結果がありません。")
            
            # 主要テーマ
            st.markdown("### 🎯 主要テーマ")
            key_themes = summary_result.get('key_themes', [])
            if key_themes:
                for i, theme in enumerate(key_themes, 1):
                    st.markdown(f"**{i}.** {theme}")
            else:
                st.info("主要テーマが見つかりませんでした。")
            
            # 推奨事項
            st.markdown("### 📝 推奨事項")
            recommendations = summary_result.get('recommendations', [])
            if recommendations:
                for i, rec in enumerate(recommendations, 1):
                    st.markdown(f"**{i}.** {rec}")
            else:
                st.info("推奨事項が見つかりませんでした。")
        else:
            # デフォルト分析結果の表示
            st.markdown("## 📊 デフォルト分析結果")
            
            # 期間概要
            st.markdown("### 📋 期間概要")
            st.info(summary_result.get('summary', ''))
            
            # 主要テーマ
            st.markdown("### 🎯 主要テーマ")
            key_themes = summary_result.get('key_themes', [])
            if key_themes:
                for i, theme in enumerate(key_themes, 1):
                    st.markdown(f"**{i}.** {theme}")
            else:
                st.info("主要テーマが見つかりませんでした。")
            
            # 感情の軌跡
            st.markdown("### 🎭 感情の軌跡")
            emotional_journey = summary_result.get('emotional_journey', [])
            if emotional_journey:
                for journey in emotional_journey:
                    st.markdown(f"""
                    **📅 {journey.get('date', '')}** - {journey.get('emotion', '')}
                    *{journey.get('context', '')}*
                    """)
            else:
                st.info("感情の軌跡データがありません。")
            
            # 洞察
            st.markdown("### 💡 洞察")
            insights = summary_result.get('insights', [])
            if insights:
                for i, insight in enumerate(insights, 1):
                    st.markdown(f"**{i}.** {insight}")
            else:
                st.info("洞察が見つかりませんでした。")
            
            # 成長領域
            st.markdown("### 🌱 成長領域")
            growth_areas = summary_result.get('growth_areas', [])
            if growth_areas:
                for i, area in enumerate(growth_areas, 1):
                    st.markdown(f"**{i}.** {area}")
            else:
                st.info("成長領域が見つかりませんでした。")
            
            # 推奨事項
            st.markdown("### 📝 推奨事項")
            recommendations = summary_result.get('recommendations', [])
            if recommendations:
                for i, rec in enumerate(recommendations, 1):
                    st.markdown(f"**{i}.** {rec}")
            else:
                st.info("推奨事項が見つかりませんでした。")
        
        # 元データの表示（折りたたみ）
        with st.expander("📊 元データ詳細", expanded=False):
            st.markdown(f"**期間:** {summary_result.get('period', '')}")
            st.markdown(f"**分析対象:** {len(period_data)}件の日記")
            
            for entry in period_data:
                with st.expander(f"📅 {entry['date']} - {entry['text'][:50]}...", expanded=False):
                    st.write(f"**内容:** {entry['text']}")
                    st.write(f"**トピック:** {', '.join(entry.get('topics', []))}")
                    st.write(f"**感情:** {', '.join(entry.get('emotions', []))}")
                    
                    # QAチェーン
                    qa_chain = entry.get('qa_chain', [])
                    if qa_chain:
                        st.markdown("**💬 質問と回答:**")
                        for i, qa in enumerate(qa_chain):
                            st.markdown(f"**Q{i+1}:** {qa['question']}")
                            st.markdown(f"**A{i+1}:** {qa['answer']}")
        
        # エクスポート機能
        st.markdown("## 💾 エクスポート")
        
        # デバッグ情報を表示
        st.info(f"分析結果のモード: {summary_result.get('mode', 'unknown')}")
        st.info(f"期間データ数: {len(period_data)}")
        
        if st.button("📄 まとめをテキストファイルとしてダウンロード"):
            try:
                # エクスポートテキストを生成
                export_text = self.period_analyzer.create_export_text(summary_result, period_data)
                
                # デバッグ情報
                st.success(f"エクスポートテキスト生成完了: {len(export_text)} 文字")
                
                # ファイル名を生成
                period_str = summary_result.get('period', 'unknown_period')
                safe_period = period_str.replace(' 〜 ', '_to_').replace(' ', '_')
                file_name = f"diary_summary_{safe_period}.txt"
                
                st.info(f"ファイル名: {file_name}")
                
                # ダウンロードボタンを表示
                st.download_button(
                    label="📥 ダウンロード",
                    data=export_text,
                    file_name=file_name,
                    mime="text/plain",
                    help="クリックしてテキストファイルをダウンロード"
                )
                
                # プレビューを表示
                with st.expander("📄 エクスポート内容プレビュー", expanded=False):
                    st.text_area("エクスポート内容", export_text[:1000] + "..." if len(export_text) > 1000 else export_text, height=300)
                    
            except Exception as e:
                st.error(f"エクスポートエラー: {str(e)}")
                st.exception(e)
    
 