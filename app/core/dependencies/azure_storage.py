from app.integrations.storage.azure_blob_storage import AzureStorageService
from app.core.dependencies.config import AppConfig
from app.integrations.storage.azure_blob_storage import AzureStorageService



def get_azure_storage_service() -> AzureStorageService:
    blob_storage_config = AppConfig().storage.blob_storage_config

    return AzureStorageService(
        endpoint_protocol=blob_storage_config.endpoints_protocol,
        account_name=blob_storage_config.account_name,
        account_key=blob_storage_config.account_key,
        pdf_container_name=blob_storage_config.pdf_container,
        image_container_name=blob_storage_config.pdf_container
    )