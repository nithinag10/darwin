from typing import Optional
from models.Product import Product
import logging
import aiomysql

logger = logging.getLogger(__name__)

class ProductRepository:
    def __init__(self, db_con):
        self.db_con = db_con

    async def create_product(self, product: Product) -> int:
        query = """
        INSERT INTO Products (project_id, name, custom_instructions, created_at, updated_at)
        VALUES (%s, %s, %s, NOW(), NOW());
        """
        try:
            async with self.db_con.cursor() as cur:
                await cur.execute(query, (
                    product.project_id,
                    product.name,
                    product.custom_instructions
                ))
                # No commit here; handled at controller level
                product_id = cur.lastrowid
                logger.info(f"Inserted Product with ID: {product_id}")
                return product_id
        except Exception as e:
            logger.error(f"Error creating product: {e}")
            raise e

    async def get_product_by_id(self, product_id: int) -> Optional[Product]:
        query = "SELECT * FROM Products WHERE id = %s;"
        try:
            async with self.db_con.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(query, (product_id,))
                row = await cur.fetchone()
                return Product(**row) if row else None
        except Exception as e:
            logger.error(f"Error fetching product with ID {product_id}: {e}")
            raise e