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
    # Grad-CAM needs gradient computation (heavier than plain YOLO inference)
    # and permanently caches a second model in memory after first use --
    # confirmed as the cause of a recurring OOM on Render's free 512MB tier.
    # Defaults on so local dev/demo is unaffected; set to false in Render's
    # env vars for the deployed backend specifically.
    enable_grad_cam: bool = True


settings = Settings()
