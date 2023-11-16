ALTER TABLE wakabi.word_knowledge
    ADD COLUMN IF NOT EXISTS true_count BIGINT DEFAULT 0;
