import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import os
import re

# ================================
# K8S DB CONFIG
# ================================
DB_CONFIG = {
    "host":     "127.0.0.1",
    "port":     51829,
    "dbname":   "job_trends",
    "user":     "admin",
    "password": "admin123",
}

CSV_PATH = "ingestion/job_sample.csv"
BATCH_SIZE = 500

def parse_salary(salary_str):
    if pd.isna(salary_str):
        return None, None
    numbers = re.findall(r'\d+', str(salary_str))
    if len(numbers) == 2:
        return int(numbers[0]) * 1000, int(numbers[1]) * 1000
    return None, None

def clean_str(val):
    if pd.isna(val) or str(val).strip() == "":
        return None
    return str(val).strip()

def parse_date(val):
    try:
        return pd.to_datetime(val).date()
    except:
        return None

def batch(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

print("Loading sample CSV...")
df = pd.read_csv(CSV_PATH)
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
print(f"Loaded {len(df)} rows")

print("Connecting to Render PostgreSQL...")
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()
print("Connected.")

# ================================
# CREATE SCHEMA
# ================================
print("Creating schema...")
cur.execute("""
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

    CREATE TABLE IF NOT EXISTS locations (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        city VARCHAR(100), country VARCHAR(100),
        region VARCHAR(100), latitude FLOAT, longitude FLOAT
    );
    CREATE TABLE IF NOT EXISTS companies (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        name VARCHAR(255), size VARCHAR(50), profile TEXT
    );
    CREATE TABLE IF NOT EXISTS jobs (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        company_id UUID REFERENCES companies(id),
        location_id UUID REFERENCES locations(id),
        title VARCHAR(255), role VARCHAR(255),
        experience_required VARCHAR(100), qualifications VARCHAR(100),
        work_type VARCHAR(50), preference VARCHAR(50),
        salary_min INT, salary_max INT,
        description TEXT, benefits TEXT, responsibilities TEXT,
        job_portal VARCHAR(100), posted_at DATE,
        source VARCHAR(50), original_job_id TEXT
    );
    CREATE TABLE IF NOT EXISTS skills (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        name TEXT UNIQUE, category VARCHAR(100)
    );
    CREATE TABLE IF NOT EXISTS job_skills (
        job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
        skill_id UUID REFERENCES skills(id) ON DELETE CASCADE,
        PRIMARY KEY (job_id, skill_id)
    );
""")
conn.commit()
print("Schema created.")

# ================================
# LOCATIONS
# ================================
print("Inserting locations...")
loc_rows = df[["location", "country", "latitude", "longitude"]].drop_duplicates()
loc_data = []
for _, row in loc_rows.iterrows():
    loc_data.append((
        clean_str(row.get("location")),
        clean_str(row.get("country")),
        float(row["latitude"]) if pd.notna(row.get("latitude")) else None,
        float(row["longitude"]) if pd.notna(row.get("longitude")) else None
    ))
execute_values(cur, "INSERT INTO locations (city, country, latitude, longitude) VALUES %s ON CONFLICT DO NOTHING", loc_data)
conn.commit()
cur.execute("SELECT id, city, country FROM locations")
location_map = {(r[1], r[2]): r[0] for r in cur.fetchall()}
print(f"Locations: {len(location_map)}")

# ================================
# COMPANIES
# ================================
print("Inserting companies...")
comp_rows = df[["company", "company_size", "company_profile"]].drop_duplicates(subset=["company"])
comp_data = [(clean_str(r["company"]), clean_str(r["company_size"]), clean_str(r["company_profile"])) for _, r in comp_rows.iterrows() if clean_str(r["company"])]
execute_values(cur, "INSERT INTO companies (name, size, profile) VALUES %s ON CONFLICT DO NOTHING", comp_data)
conn.commit()
cur.execute("SELECT id, name FROM companies")
company_map = {r[1]: r[0] for r in cur.fetchall()}
print(f"Companies: {len(company_map)}")

# ================================
# JOBS
# ================================
print("Inserting jobs...")
df[["salary_min", "salary_max"]] = df["salary_range"].str.extract(r'\$(\d+)K-\$(\d+)K').astype(float) * 1000
df["posted_at"] = pd.to_datetime(df["job_posting_date"], errors="coerce").dt.date
df["company_id"] = df["company"].map(company_map)
df["location_id"] = df.apply(lambda r: location_map.get((clean_str(r["location"]), clean_str(r["country"]))), axis=1)

jobs_df = df[["company_id","location_id","job_title","role","experience","qualifications","work_type","preference","salary_min","salary_max","job_description","benefits","responsibilities","job_portal","posted_at","job_id"]].copy()
jobs_df.columns = ["company_id","location_id","title","role","experience_required","qualifications","work_type","preference","salary_min","salary_max","description","benefits","responsibilities","job_portal","posted_at","original_job_id"]
jobs_df["source"] = "kaggle"
jobs_df = jobs_df.where(pd.notna(jobs_df), None)
job_rows = list(jobs_df.itertuples(index=False, name=None))

for i, b in enumerate(batch(job_rows, BATCH_SIZE)):
    execute_values(cur, """
        INSERT INTO jobs (company_id,location_id,title,role,experience_required,qualifications,work_type,preference,salary_min,salary_max,description,benefits,responsibilities,job_portal,posted_at,original_job_id,source)
        VALUES %s ON CONFLICT DO NOTHING
    """, b)
    conn.commit()
    print(f"  jobs batch {i+1} done")

cur.execute("SELECT id, original_job_id FROM jobs")
job_map = {r[1]: r[0] for r in cur.fetchall()}
print(f"Jobs: {len(job_map)}")

# ================================
# SKILLS
# ================================
print("Inserting skills...")
all_skills = set()
for _, row in df.iterrows():
    raw = clean_str(row.get("skills"))
    if raw:
        for s in raw.split(","):
            s = s.strip()
            if s and len(s) <= 50:
                all_skills.add(s)

execute_values(cur, "INSERT INTO skills (name) VALUES %s ON CONFLICT (name) DO NOTHING", [(s,) for s in all_skills])
conn.commit()
cur.execute("SELECT id, name FROM skills")
skill_map = {r[1]: r[0] for r in cur.fetchall()}
print(f"Skills: {len(skill_map)}")

# ================================
# JOB SKILLS
# ================================
print("Inserting job_skills...")
job_skill_rows = []
for _, row in df.iterrows():
    job_uuid = job_map.get(clean_str(row.get("job_id")))
    raw = clean_str(row.get("skills"))
    if not job_uuid or not raw:
        continue
    for s in raw.split(","):
        s = s.strip()
        skill_uuid = skill_map.get(s)
        if skill_uuid:
            job_skill_rows.append((job_uuid, skill_uuid))

for i, b in enumerate(batch(job_skill_rows, BATCH_SIZE)):
    execute_values(cur, "INSERT INTO job_skills (job_id, skill_id) VALUES %s ON CONFLICT DO NOTHING", b)
    conn.commit()
    print(f"  job_skills batch {i+1} done")

print(f"Job skills: {len(job_skill_rows)}")

# ================================
# CREATE ANALYTICS SCHEMA
# ================================
print("Creating analytics views...")
cur.execute("""
    CREATE SCHEMA IF NOT EXISTS analytics;

    CREATE OR REPLACE VIEW analytics.most_demanded_skills AS
    SELECT s.name AS skill_name, COUNT(js.job_id) AS job_count,
    RANK() OVER (ORDER BY COUNT(js.job_id) DESC) AS demand_rank
    FROM skills s JOIN job_skills js ON s.id = js.skill_id
    GROUP BY s.name ORDER BY job_count DESC;

    CREATE OR REPLACE VIEW analytics.salary_by_role AS
    SELECT role, COUNT(*) AS job_count,
    ROUND(AVG((salary_min+salary_max)/2)) AS avg_salary,
    ROUND(MIN(salary_min)) AS min_salary,
    ROUND(MAX(salary_max)) AS max_salary
    FROM jobs WHERE salary_min IS NOT NULL AND role IS NOT NULL
    GROUP BY role ORDER BY avg_salary DESC;

    CREATE OR REPLACE VIEW analytics.hiring_by_country AS
    SELECT l.country, COUNT(j.id) AS job_count,
    ROUND(AVG((j.salary_min+j.salary_max)/2)) AS avg_salary,
    RANK() OVER (ORDER BY COUNT(j.id) DESC) AS hiring_rank
    FROM jobs j JOIN locations l ON j.location_id = l.id
    WHERE l.country IS NOT NULL GROUP BY l.country ORDER BY job_count DESC;

    CREATE OR REPLACE VIEW analytics.top_hiring_companies AS
    SELECT c.name AS company_name, c.size AS company_size,
    COUNT(j.id) AS job_count,
    ROUND(AVG((j.salary_min+j.salary_max)/2)) AS avg_salary,
    RANK() OVER (ORDER BY COUNT(j.id) DESC) AS hiring_rank
    FROM jobs j JOIN companies c ON j.company_id = c.id
    WHERE c.name IS NOT NULL GROUP BY c.name, c.size ORDER BY job_count DESC;
""")
conn.commit()
print("Analytics views created.")

cur.close()
conn.close()
print("All done! Render database is ready.")