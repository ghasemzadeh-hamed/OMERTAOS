import os


class Settings:
    MEMORY_URL: str = os.getenv("AION_MEMORY_URL", "http://aion-memory:8080")
    REGISTRY_URL: str = os.getenv("AION_MODEL_REGISTRY_URL", "http://aion-model-registry:8081")
    BASE_MODEL_NAME: str = os.getenv("AION_BASE_MODEL_NAME", "aion-base")
    MIN_REWARD: float = float(os.getenv("AION_SEAL_MIN_REWARD", "0.7"))
    IMPROVEMENT_THRESHOLD: float = float(os.getenv("AION_SEAL_IMPROVEMENT_THRESHOLD", "0.01"))
    MAX_EDITS: int = int(os.getenv("AION_SEAL_MAX_EDITS", "512"))
    OUTPUT_DIR: str = os.getenv("AION_SEAL_OUTPUT_DIR", "/models")


settings = Settings()
