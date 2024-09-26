# services/blob_storage_service.py
from azure.storage.blob.aio import BlobServiceClient, BlobClient
from azure.storage.blob import ContentSettings
import logging
from azure.core.exceptions import AzureError

logger = logging.getLogger(__name__)

class BlobStorageService:
    def __init__(self, connection_string: str, container_name: str):
        """
        Initializes the BlobStorageService with the given connection string and container name.
        """
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
            # Download the blob's content
            download_stream = await self.blob_service_client.download_blob()
            data = await download_stream.readall()
            logger.info(f"Downloaded blob: {blob_name}")
            return data
        except Exception as e:
            logger.error(f"Error downloading blob {blob_name}: {e}")
            raise e

    async def download_blob_by_url(self, blob_url: str) -> bytes:
        """
        Downloads a blob's content using its URL asynchronously.

        :param blob_url: The full URL of the blob to download.
        :return: The content of the blob as bytes.
        """
        try:
            logger.debug(f"Creating BlobClient from URL: {blob_url}")
            # Initialize BlobClient using the blob URL and credentials from BlobServiceClient
            blob_client = BlobClient.from_blob_url(blob_url, credential=self.blob_service_client.credential)
            
            logger.debug("Initiating blob download.")
            # Download the blob's content
            download_stream = await blob_client.download_blob()
            data = await download_stream.readall()  # readall() is an async method
            
            logger.info(f"Downloaded blob from URL: {blob_url} (Size: {len(data)} bytes)")
            return data
        except AzureError as e:
            logger.error(f"Azure Error downloading blob from URL {blob_url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error downloading blob from URL {blob_url}: {e}")
            raise

    async def close(self):
        """
        Closes the BlobServiceClient.
        """
        try:
            await self.blob_service_client.close()
            logger.info("Closed BlobServiceClient.")
        except Exception as e:
            logger.error(f"Error closing BlobServiceClient: {e}")
            raise