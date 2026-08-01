from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    mongodb_uri: str
    jwt_secret: str
    cloudinary_url: str = ""
    cookie_secure: bool = True


settings = Settings()
