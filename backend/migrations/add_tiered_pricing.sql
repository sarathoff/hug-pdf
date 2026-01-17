"""
Database Migration: Add 3-Tier Pricing Schema

Run this SQL in your Supabase SQL Editor to add the new pricing tiers and credit system.

IMPORTANT: This will:
1. Add new columns to users table for credit tracking
2. Create credit_transactions table for audit trail
3. Create credit_packs table for top-up purchases
4. Migrate existing users to 'pro' plan with full credits
"""

-- Step 1: Add new columns to users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS plan TEXT DEFAULT 'starter' CHECK (plan IN ('starter', 'pro', 'power')),
ADD COLUMN IF NOT EXISTS research_credits INTEGER DEFAULT 2,
ADD COLUMN IF NOT EXISTS diagram_credits INTEGER DEFAULT 5,
ADD COLUMN IF NOT EXISTS ebook_credits INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS pdf_downloads INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS credits_reset_date TIMESTAMP DEFAULT (NOW() + INTERVAL '30 days');

-- Step 2: Create credit_transactions table for audit trail
CREATE TABLE IF NOT EXISTS credit_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    credit_type TEXT NOT NULL CHECK (credit_type IN ('research', 'diagram', 'ebook', 'pdf', 'all')),
    amount INTEGER NOT NULL,
    transaction_type TEXT NOT NULL CHECK (transaction_type IN ('deduct', 'add', 'reset')),
    reason TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Foreign key to users table
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_credit_transactions_user_id ON credit_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_created_at ON credit_transactions(created_at DESC);

-- Step 3: Create credit_packs table for top-up purchases
CREATE TABLE IF NOT EXISTS credit_packs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    pack_type TEXT NOT NULL CHECK (pack_type IN ('research', 'diagram', 'ebook')),
    credits_added INTEGER NOT NULL,
    amount_paid DECIMAL(10,2) NOT NULL,
    currency TEXT DEFAULT 'INR',
    payment_session_id TEXT,
    purchased_at TIMESTAMP DEFAULT NOW(),
    
    -- Foreign key to users table
    CONSTRAINT fk_user_pack FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_credit_packs_user_id ON credit_packs(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_packs_purchased_at ON credit_packs(purchased_at DESC);

-- Step 4: Migrate existing users to 'pro' plan (generous migration)
-- This gives all existing users the Pro plan benefits
UPDATE users 
SET 
    plan = 'pro',
    research_credits = 15,
    diagram_credits = 25,
    ebook_credits = 2,
    pdf_downloads = 0,
    credits_reset_date = NOW() + INTERVAL '30 days'
WHERE plan IS NULL OR plan = 'free';

-- Step 5: Update the old 'credits' column (if it exists) to be deprecated
-- Keep it for backward compatibility but don't use it
COMMENT ON COLUMN users.credits IS 'DEPRECATED: Use plan-specific credit columns instead';

-- Step 6: Create a function to auto-reset credits monthly (optional, can also be done in backend)
CREATE OR REPLACE FUNCTION reset_user_credits()
RETURNS void AS $$
BEGIN
    UPDATE users
    SET 
        research_credits = CASE 
            WHEN plan = 'starter' THEN 2
            WHEN plan = 'pro' THEN 15
            WHEN plan = 'power' THEN 50
            ELSE 2
        END,
        diagram_credits = CASE 
            WHEN plan = 'starter' THEN 5
            WHEN plan = 'pro' THEN 25
            WHEN plan = 'power' THEN -1  -- Unlimited
            ELSE 5
        END,
        ebook_credits = CASE 
            WHEN plan = 'starter' THEN 0
            WHEN plan = 'pro' THEN 2
            WHEN plan = 'power' THEN 10
            ELSE 0
        END,
        pdf_downloads = 0,
        credits_reset_date = NOW() + INTERVAL '30 days'
    WHERE credits_reset_date < NOW();
    
    -- Log the reset
    INSERT INTO credit_transactions (user_id, credit_type, amount, transaction_type, reason)
    SELECT user_id, 'all', 0, 'reset', 'Automated monthly reset'
    FROM users
    WHERE credits_reset_date < NOW();
END;
$$ LANGUAGE plpgsql;

-- Optional: Create a cron job to run this function daily (requires pg_cron extension)
-- SELECT cron.schedule('reset-credits-daily', '0 0 * * *', 'SELECT reset_user_credits()');

-- Step 7: Grant permissions (adjust based on your RLS policies)
-- Allow authenticated users to read their own credit transactions
ALTER TABLE credit_transactions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own credit transactions"
ON credit_transactions
FOR SELECT
USING (auth.uid()::text = user_id);

-- Allow service role to insert/update credit transactions
CREATE POLICY "Service role can manage credit transactions"
ON credit_transactions
FOR ALL
USING (auth.role() = 'service_role');

-- Same for credit_packs
ALTER TABLE credit_packs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own credit packs"
ON credit_packs
FOR SELECT
USING (auth.uid()::text = user_id);

CREATE POLICY "Service role can manage credit packs"
ON credit_packs
FOR ALL
USING (auth.role() = 'service_role');

-- Step 8: Verification queries
-- Run these to verify the migration worked

-- Check users table structure
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'users' 
AND column_name IN ('plan', 'research_credits', 'diagram_credits', 'ebook_credits', 'pdf_downloads', 'credits_reset_date');

-- Check how many users are on each plan
SELECT plan, COUNT(*) as user_count
FROM users
GROUP BY plan;

-- Check if tables were created
SELECT table_name 
FROM information_schema.tables 
WHERE table_name IN ('credit_transactions', 'credit_packs');

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Migration completed successfully!';
    RAISE NOTICE 'Users table updated with new credit columns';
    RAISE NOTICE 'credit_transactions and credit_packs tables created';
    RAISE NOTICE 'All existing users migrated to Pro plan';
END $$;
