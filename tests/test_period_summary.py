import datetime
from src.diary_manager_sqlite import DiaryManagerSQLite
from src.ai_analyzer import AIAnalyzer
from src.period_analyzer import PeriodAnalyzer

def test_period_summary():
    """期間まとめ機能をテスト"""
    print("=== 期間まとめ機能テスト ===")
    
    # インスタンス作成
    diary_manager = DiaryManagerSQLite()
    ai_analyzer = AIAnalyzer()
    period_analyzer = PeriodAnalyzer(ai_analyzer)
    
    # 全データを取得
    all_data = diary_manager.get_all_diary_data()
    print(f"総エントリ数: {len(all_data)}")
    
    if all_data:
        # 最新の日付を取得
        latest_date = max(entry.get('date', '') for entry in all_data)
        # 1週間前の日付を計算
        latest_dt = datetime.datetime.strptime(latest_date, '%Y-%m-%d')
        week_ago_dt = latest_dt - datetime.timedelta(days=7)
        week_ago_date = week_ago_dt.strftime('%Y-%m-%d')
        
        print(f"テスト期間: {week_ago_date} 〜 {latest_date}")
        
        # 期間データを取得
        period_data = [
            entry for entry in all_data 
            if week_ago_date <= entry.get('date', '') <= latest_date
        ]
        
        print(f"期間内エントリ数: {len(period_data)}")
        
        if period_data:
            # 期間分析を実行
            print("\n期間分析を実行中...")
            summary_result = period_analyzer.analyze_period_summary(
                period_data, week_ago_date, latest_date
            )
            
            # 結果を表示
            print("\n=== 分析結果 ===")
            print(f"期間: {summary_result.get('period', '')}")
            print(f"概要: {summary_result.get('summary', '')}")
            
            print("\n主要テーマ:")
            for theme in summary_result.get('key_themes', []):
                print(f"- {theme}")
            
            print("\n洞察:")
            for insight in summary_result.get('insights', []):
                print(f"- {insight}")
            
            print("\n推奨事項:")
            for rec in summary_result.get('recommendations', []):
                print(f"- {rec}")
            
            # 週次トレンド分析のテスト
            print("\n=== 週次トレンド分析 ===")
            weekly_result = period_analyzer.analyze_weekly_trends(period_data)
            print(f"週次分析: {weekly_result.get('summary', '')}")
            
            # エクスポートテキストのテスト
            print("\n=== エクスポートテキスト ===")
            export_text = period_analyzer.create_export_text(summary_result, period_data)
            print(export_text[:500] + "..." if len(export_text) > 500 else export_text)
            
        else:
            print("指定期間にデータがありません。")
    else:
        print("データがありません。")

if __name__ == '__main__':
    test_period_summary() 