import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "Polar Science Knowledge & Outreach Platform"
    APP_VERSION: str = "1.0.0"
    APP_DEBUG: bool = True
    
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    RAW_DATA_DIR: Path = BASE_DIR / "data" / "raw"
    PROCESSED_DATA_DIR: Path = BASE_DIR / "data" / "processed"
    METADATA_DIR: Path = BASE_DIR / "data" / "metadata"
    VECTORSTORE_DIR: Path = BASE_DIR / "data" / "vectorstore"
    
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "polar_science_db")
    
    SQLITE_DB_PATH: Path = BASE_DIR / "data" / "polar_science.db"
    
    @property
    def DATABASE_URL(self) -> str:
        url = os.getenv("DATABASE_URL")
        if url:
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql://", 1)
            return url
        return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        
    @property
    def SQLITE_URL(self) -> str:
        return f"sqlite:///{self.SQLITE_DB_PATH.as_posix()}"

    CHROMA_PERSIST_DIRECTORY: str = str(BASE_DIR / "data" / "vectorstore" / "chroma")
    CHROMA_COLLECTION_NAME: str = "polar_knowledge_base"
    
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "sentence-transformers")
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
    
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "gemini-2.0-flash")
    LLM_TEMPERATURE: float = 0.0

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()

for path in [
    settings.DATA_DIR,
    settings.RAW_DATA_DIR,
    settings.RAW_DATA_DIR / "aws",
    settings.RAW_DATA_DIR / "reports",
    settings.RAW_DATA_DIR / "publications",
    settings.RAW_DATA_DIR / "media",
    settings.PROCESSED_DATA_DIR,
    settings.METADATA_DIR,
    settings.VECTORSTORE_DIR,
]:
    path.mkdir(parents=True, exist_ok=True)
