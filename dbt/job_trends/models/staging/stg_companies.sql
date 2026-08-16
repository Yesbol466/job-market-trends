SELECT id,
    TRIM(name) AS company_name,
    TRIM(industry) AS industry,
    TRIM(size) AS company_size,
    TRIM(profile) AS company_profile
FROM {{ source('public', 'companies') }}
WHERE name IS NOT NULL