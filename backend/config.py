from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:8000"]
    max_upload_size_mb: int = 500
    wsl_python: str = "python3"
    r_home: str = ""
    dev_mode: bool = False

    model_config = {"env_prefix": "SOFTNET_", "env_file": ".env"}


settings = Settings()
