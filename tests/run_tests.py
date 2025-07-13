#!/usr/bin/env python3
"""
テスト実行スクリプト
DiaryManagerSQLiteクラスの単体テストを実行します
"""

import unittest
import sys
import os

# プロジェクトのルートディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_tests():
    """テストを実行"""
    print("=== DiaryManagerSQLite 単体テスト実行 ===")
    print()
    
    # テストディレクトリを指定
    test_dir = 'tests'
    
    # テストディスカバリーを実行
    loader = unittest.TestLoader()
    suite = loader.discover(test_dir, pattern='test_*.py')
    
    # テストランナーを作成
    runner = unittest.TextTestRunner(verbosity=2)
    
    # テストを実行
    result = runner.run(suite)
    
    # 結果を表示
    print("\n" + "="*50)
    print("テスト実行結果:")
    print(f"実行したテスト数: {result.testsRun}")
    print(f"失敗したテスト数: {len(result.failures)}")
    print(f"エラーが発生したテスト数: {len(result.errors)}")
    
    if result.failures:
        print("\n失敗したテスト:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nエラーが発生したテスト:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    # 終了コードを設定
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    exit_code = run_tests()
    sys.exit(exit_code) 