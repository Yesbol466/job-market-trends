FROM apache/airflow:2.9.1-python3.11

USER root

RUN apt-get update && apt-get install -y \
    git \
    && apt-get clean

USER airflow

RUN pip install --no-cache-dir \
    pandas \
    psycopg2-binary \
    python-dotenv \
    dbt-postgres

COPY airflow/dags/ /opt/airflow/dags/
COPY ingestion/ /opt/airflow/ingestion/
COPY dbt/ /opt/airflow/dbt/