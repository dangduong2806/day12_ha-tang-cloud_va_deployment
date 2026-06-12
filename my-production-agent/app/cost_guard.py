import redis
from datetime import datetime
from fastapi import HTTPException, status, Depends
from app.config import settings
from app.auth import verify_api_key

r = redis.from_url(settings.REDIS_URL)

def check_budget(user_id: str = Depends(verify_api_key)):
    month_key = datetime.now().strftime("%Y-%m")
    key = f"budget:{user_id}:{month_key}"
    
    current_spending = float(r.get(key) or 0)
    estimated_cost = 0.05  # Giả định mỗi câu hỏi tốn $0.05
    
    if current_spending + estimated_cost > settings.MONTHLY_BUDGET_USD:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Tài khoản đã hết ngân sách sử dụng trong tháng này ($10)!"
        )
    
    # Cộng dồn tiền ảo vào Redis
    r.incrbyfloat(key, estimated_cost)
    if r.ttl(key) == -1:
        r.expire(key, 32 * 24 * 3600)  # Hết hạn sau 32 ngày