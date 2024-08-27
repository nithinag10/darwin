from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str
    mysql_password: str
    mysql_db: str
    azure_storage_connection_string: str
    azure_storage_container_name: str

    class Config:
        env_file = ".env"


settings = Settings()
