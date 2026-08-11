from app.db.base import Base
from app.db.session import engine
from app.models.course import Course  # noqa: F401
from app.db.session import SessionLocal


SEED_COURSES = [
    {
        "title": "Mastering FastAPI",
        "author": "MindX",
        "category": "Backend",
        "description": "Learn how to build high performance APIs",
        "image_url": "https://images.unsplash.com/photo-1555066931-4365d14bab8c",
    },
    {
        "title": "Nuxt 3 for Beginners",
        "author": "MindX",
        "category": "Frontend",
        "description": "The best Vue framework",
        "image_url": "https://images.unsplash.com/photo-1498050108023-c5249f4df085",
    },
]


def init_db():
    Base.metadata.create_all(bind=engine)

    # Seed data if empty
    db = SessionLocal()
    try:
        if db.query(Course).count() == 0:
            print("Seeding starter courses...")
            db.add_all(Course(**course_data) for course_data in SEED_COURSES)
            db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
