SELECT
    l.country,
    COUNT(j.id)                         AS job_count,
    ROUND(AVG(j.salary_avg))            AS avg_salary,
    RANK() OVER (ORDER BY COUNT(j.id) DESC) AS hiring_rank
FROM {{ ref('stg_jobs') }} j
JOIN {{ ref('stg_locations') }} l ON j.location_id = l.id
WHERE l.country IS NOT NULL
GROUP BY l.country
ORDER BY job_count DESC