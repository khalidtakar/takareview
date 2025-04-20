-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create user table if it doesn't exist
CREATE TABLE IF NOT EXISTS "user" (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    subscription_type VARCHAR(50) DEFAULT 'basic',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    profile_picture TEXT,
    bio TEXT
);

-- Create tweet_analysis table if it doesn't exist
CREATE TABLE IF NOT EXISTS tweet_analysis (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES "user"(id),
    tweet_text TEXT NOT NULL,
    sentiment VARCHAR(50),
    confidence DECIMAL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indices for better performance
CREATE INDEX IF NOT EXISTS idx_user_email ON "user"(email);
CREATE INDEX IF NOT EXISTS idx_user_username ON "user"(username);
CREATE INDEX IF NOT EXISTS idx_tweet_analysis_user_id ON tweet_analysis(user_id);
CREATE INDEX IF NOT EXISTS idx_tweet_analysis_created_at ON tweet_analysis(created_at);

-- Enable RLS
ALTER TABLE "user" ENABLE ROW LEVEL SECURITY;
ALTER TABLE tweet_analysis ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS user_select_own ON "user";
DROP POLICY IF EXISTS user_update_own ON "user";
DROP POLICY IF EXISTS tweet_analysis_select_own ON tweet_analysis;
DROP POLICY IF EXISTS tweet_analysis_insert_own ON tweet_analysis;
DROP POLICY IF EXISTS tweet_analysis_update_own ON tweet_analysis;
DROP POLICY IF EXISTS tweet_analysis_delete_own ON tweet_analysis;

-- Create policies for user table
CREATE POLICY user_select_own ON "user"
    FOR SELECT
    USING (id::text = auth.uid()::text);

CREATE POLICY user_update_own ON "user"
    FOR UPDATE
    USING (id::text = auth.uid()::text);

-- Create policies for tweet_analysis table
CREATE POLICY tweet_analysis_select_own ON tweet_analysis
    FOR SELECT
    USING (user_id::text = auth.uid()::text);

CREATE POLICY tweet_analysis_insert_own ON tweet_analysis
    FOR INSERT
    WITH CHECK (user_id::text = auth.uid()::text);

CREATE POLICY tweet_analysis_update_own ON tweet_analysis
    FOR UPDATE
    USING (user_id::text = auth.uid()::text);

CREATE POLICY tweet_analysis_delete_own ON tweet_analysis
    FOR DELETE
    USING (user_id::text = auth.uid()::text); 