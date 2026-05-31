from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    app_name: str = "MultiPublisher"
    debug: bool = True
    data_dir: Path = Path(__file__).parent.parent / "data"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    model_config = {"env_prefix": "MP_", "env_file": ".env"}


settings = Settings()
