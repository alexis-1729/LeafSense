CREATE TABLE IF NOT EXISTS diagnoses (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    crop TEXT,
    pest_label TEXT NOT NULL,
    confidence DOUBLE PRECISION NOT NULL
        CHECK (confidence >= 0.0 AND confidence <= 1.0),
    top_k JSONB NOT NULL,
    conclusive BOOLEAN NOT NULL,
    diagnosis JSONB,
    sources JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_diagnoses_user_created_at
    ON diagnoses (user_id, created_at DESC);
