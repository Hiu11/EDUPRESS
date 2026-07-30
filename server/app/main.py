from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.courses import router as courses_router
from app.api.health import router as health_router
from app.api.captions import router as captions_router
from app.api.quiz import router as quiz_router
from app.api.comments import router as comments_router
from app.api.stream import router as stream_router
from app.core.config import settings

from app.db.mongo import connect_to_mongo, close_mongo_connection
from app.eventbus.producer import event_producer
from app.eventbus.consumer import event_consumer

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    await event_producer.start()
    await event_consumer.start()
    yield
    # Shutdown
    await event_consumer.stop()
    await event_producer.stop()
    await close_mongo_connection()

app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.client_origin, "http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(courses_router, prefix="/api")
app.include_router(captions_router, prefix="/api")
app.include_router(quiz_router, prefix="/api")
app.include_router(comments_router, prefix="/api")
app.include_router(stream_router, prefix="/api")
