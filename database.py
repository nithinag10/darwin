from config import settings
import aiomysql

db_pool = None


async def init_db():
    global db_pool
    db_pool = await aiomysql.create_pool(
        host=settings.mysql_host,
        port=settings.mysql_port,
        user=settings.mysql_user,
        password=settings.mysql_password,
        db=settings.mysql_db,
        autocommit=True
    )


async def close_db():
    global db_pool
    if db_pool:
        db_pool.close()
        await db_pool.wait_closed()

async def get_db_conn():
    if db_pool is None:
        await init_db()
    async with db_pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            yield conn, cur  # Yield connection and cursor

async def transaction():
    async with db_pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await conn.begin()  # Start a transaction
            try:
                yield conn, cur  # Yield connection and cursor for transaction
                await conn.commit()  # Commit the transaction if successful
            except Exception as e:
                await conn.rollback()  # Rollback on error
                raise e

