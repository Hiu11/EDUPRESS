import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.courses import router as courses_router
from app.api.enrollments import router as enrollments_router
from app.core.auth import get_current_user, get_optional_current_user
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.models.course import Course
from app.models.enrollment import EnrollmentStatus
from app.models.user import User, UserRole


class EnrollmentApiTest(unittest.TestCase):
    def setUp(self):
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(bind=engine)
        self.testing_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        db = self.testing_session()
        self.student = User(
            email="student@example.com",
            name="Student",
            hashed_password=hash_password("password123"),
            role=UserRole.student.value,
        )
        self.admin = User(
            email="admin@example.com",
            name="Admin",
            hashed_password=hash_password("password123"),
            role=UserRole.admin.value,
        )
        self.free_course = Course(
            title="Free OOP",
            author="MindX",
            category="Software Engineering",
            description="Free starter course",
            access_type="free",
            price_cents=0,
            syllabus=["Class basics"],
            resources=["Starter repo"],
        )
        self.paid_course = Course(
            title="Paid Web",
            author="MindX",
            category="Web Development",
            description="Paid project course",
            access_type="paid",
            price_cents=250000000,
            syllabus=["Production project"],
            resources=["Deployment checklist"],
        )
        db.add_all([self.student, self.admin, self.free_course, self.paid_course])
        db.commit()
        for item in [self.student, self.admin, self.free_course, self.paid_course]:
            db.refresh(item)
        db.close()

        def override_get_db():
            session = self.testing_session()
            try:
                yield session
            finally:
                session.close()

        app = FastAPI()
        app.include_router(courses_router, prefix="/api")
        app.include_router(enrollments_router, prefix="/api")
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = lambda: self.student
        app.dependency_overrides[get_optional_current_user] = lambda: self.student

        self.app = app
        self.client = TestClient(app)

    def test_free_course_enrollment_is_active_immediately(self):
        response = self.client.post("/api/enrollments", json={"course_id": self.free_course.id})

        self.assertEqual(response.status_code, 201)
        payload = response.json()
        self.assertTrue(payload["is_enrolled"])
        self.assertEqual(payload["access_state"], "free")
        self.assertEqual(payload["enrollment"]["status"], EnrollmentStatus.active.value)

    def test_paid_course_requires_manual_approval_before_content_access(self):
        requested = self.client.post(
            "/api/enrollments",
            json={"course_id": self.paid_course.id, "note": "Manual bank transfer requested"},
        )

        self.assertEqual(requested.status_code, 201)
        payload = requested.json()
        self.assertFalse(payload["is_enrolled"])
        self.assertEqual(payload["access_state"], EnrollmentStatus.pending_manual_review.value)

        blocked = self.client.get(f"/api/courses/{self.paid_course.id}/content")
        self.assertEqual(blocked.status_code, 403)

        enrollment_id = payload["enrollment"]["id"]
        self.app.dependency_overrides[get_current_user] = lambda: self.admin
        self.app.dependency_overrides[get_optional_current_user] = lambda: self.admin
        approved = self.client.post(f"/api/enrollments/{enrollment_id}/approve")
        self.assertEqual(approved.status_code, 200)
        self.assertEqual(approved.json()["status"], EnrollmentStatus.active.value)

        self.app.dependency_overrides[get_current_user] = lambda: self.student
        self.app.dependency_overrides[get_optional_current_user] = lambda: self.student
        content = self.client.get(f"/api/courses/{self.paid_course.id}/content")
        self.assertEqual(content.status_code, 200)
        self.assertEqual(content.json()["access_state"], "enrolled")
        self.assertIn("Deployment checklist", content.json()["resources"])


if __name__ == "__main__":
    unittest.main()
