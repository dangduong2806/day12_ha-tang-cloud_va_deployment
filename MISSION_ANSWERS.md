#  Delivery Checklist — Day 12 Lab Submission

> **Student Name:** Nguyễn Đăng Dương 
> **Student ID:** 2A202600678
> **Date:** 12/06/2026

---

##  Submission Requirements

Submit a **GitHub repository** containing:

### 1. Mission Answers (40 points)

Create a file `MISSION_ANSWERS.md` with your answers to all exercises:

```markdown
# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. # ❌ Vấn đề 1: API key hardcode trong code
# Nếu push lên GitHub → key bị lộ ngay lập tức

2. # ❌ Vấn đề 2: Không có config management

3. # ❌ Vấn đề 3: Print thay vì proper logging

4. # ❌ Vấn đề 4: Không có health check endpoint
# Nếu agent crash, platform không biết để restart

5. # ❌ Vấn đề 5: Port cố định — không đọc từ environment
# Trên Railway/Render, PORT được inject qua env var
...

### Exercise 1.3: Comparison table
| Feature | Develop | Production | Why Important? |
|---------|---------|------------|----------------|
| Health check  | Không có. Nếu ứng dụng bị treo hoặc crash ngầm, hệ thống bên ngoài hoàn toàn mù tịt.     | Có Endpoint chuyên biệt như /health (Liveness probe) và /ready (Readiness probe).        | Tự động phục hồi: Các nền tảng Cloud (Railway, Render, Kubernetes) dựa vào đây để biết khi nào ứng dụng bị lỗi để tự động khởi động lại (restart) container, hoặc chặn không gửi request vào khi app đang bận khởi tạo.           |

| Logging  | Dùng lệnh print() thủ công, ghi log thô sơ và vô tình in cả thông tin nhạy cảm (Secret Key) ra màn hình.     | Sử dụng Structured Logging (JSON) qua module logging của Python. Tuyệt đối không log dữ liệu nhạy cảm.        | Giám sát diện rộng: Khi lên Cloud, log dạng JSON giúp các hệ thống quản lý log tập trung (như ELK, Grafana Loki, Datadog) dễ dàng tìm kiếm, phân tích cú pháp, vẽ biểu đồ lỗi và kích hoạt cảnh báo (alert) tự động.         |

| Config & Secrets  | Hardcode trực tiếp các chuỗi bí mật như API Key, URL Database vào trong mã nguồn.     | Sử dụng Biến môi trường (Env vars) kết hợp với thư viện như pydantic-settings hoặc python-dotenv. | Bảo mật & Linh hoạt: Giúp không bị lộ private key khi push code lên GitHub. Dễ dàng thay đổi cấu hình giữa các môi trường Dev/Staging/Prod mà không cần sửa một dòng code nào.|

| Shutdown & Network | Tắt đột ngột. Cấu hình cứng host="localhost", port=8000, và bật reload=True. | Graceful Shutdown (Tắt an toàn) qua việc bắt tín hiệu SIGTERM. Đổi host="0.0.0.0", port nhận động từ môi trường (os.getenv("PORT")). | Không làm đứt quãng người dùng: 1. 0.0.0.0 là bắt buộc để Docker có thể mở cổng kết nối ra ngoài. 2. Port động giúp tương thích với cơ chế tự cấp port của Cloud. 3. Tắt an toàn giúp ứng dụng xử lý nốt các request đang chạy dở trước khi container chính thức đóng cửa khi bạn deploy bản cập nhật mới.|




## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. Base image: FROM python:3.11
2. Working directory: WORKDIR /app 
3. Tại sao COPY requirements.txt trước?  
Việc copy file requirements.txt và chạy pip install trước khi copy toàn bộ mã nguồn (app.py) là để tận dụng cơ chế Docker layer cache (Bộ nhớ đệm theo lớp của Docker). 
4. CMD vs ENTRYPOINT khác nhau thế nào?  
Dùng ENTRYPOINT cho phần lệnh bắt buộc phải chạy. Dùng CMD cho phần tham số có thể thay đổi linh hoạt.

### Exercise 2.3: Image size comparison
- Develop: [1.66] GB
- Production: [236] MB
- Difference: [1.43] GB

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- URL: https://ai-agent-w9u9.onrender.com/
- Screenshot: ![railway_deployment](day12_ha-tang-cloud_va_deployment/railway_deployment.png)

## Part 4: API Security

### Exercise 4.1-4.3: Test results
1. Test ko có API KEY: Response: {"detail":"Missing API key. Include header: X-API-Key: "}
Status: 401 Unauthorized  

2. Test có API KEY: 
question: Hello
answer: Agent đang hoạt động tốt! (mock response)
Status: 200 OK

### Exercise 4.4: Cost guard implementation
Cost guard implementation:

- `check_budget(user_id)` được gọi trước khi gọi LLM để kiểm tra user còn budget hay không.
- `record_usage(user_id, input_tokens, output_tokens)` được gọi sau khi LLM trả lời để ghi nhận usage.
- Cost được tính dựa trên số input tokens và output tokens.
- Mỗi user có daily budget `1.0 USD`.
- Toàn hệ thống có global daily budget `10.0 USD`.
- Nếu user vượt budget, server trả về `402 Payment Required`.
- Nếu global budget vượt giới hạn, server trả về `503 Service Unavailable`.

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes
[Your explanations and test results]
```
### Exercise 5.1: Health checks

