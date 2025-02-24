# 🎬 Movie Character Chatbot (Django + Celery + Redis + ChromaDB)

## 📌 Project Overview
This is a **REST API** built using **Django REST Framework (DRF)** that allows users to chat with movie characters. It uses:
- **ChromaDB** for semantic search (Retrieval-Augmented Generation - RAG).
- **Together AI Llama-3.1-8B** for AI-generated responses.
- **Redis (via Docker)** for caching and Celery task queue.
- **Celery** for background processing.
- **PostgreSQL (Optional)** for storing structured movie dialogues.

---

## 🚀 Features
✅ **Retrieves real movie dialogues before AI generation**
✅ **Uses vector embeddings for semantic search** (ChromaDB + BGE model)
✅ **Caches responses in Redis for faster retrieval**
✅ **Async processing with Celery to prevent API blocking**
✅ **Rate limiting (5 requests/sec per user)**
✅ **Load testing using Locust**

---

## 🛠️ Installation & Setup
### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/your-username/movie-character-chatbot.git
cd movie-character-chatbot
```

### **2️⃣ Create Virtual Environment & Install Dependencies**
```bash
python -m venv venv
source venv/bin/activate   # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

### **3️⃣ Set Up Environment Variables (`.env` file)**
Create a `.env` file in the project root:
```ini
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Database (PostgreSQL Optional)
DATABASE_URL=postgres://your_user:your_password@localhost:5432/movie_db

# Redis (For Celery & Caching)
REDIS_URL=redis://127.0.0.1:6379/0

# Together AI API Key (for Llama-3.1-8B)
TOGETHER_API_KEY=your-api-key
```

---

## 🐳 Running with Docker (Recommended)
### **1️⃣ Build & Run the Containers**
```bash
docker-compose up -d --build
```

### **2️⃣ Check Running Containers**
```bash
docker ps
```

### **3️⃣ Verify Redis is Running**
```bash
docker exec -it redis_cache redis-cli ping
```
✅ Expected Output: `PONG`

---

## 📡 API Endpoints
### **POST `/api/chat/`** (Chat with a Movie Character)
**Request:**
```json
{
  "character": "jules winnfield",
  "user_message": "Say what again!"
}
```

**Response:**
```json
{
  "response": "English, motherf***er! Do you speak it?!"
}
```

### **GET `/api/health/`** (Check API Health)
```bash
curl -X GET http://127.0.0.1:8000/api/health/
```

---

## 📊 Load Testing with Locust
### **1️⃣ Install Locust**
```bash
pip install locust
```

### **2️⃣ Create `locustfile.py`**
```python
from locust import HttpUser, task, between

class ChatUser(HttpUser):
    wait_time = between(1, 2)
    
    @task
    def send_message(self):
        self.client.post("/api/chat/", json={
            "character": "jules winnfield", "user_message": "Say what again!"
        })
```

### **3️⃣ Run Locust**
```bash
locust -f locustfile.py
```
- Open **http://localhost:8089** to start the test.

---

## 🔍 Debugging & Troubleshooting
### **1️⃣ Check Docker Logs**
```bash
docker logs redis_cache
```

### **2️⃣ Check Celery Worker Logs**
```bash
celery -A chat worker --loglevel=info
```

### **3️⃣ Check Redis Connection**
```bash
docker exec -it redis_cache redis-cli ping
```
✅ Expected Output: `PONG`

---

## 📜 License
MIT License - Free to use and modify. ❤️

