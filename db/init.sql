-- ===========================================
-- JOB TRENDS ANALYSIS - DATABASE SCHEMA
-- ===========================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ===========================================
-- RAW LAYER (exact copy of Kaggle CSV)
-- ===========================================

CREATE TABLE IF NOT EXISTS raw_jobs (
    job_id              TEXT,
    experience          TEXT,
    qualifications      TEXT,
    salary_range        TEXT,
    location            TEXT,
    country             TEXT,
    latitude            TEXT,
    longitude           TEXT,
    work_type           TEXT,
    company_size        TEXT,
    job_posting_date    TEXT,
    preference          TEXT,
    contact_person      TEXT,
    contact             TEXT,
    job_title           TEXT,
    role                TEXT,
    job_portal          TEXT,
    job_description     TEXT,
    benefits            TEXT,
    skills              TEXT,
    responsibilities    TEXT,
    company_name        TEXT,
    company_profile     TEXT
);

-- ===========================================
-- TRANSFORMED LAYER
-- ===========================================

CREATE TABLE IF NOT EXISTS locations (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    city        VARCHAR(100),
    country     VARCHAR(100),
    region      VARCHAR(100),
    latitude    FLOAT,
    longitude   FLOAT
);

CREATE TABLE IF NOT EXISTS companies (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name        VARCHAR(255) NOT NULL,
    industry    VARCHAR(100),
    size        VARCHAR(50),
    headquarter VARCHAR(255),
    profile     TEXT
);

CREATE TABLE IF NOT EXISTS jobs (
    id                    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id            UUID REFERENCES companies(id),
    location_id           UUID REFERENCES locations(id),
    title                 VARCHAR(255),
    role                  VARCHAR(255),
    seniority_level       VARCHAR(50),
    experience_required   VARCHAR(100),
    qualifications        VARCHAR(100),
    work_type             VARCHAR(50),
    preference            VARCHAR(50),
    salary_min            INT,
    salary_max            INT,
    description           TEXT,
    benefits              TEXT,
    responsibilities      TEXT,
    job_portal            VARCHAR(100),
    posted_at             DATE,
    source                VARCHAR(50) DEFAULT 'kaggle'
);

CREATE TABLE IF NOT EXISTS skills (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name        VARCHAR(100) UNIQUE NOT NULL,
    category    VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS job_skills (
    job_id      UUID REFERENCES jobs(id) ON DELETE CASCADE,
    skill_id    UUID REFERENCES skills(id) ON DELETE CASCADE,
    PRIMARY KEY (job_id, skill_id)
);