from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    database_url: str = ''
    bot_token: str = ''
    admins_list: set[int] = Field(default_factory=set)
    log_level: str = ''
    payment_token: str = ''

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


config = Config()
