from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables early so downstream imports (e.g., OpenAI client) see them
load_dotenv()

from src.app.routers.analysis import router as analysis_router
from src.app.routers.auth import router as auth_router
from src.app.routers.usage import router as usage_router
from src.app.routers.onboarding import router as onboarding_router

app = FastAPI(title="GreenCheck API", version="2.0.0")

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analysis_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(usage_router, prefix="/api/v1")
app.include_router(onboarding_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok"}
