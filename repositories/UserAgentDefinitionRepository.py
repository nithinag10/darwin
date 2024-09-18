from models.UserAgentDefinition import UserAgentDefinition
from database import get_db_conn

class UserAgentDefinitionRepository:
    def __init__(self, db_con):
        self.db_con = db_con

    async def create(self, user_agent: UserAgentDefinition) -> UserAgentDefinition:
        query = """
        INSERT INTO UserAgentDefinitions (created_by_user_id, name, description, characteristics, is_predefined, is_active, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW());
        """
        async with self.db_con.cursor() as cur:
            await cur.execute(query, (user_agent.created_by_user_id, user_agent.name, user_agent.description, user_agent.characteristics, user_agent.is_predefined, user_agent.is_active))
            user_agent.id = cur.lastrowid  # Get the last inserted ID
            return user_agent

    async def get_all(self) -> list:
        query = "SELECT * FROM UserAgentDefinitions WHERE is_predefined = TRUE;"
        async with self.db_con.cursor() as cur:
            await cur.execute(query)
            rows = await cur.fetchall()
            return [UserAgentDefinition(**row) for row in rows]
