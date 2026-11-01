CREATE TABLE IF NOT EXISTS studio_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    source_type VARCHAR(50),
    source_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'planning',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS studio_scenes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES studio_projects(id) ON DELETE CASCADE,
    scene_order INT NOT NULL,
    narration_text TEXT,
    visual_prompt TEXT,
    duration_seconds INT,
    audio_url TEXT,
    image_url TEXT,
    status VARCHAR(50) DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS studio_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES studio_projects(id) ON DELETE CASCADE,
    engine_name VARCHAR(50),
    status VARCHAR(50) DEFAULT 'queued',
    error_log TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
