from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage
from agents.utils.prompt_definitions import USER_AGENT_PROMPT
from agents.utils.prompt_provider import PromptProvider
from config import settings  # Importing settings from config.py

class UserAgent:
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

    async def simulate_interaction(self, scenario: str, product_info: str) -> str:
        messages = [
            HumanMessage(content=USER_AGENT_PROMPT.format(**self.characteristics)),
            HumanMessage(content=f"Scenario: {scenario}\nProduct Info: {product_info}\nSimulate your interaction:")
        ]
        response = await self.llm.ainvoke(messages)
        return response.content