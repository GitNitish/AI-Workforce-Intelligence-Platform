
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "WorkForceIQ"
    database_url: str = "sqlite:///./workforceiq.db"
    secret_key: str = Field(min_length=32)

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, value: str) -> str:
        if value == "development-secret-key":
            raise ValueError(
                "SECRET_KEY must be replaced with a secure random value."
            )

        if len(value.encode("utf-8")) < 32:
            raise ValueError(
                "SECRET_KEY must contain at least 32 bytes."
            )

        return value

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
