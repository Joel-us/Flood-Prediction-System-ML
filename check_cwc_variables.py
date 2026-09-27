import duckdb

con = duckdb.connect()

con.execute("INSTALL httpfs")
con.execute("LOAD httpfs")

df = con.execute("""
    SELECT
        variable,
        datatype_code,
        unit,
        COUNT(*) AS rows
    FROM read_parquet(
        'https://diagram-chasing.github.io/cwc-flood-forecasts/daily.parquet'
    )
    GROUP BY variable, datatype_code, unit
    ORDER BY variable, datatype_code
""").fetchdf()

print("\nCWC AVAILABLE VARIABLES")
print("=" * 80)
print(df.to_string(index=False))

con.close()