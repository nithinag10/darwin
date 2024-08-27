from functools import wraps
from fastapi import HTTPException
from database import get_db_conn

def transaction(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        async for db_connection in get_db_conn():
            try:
                await db_connection.execute("START TRANSACTION")
                result = await func(*args, **kwargs, db_con=db_connection)
                await db_connection.execute("COMMIT")
                return result
            except Exception as e:
                await db_connection.execute("ROLLBACK")
                raise HTTPException(status_code=500, detail=f"Error in transaction: {str(e)}")
            finally:
                await db_connection.close()

    return wrapper