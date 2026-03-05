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


# TODO: Make 2 separate classes for local and azure config each with pdf, images and archive directory environment
@dataclass
class LocalStorageConfig:
    pdf_dir: str = os.getenv("LOCAL_PDF_DIR", "")
    images_dir: str = os.getenv("LOCAL_IMAGES_DIR", "")
    archive_dir: str = os.getenv("LOCAL_ARCHIVE_DIR", "")


class AzureBlobStorageConfig:
    endpoints_protocol: str = "https"
    account_name: str = os.getenv("ACCOUNT_NAME", "")
    account_key: str = os.getenv("ACCOUNT_KEY", "")
    pdf_container: str = os.getenv("PDF_CONTAINER_NAME", "")
    image_container: str = os.getenv("IMAGE_CONTAINER_NAME", "")


@dataclass
class StorageConfig:
    local_storage_config: LocalStorageConfig = field(default_factory=LocalStorageConfig)
    # azure_blob_storage_config: AzureStorageConfig = field(default_factory=AzureStorageConfig)
    blob_storage_config: AzureBlobStorageConfig = field(default_factory=AzureBlobStorageConfig)


# TODO: Use this config for token creation and validation
@dataclass
class JWTConfig:
    expiration_minutes: int = int(os.getenv("JWT_EXPIRATION_MINUTES", 60))
    secret_key: str = os.getenv("JWT_SECRET_KEY", "")


@dataclass
class APIKeys:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")


@dataclass
class AppConfig:
    local_db: LocalDBConfig = field(default_factory=LocalDBConfig)
    azure_db: AzureDBConfig = field(default_factory=AzureDBConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    jwt_config: JWTConfig = field(default_factory=JWTConfig)
    api_keys: APIKeys = field(default_factory=APIKeys)


# FIXME: Make the ensure directories function here to ensure all the required directories on application startup
def ensure_directories():
    raise NotImplementedError()
