Chili Labs Backend Test Task
A production-ready RESTful API with WebSocket support for real-time avatar updates, built with FastAPI and PostgreSQL.

🚀 Features
✅ User Authentication - Registration and login with JWT tokens 
✅ OAuth2.0 Compliant - Access/Refresh token pair with token rotation
✅ Avatar Upload - Image upload with validation and storage
✅ Real-time Updates - WebSocket notifications for avatar changes
✅ User Management - Complete user deletion with cleanup
✅ JSend Response Format - Standardized API responses
✅ Docker Support - One-command deployment with Docker Compose
✅ Comprehensive Tests - Unit and integration tests with pytest
✅ API Documentation - Interactive Swagger/OpenAPI docs
📋 Requirements
Option 1: Docker (Recommended)
Docker
Docker Compose
Option 2: Local Development
Python 3.11+
PostgreSQL 15+
🏃 Quick Start with Docker
Run the entire application with one command:

bash
docker-compose up --build
The API will be available at:

API: http://localhost:8000
Documentation: http://localhost:8000/api/docs
Alternative Docs: http://localhost:8000/api/redoc
🛠️ Local Development Setup
1. Clone the Repository
bash
git clone <repository-url>
cd backend-test-task
2. Create Virtual Environment
bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
3. Install Dependencies
bash
pip install -r requirements.txt
4. Configure Environment
bash
cp .env.example .env
Edit .env and configure your database connection and secret key.

5. Start PostgreSQL
Make sure PostgreSQL is running and create a database:

sql
CREATE DATABASE chililabs_db;
CREATE USER chililabs_user WITH PASSWORD 'chililabs_password';
GRANT ALL PRIVILEGES ON DATABASE chililabs_db TO chililabs_user;
6. Run the Application
bash
uvicorn app.main:app --reload
📚 API Endpoints
Authentication
Register
http
POST /api/auth/register
Content-Type: application/json

{
  "identifier": "user@example.com",
  "password": "securepassword123"
}
Response:

json
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
Login
http
POST /api/auth/login
Content-Type: application/json

{
  "identifier": "user@example.com",
  "password": "securepassword123"
}
Refresh Token
http
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGc..."
}
Avatar Management
Upload Avatar
http
POST /api/avatars/upload
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

file: [image file]
Response:

json
{
  "status": "success",
  "data": {
    "avatar_url": "/uploads/avatars/abc123.jpg"
  }
}
User Management
Get Current User
http
GET /api/users/me
Authorization: Bearer {access_token}
Delete User
http
DELETE /api/users/me
Authorization: Bearer {access_token}
Response:

json
{
  "status": "success",
  "data": {
    "message": "User account successfully deleted"
  }
}
WebSocket Connection
javascript
const ws = new WebSocket('ws://localhost:8000/ws?token=YOUR_ACCESS_TOKEN');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Avatar updated:', data);
  // {
  //   "type": "avatar_updated",
  //   "user_id": 1,
  //   "avatar_url": "/uploads/avatars/new-avatar.jpg",
  //   "timestamp": "2025-11-03T12:00:00"
  // }
};
🧪 Testing
Run All Tests
bash
pytest
Run Unit Tests Only
bash
pytest tests/unit/
Run Integration Tests Only
bash
pytest tests/integration/
Run with Coverage
bash
pytest --cov=app --cov-report=html
🏗️ Project Structure
backend-test-task/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── auth/
│   │   ├── jwt.py           # JWT token handling
│   │   └── dependencies.py  # Auth dependencies
│   ├── routers/
│   │   ├── auth.py          # Authentication routes
│   │   ├── avatars.py       # Avatar upload routes
│   │   └── users.py         # User management routes
│   ├── services/
│   │   └── websocket.py     # WebSocket manager
│   └── utils/
│       ├── jsend.py         # JSend response formatter
│       └── password.py      # Password utilities
├── tests/
│   ├── conftest.py          # Test configuration
│   ├── unit/                # Unit tests
│   └── integration/         # Integration tests
├── uploads/                 # Avatar storage
├── docker-compose.yml       # Docker Compose config
├── Dockerfile              # Docker image
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
└── README.md              # This file
🔐 Security Features
Password Hashing: Bcrypt with salt
JWT Tokens: Stateless authentication with expiration
Token Rotation: Refresh tokens are rotated on use
Token Revocation: Old tokens are invalidated on user deletion
Input Validation: Pydantic schema validation
File Validation: Image type and size validation
SQL Injection Protection: SQLAlchemy ORM
🎯 Technology Stack
Framework: FastAPI 0.109.0
Database: PostgreSQL 15
ORM: SQLAlchemy 2.0
Authentication: JWT with python-jose
Password Hashing: Passlib with bcrypt
WebSockets: Native FastAPI WebSocket support
Testing: pytest with httpx
Containerization: Docker & Docker Compose
📖 API Documentation
Once the application is running, visit:

Swagger UI: http://localhost:8000/api/docs
ReDoc: http://localhost:8000/api/redoc
Interactive documentation allows you to test all endpoints directly from your browser.

🔧 Configuration
Key environment variables in .env:

bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# JWT
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# File Upload
MAX_FILE_SIZE=5242880  # 5MB
UPLOAD_DIR=uploads/avatars
🚢 Production Deployment
Security Recommendations
Change SECRET_KEY: Generate a secure random key
bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
Use HTTPS: Configure SSL/TLS certificates
Configure CORS: Restrict CORS_ORIGINS to your domains
Database Security: Use strong passwords, restrict access
File Storage: Consider using S3 or similar for production
Environment Variables: Never commit .env to version control
📝 Development Notes
Adding New Endpoints
Create route handler in app/routers/
Add router to app/main.py
Create tests in tests/integration/
Database Migrations
For schema changes, use Alembic:

bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
🤝 Contributing
Fork the repository
Create a feature branch
Make your changes
Add tests
Submit a pull request
📄 License
This project is created as a test task for Chili Labs.

👤 Author
Shokh

🙏 Acknowledgments
Chili Labs for the test task opportunity
FastAPI for the excellent framework
The Python community
Built with ❤️ for Chili Labs

