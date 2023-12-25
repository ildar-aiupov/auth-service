import os
from logging import config as logging_config

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

from core.logger import LOGGING


logging_config.dictConfig(LOGGING)
load_dotenv()


class Settings(BaseSettings):
    project_name: str = "auth"
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_mode: bool = False
    authjwt_secret_key: str = "secret"
    authjwt_denylist_enabled: bool = True
    authjwt_denylist_token_checks: set = {"access"}
    authjwt_access_token_expires: int = 3600
    authjwt_refresh_token_expires: int = 3600

    # настройки redis
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_cache_time: int = 3600

    # настройки postgres
    postgres_user: str = "rexample"
    postgres_password: str = "rexample"
    db_host: str = "postgres"
    db_port: int = 5432
    db_name: str = "rexample"
    users_tablename: str = "users"
    roles_tablename: str = "roles"
    visits_tablename: str = "visits"


settings = Settings()
