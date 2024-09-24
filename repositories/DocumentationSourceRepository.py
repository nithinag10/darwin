from models.documentation_source import DocumentationSourceSchema
from typing import List, Optional
import aiomysql
import logging

logger = logging.getLogger(__name__)

class DocumentationSourceRepository:
    def __init__(self, db_con):
        self.db_con = db_con

    async def create(self, documentation_source: DocumentationSourceSchema) -> int:
        query = """
        INSERT INTO DocumentationSources (product_id, type, url, created_at, updated_at, storage_url, file_size, content_type, fetched_at)
        VALUES (%s, %s, %s, NOW(), NOW(), %s, %s, %s, %s);
        """
        try:
            async with self.db_con.cursor() as cur:
                await cur.execute(query, (
                    documentation_source.product_id,
                    documentation_source.type,
                    documentation_source.url,
                    documentation_source.storage_url,
                    documentation_source.file_size,
                    documentation_source.content_type,
                    documentation_source.fetched_at
                ))
                await self.db_con.commit()
                logger.info(f"Inserted DocumentationSource with ID: {cur.lastrowid}")
                return cur.lastrowid  # Return the ID of the newly created documentation source
        except Exception as e:
            logger.error(f"Error creating DocumentationSource: {e}")
            await self.db_con.rollback()
            raise e

    async def get_by_product_id(self, product_id: int) -> List[DocumentationSourceSchema]:
        query = "SELECT * FROM DocumentationSources WHERE product_id = %s;"
        try:
            async with self.db_con.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(query, (product_id,))
                rows = await cur.fetchall()
                return [DocumentationSourceSchema(**row) for row in rows] if rows else []
        except Exception as e:
            logger.error(f"Error fetching DocumentationSources for product_id {product_id}: {e}")
            raise e

    async def get_by_id(self, documentation_source_id: int) -> Optional[DocumentationSourceSchema]:
        query = "SELECT * FROM DocumentationSources WHERE id = %s;"
        try:
            async with self.db_con.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(query, (documentation_source_id,))
                row = await cur.fetchone()
                return DocumentationSourceSchema(**row) if row else None
        except Exception as e:
            logger.error(f"Error fetching DocumentationSource with ID {documentation_source_id}: {e}")
            raise e

    async def update(self, documentation_source: DocumentationSourceSchema) -> bool:
        query = """
        UPDATE DocumentationSources 
        SET type = %s, url = %s, updated_at = NOW(), storage_url = %s, file_size = %s, content_type = %s, fetched_at = %s
        WHERE id = %s;
        """
        try:
            async with self.db_con.cursor() as cur:
                await cur.execute(query, (
                    documentation_source.type,
                    documentation_source.url,
                    documentation_source.storage_url,
                    documentation_source.file_size,
                    documentation_source.content_type,
                    documentation_source.fetched_at,
                    documentation_source.id
                ))
                await self.db_con.commit()
                logger.info(f"Updated DocumentationSource with ID: {documentation_source.id}")
                return cur.rowcount > 0  # Return True if the update was successful
        except Exception as e:
            logger.error(f"Error updating DocumentationSource with ID {documentation_source.id}: {e}")
            await self.db_con.rollback()
            raise e

    async def delete(self, documentation_source_id: int) -> bool:
        query = "DELETE FROM DocumentationSources WHERE id = %s;"
        try:
            async with self.db_con.cursor() as cur:
                await cur.execute(query, (documentation_source_id,))
                await self.db_con.commit()
                logger.info(f"Deleted DocumentationSource with ID: {documentation_source_id}")
                return cur.rowcount > 0  # Return True if the deletion was successful
        except Exception as e:
            logger.error(f"Error deleting DocumentationSource with ID {documentation_source_id}: {e}")
            await self.db_con.rollback()
            raise e
        
    async def get_sources_by_product_id(self, product_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieves documentation sources filtered by product_id if provided.
        :param product_id: (Optional) The product ID to filter sources.
        :return: List of documentation source dictionaries.
        """
        query = "SELECT * FROM DocumentationSources"
        params = ()
        if product_id is not None:
            query += " WHERE product_id = %s"
            params = (product_id,)
        
        async with aiomysql.connect(**self.db_config) as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, params)
                results = await cursor.fetchall()
        return results