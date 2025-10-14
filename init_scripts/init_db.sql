-- Initialize PostgreSQL database for PikaHelper RAG System

-- Create database if not exists (this will be handled by Docker)
-- CREATE DATABASE pikadb;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create custom types
CREATE TYPE content_type AS ENUM ('docx', 'pdf', 'txt', 'md');
CREATE TYPE processing_status AS ENUM ('pending', 'processing', 'completed', 'failed');

-- Create documents table
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size BIGINT,
    content_type content_type DEFAULT 'docx',
    minio_path TEXT,
    metadata JSONB,
    processing_status processing_status DEFAULT 'pending',
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create chunks table
CREATE TABLE IF NOT EXISTS chunks (
    id SERIAL PRIMARY KEY,
    doc_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    chunk_id VARCHAR(255) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    minio_path TEXT,
    processing_status processing_status DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create embeddings table
CREATE TABLE IF NOT EXISTS embeddings (
    id SERIAL PRIMARY KEY,
    chunk_id VARCHAR(255) REFERENCES chunks(chunk_id) ON DELETE CASCADE,
    embedding_vector FLOAT[],
    model_name VARCHAR(100),
    model_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create chat sessions table
CREATE TABLE IF NOT EXISTS chat_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Create chat messages table
CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_documents_file_name ON documents(file_name);
CREATE INDEX IF NOT EXISTS idx_documents_content_type ON documents(content_type);
CREATE INDEX IF NOT EXISTS idx_documents_processing_status ON documents(processing_status);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at);

CREATE INDEX IF NOT EXISTS idx_chunks_doc_id ON chunks(doc_id);
CREATE INDEX IF NOT EXISTS idx_chunks_chunk_id ON chunks(chunk_id);
CREATE INDEX IF NOT EXISTS idx_chunks_processing_status ON chunks(processing_status);
CREATE INDEX IF NOT EXISTS idx_chunks_created_at ON chunks(created_at);

CREATE INDEX IF NOT EXISTS idx_embeddings_chunk_id ON embeddings(chunk_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_model_name ON embeddings(model_name);
CREATE INDEX IF NOT EXISTS idx_embeddings_created_at ON embeddings(created_at);

CREATE INDEX IF NOT EXISTS idx_chat_sessions_session_id ON chat_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_last_activity ON chat_sessions(last_activity);

CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_role ON chat_messages(role);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages(created_at);

-- Create full-text search indexes
CREATE INDEX IF NOT EXISTS idx_documents_content_fts ON documents USING gin(to_tsvector('vietnamese', file_name || ' ' || COALESCE(metadata->>'title', '')));
CREATE INDEX IF NOT EXISTS idx_chunks_content_fts ON chunks USING gin(to_tsvector('vietnamese', content));

-- Create functions for data processing
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_chunks_updated_at BEFORE UPDATE ON chunks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create function to get document statistics
CREATE OR REPLACE FUNCTION get_document_stats()
RETURNS TABLE (
    total_documents BIGINT,
    total_chunks BIGINT,
    total_embeddings BIGINT,
    documents_by_type JSONB,
    processing_status JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        (SELECT COUNT(*) FROM documents) as total_documents,
        (SELECT COUNT(*) FROM chunks) as total_chunks,
        (SELECT COUNT(*) FROM embeddings) as total_embeddings,
        (SELECT jsonb_object_agg(content_type, count) 
         FROM (SELECT content_type, COUNT(*) as count FROM documents GROUP BY content_type) t) as documents_by_type,
        (SELECT jsonb_object_agg(processing_status, count) 
         FROM (SELECT processing_status, COUNT(*) as count FROM documents GROUP BY processing_status) t) as processing_status;
END;
$$ LANGUAGE plpgsql;

-- Create function to search documents
CREATE OR REPLACE FUNCTION search_documents(search_query TEXT, limit_count INTEGER DEFAULT 10)
RETURNS TABLE (
    doc_id INTEGER,
    file_name VARCHAR(255),
    file_path TEXT,
    content_preview TEXT,
    similarity_score REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.id,
        d.file_name,
        d.file_path,
        LEFT(d.metadata->>'title', 200) as content_preview,
        0.0 as similarity_score
    FROM documents d
    WHERE d.file_name ILIKE '%' || search_query || '%'
       OR d.metadata->>'title' ILIKE '%' || search_query || '%'
    ORDER BY d.created_at DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Create function to get chunk statistics
CREATE OR REPLACE FUNCTION get_chunk_stats()
RETURNS TABLE (
    total_chunks BIGINT,
    avg_chunk_size REAL,
    chunks_with_embeddings BIGINT,
    chunks_without_embeddings BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        (SELECT COUNT(*) FROM chunks) as total_chunks,
        (SELECT AVG(LENGTH(content)) FROM chunks) as avg_chunk_size,
        (SELECT COUNT(*) FROM chunks c JOIN embeddings e ON c.chunk_id = e.chunk_id) as chunks_with_embeddings,
        (SELECT COUNT(*) FROM chunks c LEFT JOIN embeddings e ON c.chunk_id = e.chunk_id WHERE e.chunk_id IS NULL) as chunks_without_embeddings;
END;
$$ LANGUAGE plpgsql;

-- Insert initial configuration
INSERT INTO documents (file_name, file_path, content_type, metadata, processing_status) 
VALUES (
    'system_config', 
    '/system/config', 
    'docx', 
    '{"description": "System configuration document", "version": "1.0"}'::jsonb, 
    'completed'
) ON CONFLICT DO NOTHING;

-- Create views for easier querying
CREATE OR REPLACE VIEW document_summary AS
SELECT 
    d.id,
    d.file_name,
    d.file_path,
    d.content_type,
    d.processing_status,
    d.created_at,
    COUNT(c.id) as chunk_count,
    COUNT(e.id) as embedding_count
FROM documents d
LEFT JOIN chunks c ON d.id = c.doc_id
LEFT JOIN embeddings e ON c.chunk_id = e.chunk_id
GROUP BY d.id, d.file_name, d.file_path, d.content_type, d.processing_status, d.created_at;

CREATE OR REPLACE VIEW chunk_summary AS
SELECT 
    c.id,
    c.chunk_id,
    c.doc_id,
    d.file_name,
    c.processing_status,
    LENGTH(c.content) as content_length,
    c.created_at,
    CASE WHEN e.id IS NOT NULL THEN true ELSE false END as has_embedding
FROM chunks c
JOIN documents d ON c.doc_id = d.id
LEFT JOIN embeddings e ON c.chunk_id = e.chunk_id;

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO pika_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO pika_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO pika_user;
