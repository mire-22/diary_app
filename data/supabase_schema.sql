-- Supabase用SQLダンプ
-- 生成日時: 2025-07-21 14:20:01
-- 元ファイル: data/diary_normalized.db

BEGIN;

-- diary_entriesテーブル
DROP TABLE IF EXISTS diary_entries CASCADE;
CREATE TABLE diary_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    date DATE NOT NULL,
    text TEXT NOT NULL,
    question TEXT,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE
);

-- emotionsテーブル
DROP TABLE IF EXISTS emotions CASCADE;
CREATE TABLE emotions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    diary_entry_id UUID REFERENCES diary_entries(id) ON DELETE CASCADE,
    emotion TEXT NOT NULL,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE
);

-- topicsテーブル
DROP TABLE IF EXISTS topics CASCADE;
CREATE TABLE topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    diary_entry_id UUID REFERENCES diary_entries(id) ON DELETE CASCADE,
    topic TEXT NOT NULL,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE
);

-- thoughtsテーブル
DROP TABLE IF EXISTS thoughts CASCADE;
CREATE TABLE thoughts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    diary_entry_id UUID REFERENCES diary_entries(id) ON DELETE CASCADE,
    thought TEXT NOT NULL,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE
);

-- goalsテーブル
DROP TABLE IF EXISTS goals CASCADE;
CREATE TABLE goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    diary_entry_id UUID REFERENCES diary_entries(id) ON DELETE CASCADE,
    goal TEXT NOT NULL,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE
);

