import os
from dotenv import load_dotenv

load_dotenv()

# jdbc:postgresql://HOST:PORT/DB_NAME

POSTGRES_URL = (
    f"jdbc:postgresql://{os.getenv('POSTGRES_HOST')}:"
    f"{os.getenv('POSTGRES_PORT')}/"
    f"{os.getenv('POSTGRES_DB')}"
)

POSTGRES_PROPERTIES = {
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "driver": "org.postgresql.Driver"
}