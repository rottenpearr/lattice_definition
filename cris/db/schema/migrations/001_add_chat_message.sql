-- Migration 001: add chat_message table
-- Хранит историю диалога, привязанную к сессии распознавания

CREATE TABLE IF NOT EXISTS chat_message (
    id          SERIAL PRIMARY KEY,
    session_id  UUID        NOT NULL,
    role        VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content     TEXT        NOT NULL,
    created_at  TIMESTAMP   DEFAULT NOW(),
    FOREIGN KEY (session_id) REFERENCES recognition_session(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_chat_session ON chat_message (session_id, created_at);
