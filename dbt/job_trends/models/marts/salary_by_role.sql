SELECT
    j.role,
    COUNT(*)                            AS job_count,
    ROUND(AVG(j.salary_avg))            AS avg_salary,
    ROUND(MIN(j.salary_min))            AS min_salary,
    ROUND(MAX(j.salary_max))            AS max_salary
FROM {{ ref('stg_jobs') }} j
WHERE j.salary_avg IS NOT NULL
    AND j.role IS NOT NULL
GROUP BY j.role
ORDER BY avg_salary DESC