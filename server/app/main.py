from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.courses import router as courses_router
from app.api.health import router as health_router
from app.api.captions import router as captions_router
from app.api.quiz import router as quiz_router
from app.core.config import settings

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.client_origin],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):517\d",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(courses_router, prefix="/api")
app.include_router(captions_router, prefix="/api")
app.include_router(quiz_router, prefix="/api")
