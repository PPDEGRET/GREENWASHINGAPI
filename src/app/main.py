from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.app.routers.analysis import router as analysis_router

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

# Include the analysis router
app.include_router(analysis_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok"}
