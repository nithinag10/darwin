import logging  # {{ edit_1 }}

# Configure logging
logging.basicConfig(level=logging.DEBUG)  # {{ edit_2 }}

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

        logging.debug(f"Initializing ProjectManagerAgent with model_api: {model_api} and model_name: {model_name}")  # {{ edit_3 }}

        if model_api == "groq":
            self.llm = ChatGroq(api_key=settings.model_api_key, temperature=settings.temperature, model_name=model_name)
        elif model_api == "openai":
            self.llm = ChatOpenAI(
                api_key=settings.openai_api_key,
                temperature=settings.temperature,
                model_name=model_name
            )
        else:
            logging.error("Unsupported model API")  # {{ edit_4 }}
            raise ValueError("Unsupported model API")

    async def define_evaluation_scope(self, evaluation_context: str) -> str:
        logging.debug(f"Defining evaluation scope for context: {evaluation_context}")  # {{ edit_5 }}
        messages = [
            HumanMessage(content=PROJECT_MANAGER_PROMPT),
            HumanMessage(content=f"Define the evaluation scope for: {evaluation_context}")
        ]
        response = await self.llm.ainvoke(messages)
        logging.debug(f"Received response: {response.content}")
        return response.content