from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import subprocess
import sys
import os

default_args = {
    'owner': 'yesbol',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def run_ingestion():
    """Run the sample data ingestion script"""
    result = subprocess.run(
        [sys.executable, '/opt/airflow/ingestion/ingest_render.py'],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        raise Exception(f"Ingestion failed: {result.stderr}")
    print("Ingestion completed successfully")

def run_dbt():
    """Run dbt transformations"""
    result = subprocess.run(
        ['dbt', 'run', '--profiles-dir', '.'],
        capture_output=True,
        text=True,
        cwd='/opt/airflow/dbt/job_trends'
    )
    print(result.stdout)
    if result.returncode != 0:
        raise Exception(f"dbt failed: {result.stderr}")
    print("dbt transformations completed successfully")

def check_data_quality():
    """Basic data quality check"""
    import psycopg2
    import os

    conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM jobs")
    job_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM job_skills")
    skill_count = cur.fetchone()[0]

    cur.close()
    conn.close()

    print(f"Data quality check: {job_count} jobs, {skill_count} job-skill relationships")

    if job_count == 0:
        raise Exception("Data quality check failed: no jobs found")

    print("Data quality check passed")

with DAG(
    dag_id='job_trends_pipeline',
    default_args=default_args,
    description='Ingests job data and runs dbt transformations',
    schedule_interval='0 0 * * 1',  # Every Monday at midnight
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['data-engineering', 'job-trends'],
) as dag:

    ingest_task = PythonOperator(
        task_id='run_ingestion',
        python_callable=run_ingestion,
    )

    dbt_task = PythonOperator(
        task_id='run_dbt_transformations',
        python_callable=run_dbt,
    )

    quality_task = PythonOperator(
        task_id='data_quality_check',
        python_callable=check_data_quality,
    )

    ingest_task >> dbt_task >> quality_task