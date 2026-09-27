import duckdb

con = duckdb.connect()

con.execute("INSTALL httpfs")
con.execute("LOAD httpfs")

query = """
WITH mapping AS (
    SELECT
        CWC_station_code AS station_code
    FROM read_csv_auto(
        'data/processed/INDOFLOODS_CWC_station_mapping.csv'
    )
    WHERE distance_km <= 5
)

SELECT
    d.variable,
    d.datatype_code,
    d.unit,
    COUNT(*) AS rows,
    COUNT(DISTINCT d.station_code) AS stations,
    MIN(d.date_ist) AS first_date,
    MAX(d.date_ist) AS last_date
FROM read_parquet(
    'https://diagram-chasing.github.io/cwc-flood-forecasts/daily.parquet'
) d
INNER JOIN mapping m
    ON d.station_code = m.station_code
WHERE d.variable IN (
    'rainfall',
    'water_level',
    'discharge'
)
GROUP BY
    d.variable,
    d.datatype_code,
    d.unit
ORDER BY
    d.variable,
    d.datatype_code
"""

df = con.execute(query).fetchdf()

print("\nMATCHED CWC DATA")
print("=" * 100)
print(df.to_string(index=False))

con.close()