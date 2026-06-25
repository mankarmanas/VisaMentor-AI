from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes.chat import router as chat_router
from src.api.models.chat import HealthResponse
from src.api.routes.users import router as users_router

app = FastAPI(
    title="Visa Mentor AI",
    description="RAG-powered F1 visa assistant for international students",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api/v1", tags=["chat"])

app.include_router(users_router, prefix="/api/v1")

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok", message="Visa Mentor AI is running")