# services/blob_storage_service.py
from azure.storage.blob.aio import BlobServiceClient
from azure.storage.blob import ContentSettings
import os
import logging

logger = logging.getLogger(__name__)

class BlobStorageService:
    def __init__(self, connection_string: str, container_name: str):
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_name = container_name

    async def upload_blob(self, blob_name: str, data: bytes, content_type: str) -> str:
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            await container_client.create_container(ignore_if_exists=True)

            blob_client = container_client.get_blob_client(blob_name)
            await blob_client.upload_blob(data, overwrite=True, content_settings=ContentSettings(content_type=content_type))
            blob_url = blob_client.url
            logger.info(f"Uploaded blob: {blob_url}")
            return blob_url
        except Exception as e:
            logger.error(f"Error uploading blob {blob_name}: {e}")
            raise e