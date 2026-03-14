# Avatar Management API

> A production-ready RESTful API with WebSocket support for real-time avatar updates.  
> Built with **FastAPI** and **PostgreSQL** as a backend test task for **Chili Labs**.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![pytest](https://img.shields.io/badge/Tests-pytest-brightgreen?logo=pytest&logoColor=white)

---

## Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Requirements](#-requirements)
- [Quick Start (Docker)](#-quick-start-with-docker)
- [Local Development Setup](#-local-development-setup)
- [API Endpoints](#-api-endpoints)
- [WebSocket](#-websocket)
- [Testing](#-testing)
- [Project Structure](#-project-structure)
- [Security](#-security)
- [Configuration](#-configuration)
- [Production Notes](#-production-notes)

---

## ✅ Features

| Feature | Description |
|---|---|
| **JWT Authentication** | Registration and login with access/refresh token pair |
| **OAuth2.0 Compliant** | Token rotation — refresh tokens are invalidated on use |
| **Avatar Upload** | Image upload with MIME type and file size validation |
| **Real-time Updates** | WebSocket notifications pushed on avatar changes |
| **User Management** | Full account deletion with cascading cleanup |
| **JSend Responses** | Standardized `success` / `fail` / `error` envelope |
| **Docker Support** | One-command deployment via Docker Compose |
| **Comprehensive Tests** | Unit and integration tests with `pytest` + `httpx` |
| **API Docs** | Auto-generated Swagger UI and ReDoc |

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.109.0 |
| Database | PostgreSQL 15 |
| ORM | SQLAlchemy 2.0 (async) |
| Auth | JWT via `python-jose` |
| Password Hashing | `passlib` with bcrypt |
| WebSockets | Native FastAPI WebSocket support |
| Testing | `pytest` + `httpx` |
| Containerization | Docker & Docker Compose |

---

## 📋 Requirements

**Option 1 — Docker (Recommended)**
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

**Option 2 — Local Development**
- Python 3.11+
- PostgreSQL 15+

---

## 🚀 Quick Start with Docker

Run the full application stack with a single command:

```bash
docker-compose up --build
```

Once running, the following endpoints are available:

| Service | URL |
|---|---|
| API Root | http://localhost:8000 |
| Swagger UI | http://localhost:8000/api/docs |
| ReDoc | http://localhost:8000/api/redoc |

---

## 🛠 Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/mufazzalshokh/backend-test-task.git
cd backend-test-task
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate       # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Open `.env` and set your database connection string and secret key (see [Configuration](#-configuration)).

### 5. Provision PostgreSQL

```sql
CREATE DATABASE chililabs_db;
CREATE USER chililabs_user WITH PASSWORD 'chililabs_password';
GRANT ALL PRIVILEGES ON DATABASE chililabs_db TO chililabs_user;
```

### 6. Run the Application

```bash
uvicorn app.main:app --reload
```

---

## 📚 API Endpoints

### Authentication

#### `POST /api/auth/register`

```http
POST /api/auth/register
Content-Type: application/json

{
  "identifier": "user@example.com",
  "password": "securepassword123"
}
```

<details>
<summary>Response</summary>

```json
{
  "status": "success",
  "data": {
    "user": {
      "id": 1,
      "identifier": "user@example.com",
      "avatar_url": null,
      "created_at": "2025-11-03T12:00:00"
    },
    "tokens": {
      "access_token": "eyJhbGc...",
      "refresh_token": "eyJhbGc...",
      "token_type": "bearer",
      "expires_in": 1800
    }
  }
}
```
</details>

---

#### `POST /api/auth/login`

```http
POST /api/auth/login
Content-Type: application/json

{
  "identifier": "user@example.com",
  "password": "securepassword123"
}
```

---

#### `POST /api/auth/refresh`

```http
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGc..."
}
```

---

### Avatar Management

#### `POST /api/avatars/upload`

```http
POST /api/avatars/upload
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

file: <image file>
```

<details>
<summary>Response</summary>

```json
{
  "status": "success",
  "data": {
    "avatar_url": "/uploads/avatars/abc123.jpg"
  }
}
```
</details>

---

### User Management

#### `GET /api/users/me`

```http
GET /api/users/me
Authorization: Bearer {access_token}
```

---

#### `DELETE /api/users/me`

```http
DELETE /api/users/me
Authorization: Bearer {access_token}
```

<details>
<summary>Response</summary>

```json
{
  "status": "success",
  "data": {
    "message": "User account successfully deleted"
  }
}
```
</details>

---

## 🔌 WebSocket

Connect with a valid access token to receive real-time avatar update events:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws?token=YOUR_ACCESS_TOKEN');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Payload shape:
  // {
  //   "type": "avatar_updated",
  //   "user_id": 1,
  //   "avatar_url": "/uploads/avatars/new-avatar.jpg",
  //   "timestamp": "2025-11-03T12:00:00"
  // }
  console.log('Avatar updated:', data);
};
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# With HTML coverage report
pytest --cov=app --cov-report=html
```

---

## 🏗 Project Structure

```
backend-test-task/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Settings via pydantic-settings
│   ├── database.py          # Async database connection
│   ├── models.py            # SQLAlchemy ORM models
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── auth/
│   │   ├── jwt.py           # JWT encoding / decoding
│   │   └── dependencies.py  # FastAPI auth dependencies
│   ├── routers/
│   │   ├── auth.py          # /api/auth/* routes
│   │   ├── avatars.py       # /api/avatars/* routes
│   │   └── users.py         # /api/users/* routes
│   ├── services/
│   │   └── websocket.py     # WebSocket connection manager
│   └── utils/
│       ├── jsend.py         # JSend response helpers
│       └── password.py      # bcrypt helpers
├── tests/
│   ├── conftest.py          # Shared fixtures
│   ├── unit/
│   └── integration/
├── uploads/                 # Local avatar storage
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🔐 Security

| Mechanism | Implementation |
|---|---|
| Password Storage | bcrypt with per-user salt |
| Stateless Auth | JWT with configurable expiry |
| Token Rotation | Refresh tokens invalidated on every use |
| Token Revocation | All tokens invalidated on account deletion |
| Input Validation | Pydantic schema validation on all endpoints |
| File Validation | MIME type + file size enforcement on upload |
| SQL Injection | Fully parameterised queries via SQLAlchemy ORM |

---

## ⚙️ Configuration

Copy `.env.example` to `.env` and adjust the values below:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# JWT
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# File Upload
MAX_FILE_SIZE=5242880   # 5 MB
UPLOAD_DIR=uploads/avatars
```

---

## 🚢 Production Notes

### Generate a Secure Secret Key

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Checklist

- [ ] Replace `SECRET_KEY` with a securely generated value
- [ ] Enable HTTPS (configure SSL/TLS in your reverse proxy)
- [ ] Restrict `CORS_ORIGINS` to your actual domain(s)
- [ ] Use strong PostgreSQL credentials and restrict network access
- [ ] Migrate avatar storage to S3-compatible object storage
- [ ] Never commit `.env` to version control

### Database Migrations (Alembic)

```bash
# Generate a new migration after model changes
alembic revision --autogenerate -m "your description"

# Apply pending migrations
alembic upgrade head
```

---

## 👤 Author

**Mufazzalshokh**  
[github.com/mufazzalshokh](https://github.com/mufazzalshokh)

---

## 📄 License

This project was created as a technical assessment for **Chili Labs**.
