import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.content import router as content_router
from app.api.courses import router as courses_router
from app.core.auth import get_current_user
from app.db.base import Base
from app.db.init_db import SEED_BLOG_POSTS, SEED_COURSES, SEED_QUIZ_QUESTIONS
from app.db.session import get_db
from app.models.content_item import ContentItem
from app.models.course import Course
from app.models.user import User, UserRole


class BackendContentApiTest(unittest.TestCase):
    def setUp(self):
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)

        db = TestingSessionLocal()
        instructor = User(
            email="instructor@example.com",
            name="Instructor",
            hashed_password="hashed",
            role=UserRole.instructor.value,
        )
        db.add_all(Course(**course_data) for course_data in SEED_COURSES)
        db.add_all(ContentItem(kind="blog-post", **post_data) for post_data in SEED_BLOG_POSTS)
        db.add_all(ContentItem(kind="quiz-question", **question_data) for question_data in SEED_QUIZ_QUESTIONS)
        db.add(instructor)
        db.commit()
        db.refresh(instructor)
        db.close()

        def override_get_db():
            session = TestingSessionLocal()
            try:
                yield session
            finally:
                session.close()

        app = FastAPI()
        app.include_router(courses_router, prefix="/api")
        app.include_router(content_router, prefix="/api")
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = lambda: instructor
        self.client = TestClient(app)

    def test_courses_api_serves_frontend_content(self):
        response = self.client.get("/api/courses")

        self.assertEqual(response.status_code, 200)
        courses = response.json()
        self.assertGreaterEqual(len(courses), 1)
        self.assertIn("slug", courses[0])
        self.assertIn("syllabus", courses[0])
        self.assertIn("resources", courses[0])

    def test_blog_posts_api_serves_backend_content(self):
        response = self.client.get("/api/content/blog-posts")

        self.assertEqual(response.status_code, 200)
        posts = response.json()
        self.assertGreaterEqual(len(posts), 1)
        self.assertIn("excerpt", posts[0])
        self.assertIn("image", posts[0])

    def test_quiz_questions_api_serves_frontend_compatible_questions(self):
        response = self.client.get("/api/content/quiz-questions")

        self.assertEqual(response.status_code, 200)
        questions = response.json()
        self.assertGreaterEqual(len(questions), 1)
        self.assertIn(questions[0]["a"], questions[0]["options"])
        self.assertIn("topic_tag", questions[0])

    def test_operations_summary_counts_managed_content(self):
        response = self.client.get("/api/content/operations/summary")

        self.assertEqual(response.status_code, 200)
        summary = response.json()
        self.assertEqual(summary["courses"], len(SEED_COURSES))
        self.assertEqual(summary["blog_posts"], len(SEED_BLOG_POSTS))
        self.assertEqual(summary["quiz_questions"], len(SEED_QUIZ_QUESTIONS))
        self.assertEqual(summary["operator_role"], UserRole.instructor.value)

    def test_instructor_can_update_content_item(self):
        created = self.client.post(
            "/api/content/blog-post",
            json={"slug": "ops-update", "title": "Original title", "payload": {"excerpt": "Draft"}},
        )
        self.assertEqual(created.status_code, 201)

        updated = self.client.patch(
            f"/api/content/blog-post/{created.json()['id']}",
            json={"title": "Published title", "payload": {"excerpt": "Ready"}},
        )

        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json()["title"], "Published title")
        self.assertEqual(updated.json()["payload"]["excerpt"], "Ready")


if __name__ == "__main__":
    unittest.main()
