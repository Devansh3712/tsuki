from pydantic import BaseSettings


class EnvVariables(BaseSettings):
    POSTGRES_URI: str
    SECRET_KEY: str
    ISSUER: str
    EMAIL: str
    TOKEN: str
    REFRESH_TOKEN: str
    TOKEN_URI: str
    CLIENT_ID: str
    CLIENT_SECRET: str
    EXPIRY: str

    class Config:
        env_file = ".env"


secrets = EnvVariables()
