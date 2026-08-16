import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import os
import re

# ================================
# LOAD ENV VARIABLES
# ================================
load_dotenv()

DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   os.getenv("POSTGRES_DB"),
    "user":     os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD")
}

CSV_PATH = "ingestion/job_descriptions.csv"
BATCH_SIZE = 5000

# ================================
# HELPER FUNCTIONS
# ================================

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

# ================================
# LOAD CSV
# ================================

print("Loading CSV...")
df = pd.read_csv(CSV_PATH)
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
print(f"Loaded {len(df)} rows")

# ================================
# CONNECT
# ================================

print("Connecting to database...")
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()
print("Connected.")

# ================================
# STEP 1 — RAW JOBS (batch)
# ================================

print("Inserting raw_jobs...")

raw_columns = [
    "job_id", "experience", "qualifications", "salary_range",
    "location", "country", "latitude", "longitude", "work_type",
    "company_size", "job_posting_date", "preference", "contact_person",
    "contact", "job_title", "role", "job_portal", "job_description",
    "benefits", "skills", "responsibilities", "company", "company_profile"
]

csv_keys = [
    "job_id", "experience", "qualifications", "salary_range",
    "location", "country", "latitude", "longitude", "work_type",
    "company_size", "job_posting_date", "preference", "contact_person",
    "contact", "job_title", "role", "job_portal", "job_description",
    "benefits", "skills", "responsibilities", "company", "company_profile"
]

raw_rows = [
    tuple(clean_str(row.get(col)) for col in csv_keys)
    for _, row in df.iterrows()
]

for i, b in enumerate(batch(raw_rows, BATCH_SIZE)):
    execute_values(cur, f"""
        INSERT INTO raw_jobs ({', '.join(raw_columns)})
        VALUES %s ON CONFLICT DO NOTHING
    """, b)
    conn.commit()
    print(f"  raw_jobs batch {i+1} done ({min((i+1)*BATCH_SIZE, len(raw_rows))}/{len(raw_rows)})")

print("raw_jobs done.")

# ================================
# STEP 2 — LOCATIONS (batch)
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

execute_values(cur, """
    INSERT INTO locations (city, country, latitude, longitude)
    VALUES %s ON CONFLICT DO NOTHING
""", loc_data)
conn.commit()

cur.execute("SELECT id, city, country FROM locations")
location_map = {(r[1], r[2]): r[0] for r in cur.fetchall()}
print(f"Locations done: {len(location_map)}")

# ================================
# STEP 3 — COMPANIES (batch)
# ================================

print("Inserting companies...")

comp_rows = df[["company", "company_size", "company_profile"]].drop_duplicates(subset=["company"])
comp_data = [
    (clean_str(r.get("company")), clean_str(r.get("company_size")), clean_str(r.get("company_profile")))
    for _, r in comp_rows.iterrows()
    if clean_str(r.get("company"))
]

execute_values(cur, """
    INSERT INTO companies (name, size, profile)
    VALUES %s ON CONFLICT DO NOTHING
""", comp_data)
conn.commit()

cur.execute("SELECT id, name FROM companies")
company_map = {r[1]: r[0] for r in cur.fetchall()}
print(f"Companies done: {len(company_map)}")

# ================================
# STEP 4 — JOBS (batch)
# ================================

print("Inserting jobs...")

job_rows = []
original_job_ids = []

for _, row in df.iterrows():
    company_id  = company_map.get(clean_str(row.get("company")))
    city        = clean_str(row.get("location"))
    country     = clean_str(row.get("country"))
    location_id = location_map.get((city, country))
    sal_min, sal_max = parse_salary(row.get("salary_range"))

    job_rows.append((
        company_id, location_id,
        clean_str(row.get("job_title")),
        clean_str(row.get("role")),
        clean_str(row.get("experience")),
        clean_str(row.get("qualifications")),
        clean_str(row.get("work_type")),
        clean_str(row.get("preference")),
        sal_min, sal_max,
        clean_str(row.get("job_description")),
        clean_str(row.get("benefits")),
        clean_str(row.get("responsibilities")),
        clean_str(row.get("job_portal")),
        parse_date(row.get("job_posting_date")),
        "kaggle",
        clean_str(row.get("job_id"))  # store original id for mapping
    ))
    original_job_ids.append(clean_str(row.get("job_id")))

for i, b in enumerate(batch(job_rows, BATCH_SIZE)):
    execute_values(cur, """
        INSERT INTO jobs (
            company_id, location_id, title, role,
            experience_required, qualifications, work_type,
            preference, salary_min, salary_max,
            description, benefits, responsibilities,
            job_portal, posted_at, source, original_job_id
        )
        VALUES %s ON CONFLICT DO NOTHING
    """, b)
    conn.commit()
    print(f"  jobs batch {i+1} done ({min((i+1)*BATCH_SIZE, len(job_rows))}/{len(job_rows)})")

# Build job_map from original_job_id
cur.execute("SELECT id, original_job_id FROM jobs")
job_map = {r[1]: r[0] for r in cur.fetchall()}
print(f"Jobs done: {len(job_map)}")

# ================================
# STEP 5 — SKILLS (batch)
# ================================

print("Inserting skills...")

all_skills = set()
for _, row in df.iterrows():
    raw = clean_str(row.get("skills"))
    if raw:
        for s in raw.split(","):
            s = s.strip()
            if s:
                all_skills.add(s)

execute_values(cur, """
    INSERT INTO skills (name)
    VALUES %s ON CONFLICT (name) DO NOTHING
""", [(s,) for s in all_skills])
conn.commit()

cur.execute("SELECT id, name FROM skills")
skill_map = {r[1]: r[0] for r in cur.fetchall()}
print(f"Skills done: {len(skill_map)}")

# ================================
# STEP 6 — JOB SKILLS (batch)
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
    execute_values(cur, """
        INSERT INTO job_skills (job_id, skill_id)
        VALUES %s ON CONFLICT DO NOTHING
    """, b)
    conn.commit()
    print(f"  job_skills batch {i+1} done ({min((i+1)*BATCH_SIZE, len(job_skill_rows))}/{len(job_skill_rows)})")

print("Job skills done.")

# ================================
# DONE
# ================================

cur.close()
conn.close()
print("All done!")