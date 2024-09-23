# services/blob_storage_service.py
from azure.storage.blob.aio import BlobServiceClient
from azure.storage.blob import ContentSettings
import logging

logger = logging.getLogger(__name__)

class BlobStorageService:
    def __init__(self, connection_string: str, container_name: str):
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_name = container_name

    async def upload_blob(self, blob_name: str, data: bytes, content_type: str) -> str:
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)

            blob_client = container_client.get_blob_client(blob_name)
            await blob_client.upload_blob(
                data,
                overwrite=True,
                content_settings=ContentSettings(content_type=content_type)
            )
            blob_url = blob_client.url
            logger.info(f"Uploaded blob: {blob_url}")
            return blob_url
        except Exception as e:
            logger.error(f"Error uploading blob {blob_name}: {e}")
            raise e

    async def download_blob(self, blob_name: str) -> bytes:
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            blob_client = container_client.get_blob_client(blob_name)

            # Download the blob's content
            download_stream = await blob_client.download_blob()
            data = await download_stream.readall()
            logger.info(f"Downloaded blob: {blob_name}")
            return data
        except Exception as e:
            logger.error(f"Error downloading blob {blob_name}: {e}")
            raise e

    async def close(self):
        await self.blob_service_client.close()
        logger.info("Closed BlobServiceClient")