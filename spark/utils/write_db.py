def to_postgres(df, table, mode="overwrite"):
    from utils.postgres import POSTGRES_URL, POSTGRES_PROPERTIES

    props = POSTGRES_PROPERTIES.copy()
    props["truncate"] = "true"

    df.write.jdbc(
        url=POSTGRES_URL,
        table=table,
        mode=mode,
        properties=props
    )
