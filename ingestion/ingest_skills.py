import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import os

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

def clean_str(val):
    if pd.isna(val) or str(val).strip() == "":
        return None
    return str(val).strip()

def batch(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

print("Loading CSV...")
df = pd.read_csv(CSV_PATH)
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
print(f"Loaded {len(df)} rows")

print("Connecting...")
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()
print("Connected.")

# ================================
# STEP 5 — SKILLS
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

print(f"Found {len(all_skills)} unique skills")

execute_values(cur, """
    INSERT INTO skills (name)
    VALUES %s ON CONFLICT (name) DO NOTHING
""", [(s,) for s in all_skills])
conn.commit()

cur.execute("SELECT id, name FROM skills")
skill_map = {r[1]: r[0] for r in cur.fetchall()}
print(f"Skills done: {len(skill_map)}")

# ================================
# STEP 6 — JOB SKILLS
# ================================

print("Inserting job_skills...")

cur.execute("SELECT id, original_job_id FROM jobs")
job_map = {r[1]: r[0] for r in cur.fetchall()}
print(f"Loaded {len(job_map)} jobs from DB")

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

print(f"Built {len(job_skill_rows)} job_skill relationships, inserting...")

for i, b in enumerate(batch(job_skill_rows, BATCH_SIZE)):
    execute_values(cur, """
        INSERT INTO job_skills (job_id, skill_id)
        VALUES %s ON CONFLICT DO NOTHING
    """, b)
    conn.commit()
    print(f"  job_skills batch {i+1} done ({min((i+1)*BATCH_SIZE, len(job_skill_rows))}/{len(job_skill_rows)})")

print("Job skills done.")

cur.close()
conn.close()
print("All done!")