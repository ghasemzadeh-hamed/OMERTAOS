import os


class Settings:
    DB_URL: str = os.getenv("AION_MEMORY_DB_URL", "sqlite:///./aion_memory.db")


settings = Settings()
