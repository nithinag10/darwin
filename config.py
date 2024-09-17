from pydantic_settings import BaseSettings
from secrets import token_urlsafe

class Settings(BaseSettings):
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str
    mysql_password: str
    mysql_db: str
    azure_storage_connection_string: str
    azure_storage_container_name: str
    secret_key: str = token_urlsafe(32)

        # Added settings for model configuration
    model_api: str = "groq"  # Options: "groq", "openai"
    model_name: str = "mixtral-8x7b-32768"  # Default model name
    temperature: float = 0.9  # Default temperature for LLMs
    model_api_key: str
    
    class Config:
        env_file = ".env"


settings = Settings()
