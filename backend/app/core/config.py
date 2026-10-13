from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.rate_limit import parse_rate

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    database_url: str
    secret_key: str
    access_token_expire_minutes: int = 60
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    algorithm: str = "HS256"

    # Rate limiting per client IP, "<count>/<second|minute|hour|day>"
    rate_limit_enabled: bool = True
    rate_limit_login: str = "10/minute"
    rate_limit_apply: str = "20/hour"

    # Optional SMTP; without smtp_host no email is sent (application is still saved)
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from: str = "noreply@jobboard.local"
    smtp_starttls: bool = True

    @field_validator("secret_key")
    @classmethod
    def secret_key_long_enough(cls, value: str) -> str:
        if len(value) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        if value.lower().startswith("change-me"):
            raise ValueError(
                "SECRET_KEY is still the placeholder from .env.example: "
                'generate one with python3 -c "import secrets; print(secrets.token_hex(32))"'
            )
        return value

    @field_validator("rate_limit_login", "rate_limit_apply")
    @classmethod
    def rate_is_valid(cls, value: str) -> str:
        parse_rate(value)  # raises ValueError on a malformed rate
        return value

    @property
    def cors_origins_list(self) -> list[str]:
        """CORS_ORIGINS is a comma-separated list of origins."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()  # type: ignore[call-arg]
