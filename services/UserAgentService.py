from repositories.UserAgentDefinitionRepository import UserAgentDefinitionRepository
from models.UserAgentDefinition import UserAgentDefinition
import aiomysql
from typing import Optional, Dict

class UserAgentService:
    def __init__(self, db_con):
        self.db_con = db_con
        self.user_agent_repository = UserAgentDefinitionRepository(db_con)  # Instantiated internally

    async def create_user_agent(self, user_agent: UserAgentDefinition) -> UserAgentDefinition:
        return await self.user_agent_repository.create(user_agent)

    async def get_all_predefined_agents(self) -> list:
        return await self.user_agent_repository.get_all()
    
    async def fetch_user_agent_definition(self, user_agent_definition_id: int) -> Optional[Dict]:
        query = "SELECT * FROM UserAgentDefinitions WHERE id = %s AND is_predefined = TRUE;"
        async with self.db_con.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(query, (user_agent_definition_id,))
            row = await cur.fetchone()
            return row if row else None