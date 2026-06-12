import redis
from fastapi import HTTPException, status, Depends
from app.config import settings
from app.auth import verify_api_key

r = redis.from_url(settings.REDIS_URL)

def check_rate_limit(user_id: str = Depends(verify_api_key)):
    key = f"rate_limit:{user_id}"
    current_requests = r.get(key)
    
    if current_requests and int(current_requests) >= settings.RATE_LIMIT_PER_MINUTE:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Bạn đã vượt quá giới hạn request cho phép (10 req/phút)!"
        )
    
    # Tăng lượt đếm và đặt hết hạn sau 60 giây
    r.incr(key)
    if r.ttl(key) == -1:
        r.expire(key, 60)