`/health` là liveness probe, dùng để kiểm tra process còn sống và service có đang hoạt động không. Endpoint này trả về status, uptime, version, environment, timestamp và một số dependency checks.

`/ready` là readiness probe, dùng để kiểm tra app đã sẵn sàng nhận traffic chưa. Nếu app đang startup hoặc shutdown, endpoint này có thể trả `503` để load balancer không route traffic vào instance đó.

Test `/health`:

```json
{"status":"ok","uptime_seconds":9.8,"version":"1.0.0","environment":"development","timestamp":"2026-06-12T09:33:17.469182+00:00","checks":{"memory":{"status":"ok","used_percent":71.9}}}
```

Test `/ready`:

```json
{"ready":true,"in_flight_requests":1}
```

Test `/ask`:

```json
{"answer":"Đây là câu trả lời từ AI agent (mock). Trong production, đây sẽ là response từ OpenAI/Anthropic."}
```

Kết luận: health check và readiness check đều hoạt động. App có thể báo trạng thái sống qua `/health` và trạng thái sẵn sàng nhận request qua `/ready`.

### Exercise 5.2: Graceful shutdown

Code sử dụng FastAPI lifespan để quản lý startup/shutdown:

- Khi startup, app load dependencies và set `_is_ready = True`.
- Khi shutdown, app set `_is_ready = False`.
- App theo dõi số request đang xử lý bằng `_in_flight_requests`.
- Trong shutdown phase, app chờ request đang chạy hoàn thành, tối đa 30 giây.
- App có signal handler cho `SIGTERM` và `SIGINT` để log quá trình shutdown.

Test result:

```text
Get-Process python
Stop-Process -Id 26192
```

Sau khi stop process, app tự tắt. Điều này cho thấy app có thể nhận tín hiệu dừng và đi qua shutdown flow thay vì chỉ bị crash bất ngờ.

### Exercise 5.3: Stateless design

Trong production version, agent không nên lưu conversation history trực tiếp trong memory của từng instance, vì khi scale nhiều instances thì mỗi instance có memory riêng. Nếu request đầu tiên vào instance 1 nhưng request tiếp theo vào instance 2, state trong memory sẽ bị mất.

Code trong `05-scaling-reliability/production/app.py` giải quyết bằng cách lưu session vào Redis:

- `save_session(session_id, data)`: lưu session vào Redis với TTL.
- `load_session(session_id)`: đọc session từ Redis.
- `append_to_history(session_id, role, content)`: thêm message vào conversation history.

Endpoint `/chat` tạo hoặc dùng lại `session_id`, lưu câu hỏi và câu trả lời vào history. Vì history được lưu trong Redis, bất kỳ agent instance nào cũng có thể đọc được cùng session.

Kết luận: thiết kế này stateless ở tầng application instance. State được đưa ra backing service là Redis, giúp app scale ngang qua nhiều instances mà vẫn giữ được conversation history.

### Exercise 5.4: Load balancing

Stack production gồm các service chính:

- `agent`: FastAPI agent, có thể scale lên nhiều instances.
- `redis`: shared storage để lưu session/conversation history.
- `nginx`: load balancer, nhận request ở port `8080` rồi forward đến các `agent` instances.

Architecture:

```text
Client -> Nginx (:8080) -> Agent instances (:8000)
                           |
                           +-> Redis
```

Test `/health` qua Nginx:

```json
{"status":"ok","instance_id":"instance-436975","uptime_seconds":1.0,"storage":"redis","redis_connected":true}
```