-- qa_chainテーブル
DROP TABLE IF EXISTS qa_chain CASCADE;
CREATE TABLE qa_chain (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    diary_entry_id UUID REFERENCES diary_entries(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE
);

-- followup_questionsテーブル
DROP TABLE IF EXISTS followup_questions CASCADE;
CREATE TABLE followup_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    diary_entry_id UUID REFERENCES diary_entries(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE
);

-- followupsテーブル
DROP TABLE IF EXISTS followups CASCADE;
CREATE TABLE followups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    diary_entry_id UUID REFERENCES diary_entries(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE
);

-- インデックス
CREATE INDEX idx_diary_date ON diary_entries(date);
CREATE INDEX idx_diary_created_at ON diary_entries(created_at);
CREATE INDEX idx_diary_user_id ON diary_entries(user_id);
CREATE INDEX idx_topics_diary_id ON topics(diary_entry_id);
CREATE INDEX idx_topics_user_id ON topics(user_id);
CREATE INDEX idx_emotions_diary_id ON emotions(diary_entry_id);
CREATE INDEX idx_emotions_user_id ON emotions(user_id);
CREATE INDEX idx_thoughts_diary_id ON thoughts(diary_entry_id);
CREATE INDEX idx_thoughts_user_id ON thoughts(user_id);
CREATE INDEX idx_goals_diary_id ON goals(diary_entry_id);
CREATE INDEX idx_goals_user_id ON goals(user_id);
CREATE INDEX idx_qa_chain_diary_id ON qa_chain(diary_entry_id);
CREATE INDEX idx_qa_chain_user_id ON qa_chain(user_id);
CREATE INDEX idx_followup_questions_diary_id ON followup_questions(diary_entry_id);
CREATE INDEX idx_followup_questions_user_id ON followup_questions(user_id);
CREATE INDEX idx_followups_diary_id ON followups(diary_entry_id);
CREATE INDEX idx_followups_user_id ON followups(user_id);

-- RLSポリシー
ALTER TABLE diary_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE emotions ENABLE ROW LEVEL SECURITY;
ALTER TABLE topics ENABLE ROW LEVEL SECURITY;
ALTER TABLE thoughts ENABLE ROW LEVEL SECURITY;
ALTER TABLE goals ENABLE ROW LEVEL SECURITY;
ALTER TABLE qa_chain ENABLE ROW LEVEL SECURITY;
ALTER TABLE followup_questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE followups ENABLE ROW LEVEL SECURITY;

-- diary_entries RLSポリシー
CREATE POLICY "Users can view own diary entries" ON diary_entries
    FOR SELECT TO authenticated USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own diary entries" ON diary_entries
    FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own diary entries" ON diary_entries
    FOR UPDATE TO authenticated USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own diary entries" ON diary_entries
    FOR DELETE TO authenticated USING (auth.uid() = user_id);

-- emotions RLSポリシー
CREATE POLICY "Users can view own emotions" ON emotions
    FOR SELECT TO authenticated USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own emotions" ON emotions
    FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own emotions" ON emotions
    FOR UPDATE TO authenticated USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own emotions" ON emotions
    FOR DELETE TO authenticated USING (auth.uid() = user_id);

-- topics RLSポリシー
CREATE POLICY "Users can view own topics" ON topics
    FOR SELECT TO authenticated USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own topics" ON topics
    FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own topics" ON topics
    FOR UPDATE TO authenticated USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own topics" ON topics
    FOR DELETE TO authenticated USING (auth.uid() = user_id);

-- thoughts RLSポリシー
CREATE POLICY "Users can view own thoughts" ON thoughts
    FOR SELECT TO authenticated USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own thoughts" ON thoughts
    FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own thoughts" ON thoughts
    FOR UPDATE TO authenticated USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own thoughts" ON thoughts
    FOR DELETE TO authenticated USING (auth.uid() = user_id);

-- goals RLSポリシー
CREATE POLICY "Users can view own goals" ON goals
    FOR SELECT TO authenticated USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own goals" ON goals
    FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own goals" ON goals
    FOR UPDATE TO authenticated USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own goals" ON goals
    FOR DELETE TO authenticated USING (auth.uid() = user_id);

-- qa_chain RLSポリシー
CREATE POLICY "Users can view own qa_chain" ON qa_chain
    FOR SELECT TO authenticated USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own qa_chain" ON qa_chain
    FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own qa_chain" ON qa_chain
    FOR UPDATE TO authenticated USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own qa_chain" ON qa_chain
    FOR DELETE TO authenticated USING (auth.uid() = user_id);

-- followup_questions RLSポリシー
CREATE POLICY "Users can view own followup_questions" ON followup_questions
    FOR SELECT TO authenticated USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own followup_questions" ON followup_questions
    FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own followup_questions" ON followup_questions
    FOR UPDATE TO authenticated USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own followup_questions" ON followup_questions
    FOR DELETE TO authenticated USING (auth.uid() = user_id);

-- followups RLSポリシー
CREATE POLICY "Users can view own followups" ON followups
    FOR SELECT TO authenticated USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own followups" ON followups
    FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own followups" ON followups
    FOR UPDATE TO authenticated USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own followups" ON followups
    FOR DELETE TO authenticated USING (auth.uid() = user_id);

-- データ移行用関数（セキュリティ強化版）
CREATE OR REPLACE FUNCTION public.migrate_user_data(old_user_id TEXT, new_user_id UUID)
RETURNS VOID AS $$
BEGIN
    -- 既存のデータを新しいユーザーIDに更新
    UPDATE public.diary_entries SET user_id = new_user_id WHERE user_id = old_user_id;
    UPDATE public.emotions SET user_id = new_user_id WHERE user_id = old_user_id;
    UPDATE public.topics SET user_id = new_user_id WHERE user_id = old_user_id;
    UPDATE public.thoughts SET user_id = new_user_id WHERE user_id = old_user_id;
    UPDATE public.goals SET user_id = new_user_id WHERE user_id = old_user_id;
    UPDATE public.qa_chain SET user_id = new_user_id WHERE user_id = old_user_id;
    UPDATE public.followup_questions SET user_id = new_user_id WHERE user_id = old_user_id;
    UPDATE public.followups SET user_id = new_user_id WHERE user_id = old_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMIT;

-- 使用例:
-- 1. このSQLファイルをSupabaseのSQL Editorで実行
-- 2. ユーザー登録後、以下のコマンドでデータを移行:
-- SELECT public.migrate_user_data('e777441d-336e-45e0-a11c-d84eb3b0e3b2', auth.uid());
-- 3. 移行完了後、関数を削除:
-- DROP FUNCTION public.migrate_user_data(TEXT, UUID);
