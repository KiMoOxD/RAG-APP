-- =============================================
-- RAG Application Database Schema for Supabase
-- =============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================
-- Projects Table
-- =============================================
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_projects_project_id ON projects(project_id);

-- =============================================
-- Assets Table (File metadata)
-- =============================================
CREATE TABLE IF NOT EXISTS assets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset_project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    asset_type VARCHAR(50) NOT NULL,
    asset_name VARCHAR(500) NOT NULL,
    asset_size INTEGER DEFAULT 0,
    asset_config JSONB,
    asset_storage_path VARCHAR(1000),
    asset_pushed_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Unique constraint for project + asset name combination
    UNIQUE(asset_project_id, asset_name)
);

-- Indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_assets_project_id ON assets(asset_project_id);
CREATE INDEX IF NOT EXISTS idx_assets_type ON assets(asset_type);

-- =============================================
-- Chunks Table (Document chunks)
-- =============================================
CREATE TABLE IF NOT EXISTS chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chunk_text TEXT NOT NULL,
    chunk_metadata JSONB,
    chunk_order INTEGER NOT NULL,
    chunk_project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    chunk_asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_chunks_project_id ON chunks(chunk_project_id);
CREATE INDEX IF NOT EXISTS idx_chunks_asset_id ON chunks(chunk_asset_id);
CREATE INDEX IF NOT EXISTS idx_chunks_order ON chunks(chunk_order);

-- =============================================
-- Row Level Security (Optional but recommended)
-- =============================================
-- Uncomment these if you want to enable RLS

-- ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE assets ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE chunks ENABLE ROW LEVEL SECURITY;

-- =============================================
-- Updated At Trigger Function
-- =============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to all tables
CREATE TRIGGER update_projects_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_assets_updated_at
    BEFORE UPDATE ON assets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_chunks_updated_at
    BEFORE UPDATE ON chunks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
