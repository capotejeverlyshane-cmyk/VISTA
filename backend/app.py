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
frontend_url = os.environ.get("FRONTEND_URL", "http://127.0.0.1:5500")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev. Change to [frontend_url] for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(admin.router)
app.include_router(services.router)

@app.get("/")
def root():
    return {"status": "VISTA Backend API is running."}

if __name__ == "__main__":
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8001, reload=True)