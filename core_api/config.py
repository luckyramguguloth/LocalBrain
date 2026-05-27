import os

# Robust custom .env loader to load variables without any external dependency
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                key_val = line.split("=", 1)
                if len(key_val) == 2:
                    k, v = key_val[0].strip(), key_val[1].strip()
                    # Remove surrounding quotes if present
                    if v.startswith(('"', "'")) and v.endswith(('"', "'")):
                        v = v[1:-1]
                    os.environ[k] = v

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "secure_memory_neo4j")
    POSTGRES_DSN: str = os.getenv("POSTGRES_DSN", "postgresql://memory_admin:secure_memory_pg@localhost:5433/memory_metadata")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    APP_NAME: str = "Enterprise Memory Engine API"

settings = Settings()
