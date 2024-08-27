from models.User import User
from typing import List


class UserRepository:
    def __init__(self, db):
        self.db = db

    async def create(self, user: User) -> int:
        query = """
        INSERT INTO users (name)
        VALUES (%s)
        """
        values = (user.name,)
        await self.db.execute(query, values)
        return self.db.lastrowid

    async def get_by_id(self, user_id: int) -> User:
        query = "SELECT * FROM users WHERE id = %s"
        await self.db.execute(query, (user_id,))
        result = await self.db.fetchone()
        if result:
            return User(**result)
        return None

    async def get_all(self) -> List[User]:
        query = "SELECT * FROM users"
        await self.db.execute(query)
        results = await self.db.fetchall()
        return [User(**row) for row in results]

    async def update(self, user: User) -> bool:
        query = """
        UPDATE users
        SET name = %s
        WHERE id = %s
        """
        values = (user.name, user.id)
        await self.db.execute(query, values)
        return self.db.rowcount > 0

    async def delete(self, user_id: int) -> bool:
        query = "DELETE FROM users WHERE id = %s"
        await self.db.execute(query, (user_id,))
        return self.db.rowcount > 0
