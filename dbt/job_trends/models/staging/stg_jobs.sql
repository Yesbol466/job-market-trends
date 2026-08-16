SELECT id,
    company_id,
    location_id,
    TRIM(title) AS job_title,
    TRIM(role) AS role,
    TRIM(experience_required) AS experience,
    TRIM(qualifications) AS qualifications,
    TRIM(work_type) AS work_type,
    TRIM(preference) AS preference,
    salary_min,
    salary_max,
    (salary_min + salary_max) / 2 AS salary_avg,
    TRIM(job_portal) AS job_portal,
    posted_at,
    source,
    original_job_id
FROM {{ source('public', 'jobs') }}
WHERE title IS NOT NULL