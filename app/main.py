from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

app = FastAPI(title=settings.APP_NAME, docs_url="/api/docs")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "success", "message": "API is running"}

@app.get("/health")
async def health():
    return {"status": "success"}

# Try to import routers with error messages
print("=" * 60)
print("ATTEMPTING TO LOAD ROUTERS...")
print("=" * 60)

try:
    from app.routers import auth
    print("✅ Auth router loaded")
    app.include_router(auth.router)
except Exception as e:
    print(f"❌ Auth router ERROR: {e}")
    import traceback
    traceback.print_exc()

try:
    from app.routers import avatars
    print("✅ Avatars router loaded")
    app.include_router(avatars.router)
except Exception as e:
    print(f"❌ Avatars router ERROR: {e}")
    import traceback
    traceback.print_exc()

try:
    from app.routers import users
    print("✅ Users router loaded")
    app.include_router(users.router)
except Exception as e:
    print(f"❌ Users router ERROR: {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)