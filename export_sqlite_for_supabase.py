#!/usr/bin/env python3
"""
SQLiteからSupabase用のSQLダンプを生成するスクリプト
- UUID型のuser_idカラムを追加
- RLS対応のスキーマに変換
- データ型をSupabaseに最適化
"""

import sqlite3
import os
from datetime import datetime

def export_sqlite_for_supabase(db_path, output_path):
    """SQLiteデータベースをSupabase用のSQLダンプに変換"""
    
    if not os.path.exists(db_path):
        print(f"エラー: データベースファイルが見つかりません: {db_path}")
        return False
    
    try:
        # SQLiteデータベースに接続
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        # 出力ファイルを開く
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("-- Supabase用SQLダンプ\n")
            f.write(f"-- 生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("-- 元ファイル: " + db_path + "\n\n")
            
            # トランザクション開始
            f.write("BEGIN;\n\n")
            
            # 1. diary_entriesテーブル（user_idをUUID型に変更）
            f.write("-- diary_entriesテーブル\n")
            f.write("DROP TABLE IF EXISTS diary_entries CASCADE;\n")
            f.write("CREATE TABLE diary_entries (\n")
            f.write("    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),\n")
            f.write("    original_id TEXT,\n")
            f.write("    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),\n")
            f.write("    date DATE NOT NULL,\n")
            f.write("    text TEXT NOT NULL,\n")
            f.write("    question TEXT,\n")
            f.write("    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE\n")
            f.write(");\n\n")
            
            # 2. emotionsテーブル（user_idを追加）
            f.write("-- emotionsテーブル\n")
            f.write("DROP TABLE IF EXISTS emotions CASCADE;\n")
            f.write("CREATE TABLE emotions (\n")
            f.write("    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),\n")
            f.write("    diary_entry_id UUID REFERENCES diary_entries(id) ON DELETE CASCADE,\n")
            f.write("    emotion TEXT NOT NULL,\n")
            f.write("    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE\n")
            f.write(");\n\n")
            
            # 3. topicsテーブル（user_idを追加）
            f.write("-- topicsテーブル\n")
            f.write("DROP TABLE IF EXISTS topics CASCADE;\n")
            f.write("CREATE TABLE topics (\n")
            f.write("    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),\n")
            f.write("    diary_entry_id UUID REFERENCES diary_entries(id) ON DELETE CASCADE,\n")
            f.write("    topic TEXT NOT NULL,\n")
            f.write("    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE\n")
            f.write(");\n\n")
            
            # 4. thoughtsテーブル（user_idを追加）
            f.write("-- thoughtsテーブル\n")
            f.write("DROP TABLE IF EXISTS thoughts CASCADE;\n")
            f.write("CREATE TABLE thoughts (\n")
            f.write("    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),\n")
            f.write("    diary_entry_id UUID REFERENCES diary_entries(id) ON DELETE CASCADE,\n")
            f.write("    thought TEXT NOT NULL,\n")
            f.write("    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE\n")
            f.write(");\n\n")
            
            # 5. goalsテーブル（user_idを追加）
            f.write("-- goalsテーブル\n")
            f.write("DROP TABLE IF EXISTS goals CASCADE;\n")
            f.write("CREATE TABLE goals (\n")
            f.write("    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),\n")
            f.write("    diary_entry_id UUID REFERENCES diary_entries(id) ON DELETE CASCADE,\n")
            f.write("    goal TEXT NOT NULL,\n")
            f.write("    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE\n")
            f.write(");\n\n")
            
            # 6. qa_chainテーブル（user_idを追加）
            f.write("-- qa_chainテーブル\n")
            f.write("DROP TABLE IF EXISTS qa_chain CASCADE;\n")
            f.write("CREATE TABLE qa_chain (\n")
            f.write("    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),\n")
            f.write("    diary_entry_id UUID REFERENCES diary_entries(id) ON DELETE CASCADE,\n")
            f.write("    question TEXT NOT NULL,\n")
            f.write("    answer TEXT NOT NULL,\n")
            f.write("    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE\n")
            f.write(");\n\n")
            
            # 7. followup_questionsテーブル（user_idを追加）
            f.write("-- followup_questionsテーブル\n")
            f.write("DROP TABLE IF EXISTS followup_questions CASCADE;\n")
            f.write("CREATE TABLE followup_questions (\n")
            f.write("    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),\n")
            f.write("    diary_entry_id UUID REFERENCES diary_entries(id) ON DELETE CASCADE,\n")
            f.write("    question TEXT NOT NULL,\n")
            f.write("    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE\n")
            f.write(");\n\n")
            
            # 8. followupsテーブル（user_idを追加）
            f.write("-- followupsテーブル\n")
            f.write("DROP TABLE IF EXISTS followups CASCADE;\n")
            f.write("CREATE TABLE followups (\n")
            f.write("    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),\n")
            f.write("    diary_entry_id UUID REFERENCES diary_entries(id) ON DELETE CASCADE,\n")
            f.write("    text TEXT NOT NULL,\n")
            f.write("    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE\n")
            f.write(");\n\n")
            
            # インデックス作成
            f.write("-- インデックス\n")
            f.write("CREATE INDEX idx_diary_date ON diary_entries(date);\n")
            f.write("CREATE INDEX idx_diary_created_at ON diary_entries(created_at);\n")
            f.write("CREATE INDEX idx_diary_user_id ON diary_entries(user_id);\n")
            f.write("CREATE INDEX idx_topics_diary_id ON topics(diary_entry_id);\n")
            f.write("CREATE INDEX idx_topics_user_id ON topics(user_id);\n")
            f.write("CREATE INDEX idx_emotions_diary_id ON emotions(diary_entry_id);\n")
            f.write("CREATE INDEX idx_emotions_user_id ON emotions(user_id);\n")
            f.write("CREATE INDEX idx_thoughts_diary_id ON thoughts(diary_entry_id);\n")
            f.write("CREATE INDEX idx_thoughts_user_id ON thoughts(user_id);\n")
            f.write("CREATE INDEX idx_goals_diary_id ON goals(diary_entry_id);\n")
            f.write("CREATE INDEX idx_goals_user_id ON goals(user_id);\n")
            f.write("CREATE INDEX idx_qa_chain_diary_id ON qa_chain(diary_entry_id);\n")
            f.write("CREATE INDEX idx_qa_chain_user_id ON qa_chain(user_id);\n")
            f.write("CREATE INDEX idx_followup_questions_diary_id ON followup_questions(diary_entry_id);\n")
            f.write("CREATE INDEX idx_followup_questions_user_id ON followup_questions(user_id);\n")
            f.write("CREATE INDEX idx_followups_diary_id ON followups(diary_entry_id);\n")
            f.write("CREATE INDEX idx_followups_user_id ON followups(user_id);\n\n")
            
            # RLSポリシー
            f.write("-- RLSポリシー\n")
            f.write("ALTER TABLE diary_entries ENABLE ROW LEVEL SECURITY;\n")
            f.write("ALTER TABLE emotions ENABLE ROW LEVEL SECURITY;\n")
            f.write("ALTER TABLE topics ENABLE ROW LEVEL SECURITY;\n")
            f.write("ALTER TABLE thoughts ENABLE ROW LEVEL SECURITY;\n")
            f.write("ALTER TABLE goals ENABLE ROW LEVEL SECURITY;\n")
            f.write("ALTER TABLE qa_chain ENABLE ROW LEVEL SECURITY;\n")
            f.write("ALTER TABLE followup_questions ENABLE ROW LEVEL SECURITY;\n")
            f.write("ALTER TABLE followups ENABLE ROW LEVEL SECURITY;\n\n")
            
            # diary_entriesのポリシー
            f.write("-- diary_entries RLSポリシー\n")
            f.write("CREATE POLICY \"Users can view own diary entries\" ON diary_entries\n")
            f.write("    FOR SELECT TO authenticated USING (auth.uid() = user_id);\n\n")
            f.write("CREATE POLICY \"Users can insert own diary entries\" ON diary_entries\n")
            f.write("    FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);\n\n")
            f.write("CREATE POLICY \"Users can update own diary entries\" ON diary_entries\n")
            f.write("    FOR UPDATE TO authenticated USING (auth.uid() = user_id);\n\n")
            f.write("CREATE POLICY \"Users can delete own diary entries\" ON diary_entries\n")
            f.write("    FOR DELETE TO authenticated USING (auth.uid() = user_id);\n\n")
            
            # 他のテーブルのポリシー（共通）
            tables = ['emotions', 'topics', 'thoughts', 'goals', 'qa_chain', 'followup_questions', 'followups']
            for table in tables:
                f.write(f"-- {table} RLSポリシー\n")
                f.write(f"CREATE POLICY \"Users can view own {table}\" ON {table}\n")
                f.write(f"    FOR SELECT TO authenticated USING (auth.uid() = user_id);\n\n")
                f.write(f"CREATE POLICY \"Users can insert own {table}\" ON {table}\n")
                f.write(f"    FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);\n\n")
                f.write(f"CREATE POLICY \"Users can update own {table}\" ON {table}\n")
                f.write(f"    FOR UPDATE TO authenticated USING (auth.uid() = user_id);\n\n")
                f.write(f"CREATE POLICY \"Users can delete own {table}\" ON {table}\n")
                f.write(f"    FOR DELETE TO authenticated USING (auth.uid() = user_id);\n\n")
            
            # データ移行のための関数（セキュリティ強化版）
            f.write("-- データ移行用関数（セキュリティ強化版）\n")
            f.write("CREATE OR REPLACE FUNCTION public.migrate_user_data(old_user_id TEXT, new_user_id UUID)\n")
            f.write("RETURNS VOID AS $$\n")
            f.write("BEGIN\n")
            f.write("    -- 既存のデータを新しいユーザーIDに更新\n")
            f.write("    UPDATE public.diary_entries SET user_id = new_user_id WHERE user_id = old_user_id;\n")
            f.write("    UPDATE public.emotions SET user_id = new_user_id WHERE user_id = old_user_id;\n")
            f.write("    UPDATE public.topics SET user_id = new_user_id WHERE user_id = old_user_id;\n")
            f.write("    UPDATE public.thoughts SET user_id = new_user_id WHERE user_id = old_user_id;\n")
            f.write("    UPDATE public.goals SET user_id = new_user_id WHERE user_id = old_user_id;\n")
            f.write("    UPDATE public.qa_chain SET user_id = new_user_id WHERE user_id = old_user_id;\n")
            f.write("    UPDATE public.followup_questions SET user_id = new_user_id WHERE user_id = old_user_id;\n")
            f.write("    UPDATE public.followups SET user_id = new_user_id WHERE user_id = old_user_id;\n")
            f.write("END;\n")
            f.write("$$ LANGUAGE plpgsql SECURITY DEFINER;\n\n")
            
            # トランザクション終了
            f.write("COMMIT;\n\n")
            
            # 使用例
            f.write("-- 使用例:\n")
            f.write("-- 1. このSQLファイルをSupabaseのSQL Editorで実行\n")
            f.write("-- 2. ユーザー登録後、以下のコマンドでデータを移行:\n")
            f.write("-- SELECT public.migrate_user_data('e777441d-336e-45e0-a11c-d84eb3b0e3b2', auth.uid());\n")
            f.write("-- 3. 移行完了後、関数を削除:\n")
            f.write("-- DROP FUNCTION public.migrate_user_data(TEXT, UUID);\n")
        
        print(f"✅ Supabase用SQLダンプが正常に作成されました: {output_path}")
        print(f"📊 ファイルサイズ: {os.path.getsize(output_path):,} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    # 設定
    db_path = "data/diary_normalized.db"
    output_path = "data/supabase_schema.sql"
    
    print("🚀 Supabase用SQLダンプ生成を開始...")
    print(f"📁 入力ファイル: {db_path}")
    print(f"📁 出力ファイル: {output_path}")
    print("-" * 50)
    
    success = export_sqlite_for_supabase(db_path, output_path)
    
    if success:
        print("\n🎉 完了！")
        print("\n📋 次のステップ:")
        print("1. Supabaseダッシュボードにアクセス")
        print("2. SQL Editorを開く")
        print("3. 生成されたSQLファイルの内容をコピー&ペースト")
        print("4. 実行ボタンをクリック")
        print("5. ユーザー登録後、データ移行関数を実行")
    else:
        print("\n❌ 処理が失敗しました") 