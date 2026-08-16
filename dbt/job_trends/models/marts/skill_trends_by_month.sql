SELECT
    DATE_TRUNC('month', j.posted_at)    AS month,
    s.skill_name,
    COUNT(js.job_id)                    AS job_count
FROM {{ ref('stg_jobs') }} j
JOIN {{ source('public', 'job_skills') }} js ON j.id = js.job_id
JOIN {{ ref('stg_skills') }} s ON js.skill_id = s.id
WHERE j.posted_at IS NOT NULL
GROUP BY month, s.skill_name
ORDER BY month DESC, job_count DESC