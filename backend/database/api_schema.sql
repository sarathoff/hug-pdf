-- API Keys and Usage Tracking Schema
-- Run this in your Supabase SQL editor

-- API Keys table
-- Note: user_id can be any UUID, doesn't need to reference auth.users for API testing
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    key_prefix VARCHAR(50) NOT NULL,
    tier VARCHAR(50) DEFAULT 'free' CHECK (tier IN ('free', 'pro', 'enterprise')),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used_at TIMESTAMP WITH TIME ZONE,
    requests_count INTEGER DEFAULT 0,
    requests_limit INTEGER DEFAULT 1000
);

-- API Usage tracking table
CREATE TABLE IF NOT EXISTS api_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    api_key_id UUID NOT NULL REFERENCES api_keys(id) ON DELETE CASCADE,
    endpoint VARCHAR(255) NOT NULL,
    status_code INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_key_hash ON api_keys(key_hash);
CREATE INDEX IF NOT EXISTS idx_api_keys_is_active ON api_keys(is_active);
CREATE INDEX IF NOT EXISTS idx_api_usage_api_key_id ON api_usage(api_key_id);
CREATE INDEX IF NOT EXISTS idx_api_usage_created_at ON api_usage(created_at);

-- Function to increment request count
CREATE OR REPLACE FUNCTION increment_api_key_requests(key_id UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE api_keys
    SET requests_count = requests_count + 1
    WHERE id = key_id;
END;
$$ LANGUAGE plpgsql;

-- Row Level Security (RLS) policies
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_usage ENABLE ROW LEVEL SECURITY;

-- Users can only see their own API keys
CREATE POLICY "Users can view own API keys"
    ON api_keys FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own API keys"
    ON api_keys FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own API keys"
    ON api_keys FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own API keys"
    ON api_keys FOR DELETE
    USING (auth.uid() = user_id);

-- Users can view usage for their API keys
CREATE POLICY "Users can view own API usage"
    ON api_usage FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM api_keys
            WHERE api_keys.id = api_usage.api_key_id
            AND api_keys.user_id = auth.uid()
        )
    );

-- Service role can insert usage (for backend tracking)
CREATE POLICY "Service role can insert usage"
    ON api_usage FOR INSERT
    WITH CHECK (true);

COMMENT ON TABLE api_keys IS 'Stores API keys for developer access';
COMMENT ON TABLE api_usage IS 'Tracks API usage for analytics and billing';
