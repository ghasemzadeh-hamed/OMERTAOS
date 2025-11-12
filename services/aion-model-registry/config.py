import os


class Settings:
    DB_URL: str = os.getenv("AION_MODEL_REGISTRY_DB_URL", "sqlite:///./aion_model_registry.db")


settings = Settings()
