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
1. Base image: [Your answer]
2. Working directory: [Your answer]
...

### Exercise 2.3: Image size comparison
- Develop: [X] MB
- Production: [Y] MB
- Difference: [Z]%

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- URL: https://your-app.railway.app
- Screenshot: [Link to screenshot in repo]

## Part 4: API Security

### Exercise 4.1-4.3: Test results
[Paste your test outputs]

### Exercise 4.4: Cost guard implementation
[Explain your approach]

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes
[Your explanations and test results]
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