Test `/ready` qua Nginx:

```json
{"ready":true,"instance":"instance-fdd975"}
```

Test `/chat`:

```text
session_id: df87e009-e981-4400-9e52-2f5703d7a8a4
question: What is Redis used for?
served_by: instance-bb2fe3
storage: redis
```

Kết luận: Nginx đã route request đến các agent instances khác nhau. Response có `served_by`, giúp quan sát instance nào xử lý request. State được lưu bằng Redis nên app vẫn giữ được session dù request được xử lý bởi instance khác nhau.

### Exercise 5.5: Test stateless

Chạy script:

```powershell
python test_stateless.py
```

Kết quả:

```text
Total requests: 5
Instances used: {'instance-436975', 'instance-bb2fe3', 'instance-fdd975'}
All requests served despite different instances.
Total messages in history: 10
Session history preserved across all instances via Redis.
```

---

### 2. Full Source Code - Lab 06 Complete (60 points)

Your final production-ready agent with all files:

```
your-repo/
├── app/
│   ├── main.py              # Main application
│   ├── config.py            # Configuration
│   ├── auth.py              # Authentication
│   ├── rate_limiter.py      # Rate limiting
│   └── cost_guard.py        # Cost protection
├── utils/
│   └── mock_llm.py          # Mock LLM (provided)
├── Dockerfile               # Multi-stage build
├── docker-compose.yml       # Full stack
├── requirements.txt         # Dependencies
├── .env.example             # Environment template
├── .dockerignore            # Docker ignore
├── railway.toml             # Railway config (or render.yaml)
└── README.md                # Setup instructions
```

**Requirements:**
-  All code runs without errors
-  Multi-stage Dockerfile (image < 500 MB)
-  API key authentication
-  Rate limiting (10 req/min)
-  Cost guard ($10/month)
-  Health + readiness checks
-  Graceful shutdown
-  Stateless design (Redis)
-  No hardcoded secrets

---

### 3. Service Domain Link

Create a file `DEPLOYMENT.md` with your deployed service information:

```markdown
# Deployment Information

## Public URL
https://your-agent.railway.app

## Platform
Railway / Render / Cloud Run

## Test Commands

### Health Check
```bash
curl https://your-agent.railway.app/health
# Expected: {"status": "ok"}
```

### API Test (with authentication)
```bash
curl -X POST https://your-agent.railway.app/ask \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "question": "Hello"}'
```

## Environment Variables Set
- PORT
- REDIS_URL
- AGENT_API_KEY
- LOG_LEVEL

## Screenshots
- [Deployment dashboard](screenshots/dashboard.png)
- [Service running](screenshots/running.png)
- [Test results](screenshots/test.png)
```

##  Pre-Submission Checklist

- [ ] Repository is public (or instructor has access)
- [ ] `MISSION_ANSWERS.md` completed with all exercises
- [ ] `DEPLOYMENT.md` has working public URL
- [ ] All source code in `app/` directory
- [ ] `README.md` has clear setup instructions
- [ ] No `.env` file committed (only `.env.example`)
- [ ] No hardcoded secrets in code
- [ ] Public URL is accessible and working
- [ ] Screenshots included in `screenshots/` folder
- [ ] Repository has clear commit history

---

##  Self-Test

Before submitting, verify your deployment:

```bash
# 1. Health check
curl https://your-app.railway.app/health

# 2. Authentication required
curl https://your-app.railway.app/ask
# Should return 401

# 3. With API key works
curl -H "X-API-Key: YOUR_KEY" https://your-app.railway.app/ask \
  -X POST -d '{"user_id":"test","question":"Hello"}'
# Should return 200

# 4. Rate limiting
for i in {1..15}; do 
  curl -H "X-API-Key: YOUR_KEY" https://your-app.railway.app/ask \
    -X POST -d '{"user_id":"test","question":"test"}'; 
done
# Should eventually return 429
```

---

##  Submission

**Submit your GitHub repository URL:**

```
https://github.com/your-username/day12-agent-deployment
```

**Deadline:** 17/4/2026

---

##  Quick Tips

1.  Test your public URL from a different device
2.  Make sure repository is public or instructor has access
3.  Include screenshots of working deployment
4.  Write clear commit messages
5.  Test all commands in DEPLOYMENT.md work
6.  No secrets in code or commit history

---

##  Need Help?

- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Review [CODE_LAB.md](CODE_LAB.md)
- Ask in office hours
- Post in discussion forum

---

**Good luck! **
