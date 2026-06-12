import json
import redis
from fastapi import FastAPI, Depends
from app.config import settings
from app.auth import verify_api_key
from app.rate_limiter import check_rate_limit
from app.cost_guard import check_budget

app = FastAPI(title="Production AI Agent")
r = redis.from_url(settings.REDIS_URL)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ready")
def ready():
    try:
        r.ping()
        return {"status": "ready"}
    except Exception:
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=503, content={"status": "not ready"})

@app.post("/ask")
def ask(
    question: str,
    user_id: str = Depends(verify_api_key),
    _rate: None = Depends(check_rate_limit),
    _budget: None = Depends(check_budget)
):
    # 1. Lấy lịch sử hội thoại stateless từ Redis
    history_key = f"history:{user_id}"
    history = r.lrange(history_key, 0, -1)
    
    # 2. Xử lý câu trả lời của AI (Mock LLM)
    bot_response = f"[Mock LLM] Trả lời cho câu hỏi '{question}' từ cụm cluster."
    
    # 3. Lưu cặp câu hỏi-trả lời mới vào Redis dạng JSON string
    turn_data = {"question": question, "answer": bot_response}
    r.rpush(history_key, json.dumps(turn_data))
    r.expire(history_key, 3600)  # Lưu lịch sử trong 1 tiếng
    
    return {
        "user_id": user_id,
        "response": bot_response,
        "history_count": len(history) + 1
    }