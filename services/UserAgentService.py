from repositories.UserAgentDefinitionRepository import UserAgentDefinitionRepository
from models.UserAgentDefinition import UserAgentDefinition

class UserAgentService:
    def __init__(self, user_agent_repository: UserAgentDefinitionRepository):
        self.user_agent_repository = user_agent_repository

    async def create_user_agent(self, user_agent: UserAgentDefinition) -> UserAgentDefinition:
        return await self.user_agent_repository.create(user_agent)

    async def get_all_predefined_agents(self) -> list:
        return await self.user_agent_repository.get_all()
