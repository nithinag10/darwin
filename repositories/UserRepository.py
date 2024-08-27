from models.User import User
from typing import Dict, Optional, List

class UserRepository:
    def __init__(self, db_connection):
        self.db = db_connection

    async def create_user(self, user: User) -> int:
        query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
        values = (user.name, user.email, user.password)
        await self.db.execute(query, values)
        return self.db.lastrowid

    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        query = "SELECT * FROM users WHERE email = %s"
        await self.db.execute(query, (email,))
        result = await self.db.fetchone()
        return result

    async def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        query = "SELECT * FROM users WHERE id = %s"
        await self.db.execute(query, (user_id,))
        result = await self.db.fetchone()
        return result
