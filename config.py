from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    SQL_USER: str
    SQL_PASSWORD: str
    SQL_IP: str
    SQL_PORT: int
    SQL_NAME: str

    MONGO_NAME: str
    MONGO_IP: str
    MONGO_PORT: int

    REDIS_IP: str
    REDIS_PORT: int
    REDIS_NAME: str


    @property
    def DATABASE_SQL_URL(self):
        return f"postgresql+asyncpg://{self.SQL_USER}:{self.SQL_PASSWORD}@{self.SQL_IP}:{self.SQL_PORT}/{self.SQL_NAME}"

    @property
    def DATABASE_MONGO_URL(self):
        return f"mongodb://{self.MONGO_IP}:{self.MONGO_PORT}"


    @property
    def DATABASE_REDIS_URL(self):
        return f"redis://{self.REDIS_IP}:{self.REDIS_PORT}/{self.REDIS_NAME}"

    class Config:
        env_file = ".env"

settings = Settings()

