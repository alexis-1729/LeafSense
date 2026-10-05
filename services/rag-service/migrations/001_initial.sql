CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY,
    content TEXT NOT NULL,
    pest_label TEXT NOT NULL,
    crop TEXT NOT NULL,
    source TEXT NOT NULL,
    language TEXT NOT NULL,
    filename TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'processing', 'indexed', 'failed', 'deleting')),
    chunk_count INTEGER NOT NULL DEFAULT 0 CHECK (chunk_count >= 0),
    error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_documents_status_created_at
    ON documents (status, created_at);
