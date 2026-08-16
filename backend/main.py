from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
def get_conn():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", 5432)),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )

@app.get("/api/skills/demand")
def skill_demand(limit: int = 20):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT skill_name, skill_category, job_count, demand_rank
        FROM analytics.most_demanded_skills
        ORDER BY demand_rank
        LIMIT %s
    """, (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return list(rows)

@app.get("/api/salary/by-role")
def salary_by_role(limit: int = 15):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT role, job_count, avg_salary, min_salary, max_salary
        FROM analytics.salary_by_role
        ORDER BY avg_salary DESC
        LIMIT %s
    """, (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return list(rows)

@app.get("/api/hiring/by-country")
def hiring_by_country(limit: int = 15):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT country, job_count, avg_salary, hiring_rank
        FROM analytics.hiring_by_country
        ORDER BY hiring_rank
        LIMIT %s
    """, (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return list(rows)

@app.get("/api/companies/top")
def top_companies(limit: int = 15):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT company_name, company_size, job_count, avg_salary, hiring_rank
        FROM analytics.top_hiring_companies
        ORDER BY hiring_rank
        LIMIT %s
    """, (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return list(rows)

@app.get("/api/stats/summary")
def summary():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT
            (SELECT COUNT(*) FROM public.jobs)       AS total_jobs,
            (SELECT COUNT(*) FROM public.companies)  AS total_companies,
            (SELECT COUNT(*) FROM public.skills)     AS total_skills,
            (SELECT COUNT(*) FROM public.locations)  AS total_countries
    """)
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row