from pydantic_settings import BaseSettings
from dotenv import load_dotenv


load_dotenv()


class Settings(BaseSettings):
    base_url: str = "http://fastapi:8000/api/v1"


settings = Settings()
