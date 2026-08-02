from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    mongodb_uri: str
    jwt_secret: str
    cloudinary_url: str = ""
    cookie_secure: bool = True
    frontend_origin: str = "http://localhost:3000"
    ai_model_weights_path: str = "ai_model/weights/best.pt"
    ai_class_names: str = "cavity,plaque,gingivitis"


settings = Settings()
