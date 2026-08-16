SELECT
    c.company_name,
    c.company_size,
    COUNT(j.id)                         AS job_count,
    ROUND(AVG(j.salary_avg))            AS avg_salary,
    RANK() OVER (ORDER BY COUNT(j.id) DESC) AS hiring_rank
FROM {{ ref('stg_jobs') }} j
JOIN {{ ref('stg_companies') }} c ON j.company_id = c.id
WHERE c.company_name IS NOT NULL
GROUP BY c.company_name, c.company_size
ORDER BY job_count DESC