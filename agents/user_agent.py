import logging  # Importing logging module

# Configure logging
logging.basicConfig(level=logging.DEBUG)  # Set logging level to DEBUG
logger = logging.getLogger(__name__)  # Create a logger

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

        logger.debug(f"Initializing UserAgent with model_api: {model_api} and model_name: {model_name}")  # Debug log

        if model_api == "groq":
            self.llm = ChatGroq(api_key=settings.model_api_key, temperature=settings.temperature, model_name=model_name)
            logger.debug("Using ChatGroq model")  # Debug log
        elif model_api == "openai":
            self.llm = ChatOpenAI(
                api_key=settings.openai_api_key,
                temperature=settings.temperature,
                model_name=model_name
            )
            logger.debug("Using ChatOpenAI model")  # Debug log
        else:
            logger.error("Unsupported model API")  # Error log
            raise ValueError("Unsupported model API")

    async def simulate_interaction(self, scenario: str, product_info: str) -> str:
        logger.debug(f"Simulating interaction with scenario: {scenario} and product_info: {product_info}")  # Debug log
        
        dummy_agent_characteristics = {
            "name": "Test Agent",
            "age": 5,
            "type": "virtual assistant",
            "language": "English",
            "skills": ["chatting", "information retrieval", "task management"]
        }
        
        messages = [
            HumanMessage(content=USER_AGENT_PROMPT.format(**dummy_agent_characteristics)),
            HumanMessage(content=f"Scenario: {scenario}\nProduct Info: {product_info}\nSimulate your interaction:")
        ]
        response = await self.llm.ainvoke(messages)
        logger.debug("Received response from model")
        return response.content