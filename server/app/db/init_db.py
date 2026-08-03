from app.db.base import Base
from app.db.session import engine
from app.models.course import Course  # noqa: F401


from app.db.session import SessionLocal

def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Seed data if empty
    db = SessionLocal()
    if db.query(Course).count() == 0:
        print("Seeding dummy courses...")
        c1 = Course(
            title="Mastering FastAPI",
            description="Learn how to build high performance APIs",
            instructor="MindX",
            price=49.99,
            thumbnail_url="https://images.unsplash.com/photo-1555066931-4365d14bab8c"
        )
        c2 = Course(
            title="Nuxt 3 for Beginners",
            description="The best Vue framework",
            instructor="MindX",
            price=39.99,
            thumbnail_url="https://images.unsplash.com/photo-1498050108023-c5249f4df085"
        )
        db.add(c1)
        db.add(c2)
        db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
