from .prompt_definitions import (
    PROJECT_MANAGER_PROMPT,
    USER_AGENT_PROMPT,
    DEFAULT_PROMPT
)

class PromptProvider:
    def __init__(self, some_configuration: dict):
        self.config = some_configuration

    def get_prompt(self, prompt_name: str) -> str:
        prompts = {
            "PROJECT_MANAGER_PROMPT": PROJECT_MANAGER_PROMPT,
            "USER_AGENT_PROMPT": USER_AGENT_PROMPT,
            # Add more prompts as needed
        }
        return prompts.get(prompt_name, DEFAULT_PROMPT)
