from azure.storage.blob import BlobServiceClient
from app.core.dependencies.config import AppConfig
from app.utils.utils import generate_azure_connection_string


class AzureStorageService:
    def __init__(
            self,
            endpoint_protocol: str,
            account_name: str,
            account_key: str,
            pdf_container_name: str,
            image_container_name: str
    ):
        self.blob_service_client = BlobServiceClient.from_connection_string(
            generate_azure_connection_string(endpoint_protocol, account_name,account_key),
            connection_timeout=300,
            read_timeout=300
        )
        self.pdf_container_name = pdf_container_name
        self.image_container_name = image_container_name

    def get_container_client(self, file_type: str):
        if file_type.lower() == "image":
            container_name = self.image_container_name
        elif file_type.lower() == "pdf":
            container_name = self.pdf_container_name
        else:
            raise ValueError("Unsupported file type")

        return self.blob_service_client.get_container_client(container_name)


    def upload_file(self, file_path: str, blob_name: str, file_type: str):
        container_client = self.get_container_client(file_type)
        print('Uploading file path: ', file_path)
        print('Uploading blob name: ', blob_name)
        print('Uploading file type: ', file_type)

        with open(file_path, "rb") as data:
            container_client.upload_blob(blob_name, data, overwrite=True)
