from psycopg_pool import ConnectionPool
from typing import Generator
from psycopg import Connection
# TODO: Remove these import after testing the service layer
from app.utils import database
from app.config import config


def get_database_connection() -> Generator[Connection, None, None]:
    pool = PostgresPool.get_local_pool()
    with pool.connection() as conn:
        yield conn

# TODO: Remove the config and database connection from this file
config = config.AppConfig()
local_db_config = config.local_db


dsn = database.generate_dsn(
    local_db_config.host,
    local_db_config.port,
    local_db_config.username,
    local_db_config.password,
    local_db_config.db_name
)



class PostgresPool:
    _instance = None

    @classmethod
    def init(cls, dsn: str, min_conn: int = 1, max_conn: int = 100):
        if cls._instance is None:
            cls._instance = ConnectionPool(
                conninfo=dsn,
                min_size=min_conn,
                max_size=max_conn,
                open=True
            )
        return cls._instance

    @classmethod
    def get_local_pool(cls) -> ConnectionPool:
        if cls._instance is None:
            raise RuntimeError('Postgres pool not initialized')
        return cls._instance

    # TODO: Call this on graceful shutdown
    @classmethod
    def close(cls):
        if cls._instance is not None:
            cls._instance.close()
            cls._instance = None


PostgresPool.init(dsn)
