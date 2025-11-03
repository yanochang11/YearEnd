from fastapi import Header, HTTPException, status, Security
from fastapi.security import APIKeyHeader

from .config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

async def get_api_key(api_key: str = Security(api_key_header)):
    """
    Dependency to verify the X-API-Key header.

    Compares the provided API key with the one in the settings.
    Raises HTTPException 401 if the key is invalid.
    """
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )
    return api_key
