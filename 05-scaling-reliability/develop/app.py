"""
BASIC — Health Check + Graceful Shutdown

Hai tính năng tối thiểu cần có trước khi deploy:
  1. GET /health  — liveness: "agent có còn sống không?"
  2. GET /ready   — readiness: "agent có sẵn sàng nhận request chưa?"
  3. Graceful shutdown: hoàn thành request hiện tại trước khi tắt

Chạy:
    python app.py

Test health check:
    curl http://localhost:8000/health
    curl http://localhost:8000/ready

Simulate shutdown:
    # Trong terminal khác
    kill -SIGTERM <pid>
    # Xem agent log graceful shutdown message
"""
import os
import time
import signal
import logging
import sys
from datetime import datetime, timezone
from contextlib import asynccontextmanager


from fastapi import FastAPI, HTTPException, Request
import uvicorn
from utils.mock_llm import ask

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

START_TIME = time.time()
_is_ready = False
_in_flight_requests = 0  # đếm số request đang xử lý


from fastapi.responses import JSONResponse
import redis
import json
# ví dụ Postgres client
# import psycopg2
# db = psycopg2.connect(os.getenv(...))

# Initialize Redis client from environment, but tolerate missing Redis (for exercises)
try:
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    # quick ping to verify connection
    r.ping()
    logger.info(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
except Exception:
    r = None
    logger.warning("Redis not available; conversation history disabled")


def get_history(user_id: str, limit: int = 50):
    if not r:
        return []
    try:
        return r.lrange(f"history:{user_id}", 0, limit - 1)
    except Exception:
        logger.exception("Error reading history from Redis")
        return []


def append_history(user_id: str, entry: str, max_len: int = 100):
    if not r:
        return
    try:
        r.lpush(f"history:{user_id}", entry)
        r.ltrim(f"history:{user_id}", 0, max_len - 1)
    except Exception:
        logger.exception("Error appending history to Redis")

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _is_ready

    # ── Startup ──
    logger.info("Agent starting up...")
    logger.info("Loading model and checking dependencies...")
    time.sleep(0.2)  # simulate startup time
    _is_ready = True
    logger.info("✅ Agent is ready!")

    yield

    # ── Shutdown ──
    _is_ready = False
    logger.info("🔄 Graceful shutdown initiated...")

    # Chờ request đang xử lý hoàn thành (tối đa 30 giây)
    timeout = 30
    elapsed = 0
    while _in_flight_requests > 0 and elapsed < timeout:
        logger.info(f"Waiting for {_in_flight_requests} in-flight requests...")
        time.sleep(1)
        elapsed += 1

    logger.info("✅ Shutdown complete")


app = FastAPI(title="Agent — Health Check Demo", lifespan=lifespan)


@app.middleware("http")
async def track_requests(request, call_next):
    """Theo dõi số request đang xử lý."""
    global _in_flight_requests
    _in_flight_requests += 1
    try:
        response = await call_next(request)
        return response
    finally:
        _in_flight_requests -= 1


# ──────────────────────────────────────────────────────────
# Business Logic
# ──────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "AI Agent with health checks!"}


@app.post("/ask")
async def ask_agent(request: Request):
    """Endpoint now expects JSON: {"user_id":"...","question":"..."}
    Stores conversation history in Redis (stateless design).
    """
    body = await request.json()
    user_id = body.get("user_id")
    question = body.get("question")

    if not user_id or not question:
        raise HTTPException(status_code=422, detail="user_id and question are required")

    if not _is_ready:
        raise HTTPException(503, "Agent not ready")

    # Load history from Redis (stateless)
    history = get_history(user_id)

    # Call LLM (mock) — in real app we'd pass history to model
    answer = ask(question)

    # Append QA pair to Redis history as JSON string
    entry = json.dumps({
        "question": question,
        "answer": answer,
        "ts": datetime.now(timezone.utc).isoformat(),
    })
    append_history(user_id, entry)

    return {"answer": answer, "history_count": len(history) + 1}


# ──────────────────────────────────────────────────────────
# HEALTH CHECKS — Phần quan trọng nhất của file này
# ──────────────────────────────────────────────────────────

@app.get("/health")
def health():
    """
    LIVENESS PROBE — "Agent có còn sống không?"

    Cloud platform (Railway, Render, K8s) gọi endpoint này định kỳ.
    Nếu trả về non-200 hoặc timeout → platform restart container.

    Nên trả về:
    - status: "ok" hoặc "degraded"
    - uptime: seconds
    - version: để biết đang chạy version nào
    """
    # uptime = round(time.time() - START_TIME, 1)

    # # Kiểm tra dependencies quan trọng
    # checks = {}

    # # Check memory (ví dụ đơn giản)
    # try:
    #     import psutil
    #     mem = psutil.virtual_memory()
    #     checks["memory"] = {
    #         "status": "ok" if mem.percent < 90 else "degraded",
    #         "used_percent": mem.percent,
    #     }
    # except ImportError:
    #     checks["memory"] = {"status": "ok", "note": "psutil not installed"}

    # overall_status = "ok" if all(
    #     v.get("status") == "ok" for v in checks.values()
    # ) else "degraded"

    # return {
    #     "status": overall_status,
    #     "uptime_seconds": uptime,
    #     "version": "1.0.0",
    #     "environment": os.getenv("ENVIRONMENT", "development"),
    #     "timestamp": datetime.now(timezone.utc).isoformat(),
    #     "checks": checks,
    # }
    return {"status": "ok"}


@app.get("/ready")
def ready():
    """
    READINESS PROBE — "Agent có sẵn sàng nhận request chưa?"

    Load balancer dùng endpoint này để quyết định có route
    traffic vào instance này không.

    Trả về 503 khi:
    - Đang khởi động (model chưa load xong)
    - Đang shutdown
    - Database/dependencies chưa connect
    """
    # if not _is_ready:
    #     raise HTTPException(
    #         status_code=503,
    #         detail="Agent not ready. Check back in a few seconds.",
    #     )
    # return {
    #     "ready": True,
    #     "in_flight_requests": _in_flight_requests,
    # }
    try:
        # Check Redis
        r.ping()
        # Check database
        db.execute("SELECT 1")
        return {"status": "ready"}
    except:
        return JSONResponse(
            status_code=503,
            content={"status": "not ready"}
        )



# ──────────────────────────────────────────────────────────
# GRACEFUL SHUTDOWN
# ──────────────────────────────────────────────────────────

def handle_sigterm(signum, frame):
    """
    SIGTERM là signal platform gửi khi muốn dừng container.
    Khác với SIGKILL (không thể catch được).

    uvicorn bắt SIGTERM tự động và gọi lifespan shutdown.
    Hàm này để log thêm thông tin.
    """
    logger.info(f"Received signal {signum} — initiating graceful shutdown handler")

    # 1) Stop accepting new requests
    try:
        global _is_ready
        _is_ready = False
    except Exception:
        pass

    # 2) Wait for in-flight requests to finish (max 30s)
    timeout = 30
    waited = 0
    while _in_flight_requests > 0 and waited < timeout:
        logger.info(f"Waiting for {_in_flight_requests} in-flight requests to finish...")
        time.sleep(1)
        waited += 1

    if _in_flight_requests > 0:
        logger.warning(f"Shutdown timeout reached; {_in_flight_requests} requests still in-flight")
    else:
        logger.info("All in-flight requests completed")

    # 3) Close external connections if present
    try:
        if 'r' in globals() and getattr(r, 'close', None):
            try:
                r.close()
                logger.info("Closed Redis connection")
            except Exception:
                logger.exception("Error closing Redis connection")
    except Exception:
        logger.debug("No Redis client to close")

    try:
        if 'db' in globals() and getattr(db, 'close', None):
            try:
                db.close()
                logger.info("Closed DB connection")
            except Exception:
                logger.exception("Error closing DB connection")
    except Exception:
        logger.debug("No DB client to close")

    # 4) Exit process
    logger.info("Exiting process now")
    try:
        sys.exit(0)
    except SystemExit:
        # ensure process terminates
        os._exit(0)


signal.signal(signal.SIGTERM, handle_sigterm)
signal.signal(signal.SIGINT, handle_sigterm)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting agent on port {port}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        # ✅ Cho phép graceful shutdown
        timeout_graceful_shutdown=30,
    )
