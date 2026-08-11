import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.auth import router as auth_router
from app.api.courses import router as courses_router
from app.db.base import Base
from app.db.session import get_db
from app.models.course import Course  # noqa: F401
from app.models.user import User, UserRole


class AuthApiTest(unittest.TestCase):
    def setUp(self):
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(bind=engine)
        testing_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        def override_get_db():
            db = testing_session()
            try:
                yield db
            finally:
                db.close()

        app = FastAPI()
        app.dependency_overrides[get_db] = override_get_db
        app.include_router(auth_router, prefix="/api")
        app.include_router(courses_router, prefix="/api")

        self.client = TestClient(app)
        self.testing_session = testing_session

    def test_register_login_and_me_flow(self):
        register = self.client.post(
            "/api/auth/register",
            json={"name": "Student One", "email": "student@example.com", "password": "password123"},
        )
        self.assertEqual(register.status_code, 201)
        self.assertEqual(register.json()["role"], UserRole.student.value)

        login = self.client.post(
            "/api/auth/login",
            json={"email": "student@example.com", "password": "password123"},
        )
        self.assertEqual(login.status_code, 200)
        token = login.json()["access_token"]

        me = self.client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.json()["email"], "student@example.com")

    def test_course_creation_requires_instructor_or_admin_role(self):
        self.client.post(
            "/api/auth/register",
            json={"name": "Teacher", "email": "teacher@example.com", "password": "password123"},
        )
        student_login = self.client.post(
            "/api/auth/login",
            json={"email": "teacher@example.com", "password": "password123"},
        )
        student_token = student_login.json()["access_token"]

        course_payload = {
            "title": "Secure FastAPI",
            "author": "MindX",
            "category": "Backend",
            "description": "Auth and authorization basics",
        }
        forbidden = self.client.post(
            "/api/courses",
            json=course_payload,
            headers={"Authorization": f"Bearer {student_token}"},
        )
        self.assertEqual(forbidden.status_code, 403)

        db = self.testing_session()
        try:
            user = db.query(User).filter(User.email == "teacher@example.com").one()
            user.role = UserRole.instructor.value
            db.commit()
        finally:
            db.close()

        instructor_login = self.client.post(
            "/api/auth/login",
            json={"email": "teacher@example.com", "password": "password123"},
        )
        instructor_token = instructor_login.json()["access_token"]

        created = self.client.post(
            "/api/courses",
            json=course_payload,
            headers={"Authorization": f"Bearer {instructor_token}"},
        )
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.json()["title"], "Secure FastAPI")


if __name__ == "__main__":
    unittest.main()
