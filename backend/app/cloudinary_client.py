from urllib.parse import urlparse

import cloudinary
import cloudinary.uploader

from app.config import settings

_parsed = urlparse(settings.cloudinary_url)
cloudinary.config(
    cloud_name=_parsed.hostname,
    api_key=_parsed.username,
    api_secret=_parsed.password,
)


def upload_image(file_bytes: bytes, folder: str) -> str:
    result = cloudinary.uploader.upload(file_bytes, folder=folder, resource_type="image")
    return result["secure_url"]
