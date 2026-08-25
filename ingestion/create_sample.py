import pandas as pd

df = pd.read_csv('ingestion/job_descriptions.csv')
sample = df.sample(n=10000, random_state=42)
sample.to_csv('ingestion/job_sample.csv', index=False)
print(f"Sample created: {len(sample)} rows")
print(f"Columns: {list(sample.columns)}")