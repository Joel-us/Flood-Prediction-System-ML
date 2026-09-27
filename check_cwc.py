import duckdb

con = duckdb.connect()

con.execute("INSTALL httpfs")
con.execute("LOAD httpfs")

con.execute("""
    CREATE OR REPLACE TABLE mapping AS
    SELECT *
    FROM read_csv_auto('data/processed/INDOFLOODS_CWC_station_mapping.csv')
    WHERE distance_km <= 5
""")

count = con.execute(
    "SELECT COUNT(*) FROM mapping"
).fetchone()[0]

print("Matched stations:", count)

columns = con.execute("""
    DESCRIBE
    SELECT *
    FROM read_parquet(
        'https://diagram-chasing.github.io/cwc-flood-forecasts/daily.parquet'
    )
""").fetchdf()

print("\nCWC DAILY DATA COLUMNS")
print("=" * 60)
print(columns.to_string(index=False))

con.close()
