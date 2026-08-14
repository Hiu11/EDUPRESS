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
from app.models.enrollment import Enrollment
from app.models.quiz_history import QuizHistory
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

    def test_admin_can_review_and_update_users(self):
        self.client.post(
            "/api/auth/register",
            json={"name": "Student", "email": "student2@example.com", "password": "password123"},
        )
        self.client.post(
            "/api/auth/register",
            json={"name": "Admin", "email": "admin@example.com", "password": "password123"},
        )
        db = self.testing_session()
        try:
            admin = db.query(User).filter(User.email == "admin@example.com").one()
            student = db.query(User).filter(User.email == "student2@example.com").one()
            admin.role = UserRole.admin.value
            db.commit()
            student_id = student.id
        finally:
            db.close()

        admin_login = self.client.post(
            "/api/auth/login",
            json={"email": "admin@example.com", "password": "password123"},
        )
        admin_token = admin_login.json()["access_token"]

        users = self.client.get("/api/auth/users", headers={"Authorization": f"Bearer {admin_token}"})
        self.assertEqual(users.status_code, 200)
        self.assertGreaterEqual(len(users.json()), 2)

        updated = self.client.patch(
            f"/api/auth/users/{student_id}",
            json={"role": UserRole.instructor.value, "is_active": False},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json()["role"], UserRole.instructor.value)
        self.assertFalse(updated.json()["is_active"])

    def test_user_can_export_and_delete_account_data(self):
        self.client.post(
            "/api/auth/register",
            json={"name": "Privacy User", "email": "privacy@example.com", "password": "password123"},
        )
        login = self.client.post(
            "/api/auth/login",
            json={"email": "privacy@example.com", "password": "password123"},
        )
        token = login.json()["access_token"]

        db = self.testing_session()
        try:
            user = db.query(User).filter(User.email == "privacy@example.com").one()
            course = Course(
                title="Privacy Basics",
                author="MindX",
                category="Operations",
                description="Learner data controls",
            )
            db.add(course)
            db.commit()
            db.refresh(course)
            db.add_all(
                [
                    QuizHistory(
                        user_id=str(user.id),
                        course_id=str(course.id),
                        score=4,
                        total=5,
                        topic="privacy",
                        max_streak=3,
                    ),
                    Enrollment(user_id=user.id, course_id=course.id, status="active"),
                ]
            )
            db.commit()
            user_id = user.id
        finally:
            db.close()

        export = self.client.get("/api/auth/me/export", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(export.status_code, 200)
        payload = export.json()
        self.assertEqual(payload["user"]["email"], "privacy@example.com")
        self.assertEqual(len(payload["quiz_history"]), 1)
        self.assertEqual(len(payload["enrollments"]), 1)
        self.assertIn("retention_policy", payload)

        deleted = self.client.delete("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(deleted.status_code, 204)

        db = self.testing_session()
        try:
            self.assertIsNone(db.get(User, user_id))
            self.assertEqual(db.query(QuizHistory).filter(QuizHistory.user_id == str(user_id)).count(), 0)
            self.assertEqual(db.query(Enrollment).filter(Enrollment.user_id == user_id).count(), 0)
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
