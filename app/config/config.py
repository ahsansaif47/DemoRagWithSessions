from dataclasses import dataclass
import os
from dotenv import load_dotenv
from dataclasses import dataclass, field

load_dotenv(verbose=True)


@dataclass
class LocalDBConfig:
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = os.getenv("DB_PORT", 5432)
    username: str = os.getenv("DB_USERNAME", "postgres")
    password: str = os.getenv("DB_PASSWORD", "demo-rag123")
    db_name: str = os.getenv("DB_NAME", "demo-rag")


@dataclass
class AzureDBConfig:
    db: str = os.getenv("AZURE_DB", "")


@dataclass
class StorageConfig:
    local_storage: str = os.getenv("LOCAL_STORE", "")
    azure_blob_storage: str = os.getenv("AZURE_BLOB_STORAGE", "")


@dataclass
class AppConfig:
    local_db: LocalDBConfig = field(default_factory=LocalDBConfig)
    azure_db: AzureDBConfig = field(default_factory=AzureDBConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)


# FIXME: Make the ensure directories function here to ensure all the required directories on application startup
def ensure_directories():
    raise NotImplementedError()
