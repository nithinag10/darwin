from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage
from agents.utils.prompt_definitions import PROJECT_MANAGER_PROMPT
from agents.utils.prompt_provider import PromptProvider
from config import settings 

class ProjectManagerAgent:
    def __init__(self, agent_characteristics: dict):
        self.characteristics = agent_characteristics
        model_api = settings.model_api  # Retrieved from config.py
        model_name = settings.model_name  # Retrieved from config.py

        if model_api == "groq":
            self.llm = ChatGroq(api_key=settings.model_api_key, temperature=settings.temperature, model_name=model_name)
        elif model_api == "openai":
            self.llm = ChatOpenAI(
                api_key=settings.openai_api_key,
                temperature=settings.temperature,
                model_name=model_name
            )
        else:
            raise ValueError("Unsupported model API")

    async def define_evaluation_scope(self, evaluation_context: str) -> str:
        messages = [
            HumanMessage(content=PROJECT_MANAGER_PROMPT),
            HumanMessage(content=f"Define the evaluation scope for: {evaluation_context}")
        ]
        response = await self.llm.ainvoke(messages)
        return response.content