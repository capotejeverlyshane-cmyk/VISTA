from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn
from contextlib import asynccontextmanager

from services.cache import init_cache
from services.nlp import load_models
from routers import chat, admin, services

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup tasks
    print("[INFO] Starting up VISTA Backend...")
    init_cache()
    load_models()
    yield
    # Shutdown tasks
    print("[INFO] Shutting down VISTA Backend...")

app = FastAPI(title="VISTA LGU Chatbot API", lifespan=lifespan)

# Setup CORS
frontend_url = os.environ.get("FRONTEND_URL", "").rstrip("/")
allowed_origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:8085",
    "http://localhost:8085",
    "https://vista-frontend-five.vercel.app",
]
if frontend_url and frontend_url not in allowed_origins:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://vista-[a-zA-Z0-9_-]+\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(admin.router)
app.include_router(services.router)

@app.post("/feedback")
def submit_feedback_root(req: services.FeedbackRequest):
    return services.submit_feedback(req)

@app.get("/")
def root():
    return {"status": "VISTA Backend API is running."}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)

