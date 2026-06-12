from fastapi import Header, HTTPException, status
from app.config import settings

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.AGENT_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mã API Key không hợp lệ!"
        )
    return "user_123"  # Giả định trả về user_id cố định từ API Key này