SELECT
    id,
    TRIM(name)      AS skill_name,
    TRIM(category)  AS skill_category
FROM {{ source('public', 'skills') }}
WHERE name IS NOT NULL