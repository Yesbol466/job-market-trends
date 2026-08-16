SELECT
    id,
    TRIM(city)      AS city,
    TRIM(country)   AS country,
    TRIM(region)    AS region,
    latitude,
    longitude
FROM {{ source('public', 'locations') }}
WHERE city IS NOT NULL