def write_to_postgres(df, table, mode="overwrite"):
    from utils.postgres import POSTGRES_URL, POSTGRES_PROPERTIES
    df.write.jdbc(
        url=POSTGRES_URL,
        table=table,
        mode=mode,
        properties=POSTGRES_PROPERTIES
    )
