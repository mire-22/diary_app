import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.diary_manager_sqlite import DiaryManagerSQLite
from src.period_analyzer import PeriodAnalyzer
import datetime

def test_export_functionality():
    """エクスポート機能をテスト"""
    print("=== エクスポート機能テスト ===")
    
    try:
        # インスタンス作成
        diary_manager = DiaryManagerSQLite()
        period_analyzer = PeriodAnalyzer()
        
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
                # モック分析結果を作成
                summary_result = {
                    "period": f"{week_ago_date} 〜 {latest_date}",
                    "mode": "default",
                    "summary": f"この期間は{len(period_data)}件の日記があり、様々な出来事や感情の変化が記録されました。",
                    "key_themes": ["自己成長", "人間関係", "目標設定"],
                    "emotional_journey": [
                        {"date": week_ago_date, "emotion": "期待", "context": "新しい期間の開始"},
                        {"date": latest_date, "emotion": "達成感", "context": "期間の振り返り"}
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
                
                # エクスポートテキストを生成
                print("\n=== エクスポートテキスト生成 ===")
                export_text = period_analyzer.create_export_text(summary_result, period_data)
                
                print(f"エクスポートテキストの長さ: {len(export_text)} 文字")
                print("\n=== エクスポートテキスト（最初の500文字） ===")
                print(export_text[:500])
                
                # ファイルに保存してテスト
                test_filename = f"test_export_{week_ago_date}_to_{latest_date}.txt"
                with open(test_filename, 'w', encoding='utf-8') as f:
                    f.write(export_text)
                
                print(f"\n✅ エクスポートテキストを {test_filename} に保存しました")
                print(f"ファイルサイズ: {os.path.getsize(test_filename)} バイト")
                
                # ファイルの内容を確認
                print(f"\n=== 保存されたファイルの内容確認 ===")
                with open(test_filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"ファイル内容の長さ: {len(content)} 文字")
                    print("ファイルの最初の200文字:")
                    print(content[:200])
                
            else:
                print("指定期間にデータがありません。")
        else:
            print("データがありません。")
            
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_export_functionality() 