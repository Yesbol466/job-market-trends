SELECT
    s.skill_name,
    s.skill_category,
    COUNT(js.job_id)                        AS job_count,
    RANK() OVER (ORDER BY COUNT(js.job_id) DESC) AS demand_rank
FROM {{ ref('stg_skills') }} s
JOIN {{ source('public', 'job_skills') }} js ON s.id = js.skill_id
WHERE LENGTH(s.skill_name) <= 50
GROUP BY s.skill_name, s.skill_category
ORDER BY job_count DESC