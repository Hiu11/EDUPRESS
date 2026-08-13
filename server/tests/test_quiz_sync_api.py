import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.quiz import router as quiz_router
from app.core.auth import get_current_user
from app.db.base import Base
from app.db.session import get_db
from app.models.quiz_history import QuizHistory  # noqa: F401
from app.models.user import User


class FailingCommitSession:
    def __init__(self):
        self.rolled_back = False

    def add(self, _model):
        return None

    def commit(self):
        raise RuntimeError("database write failed")

    def refresh(self, _model):
        return None

    def rollback(self):
        self.rolled_back = True

    def close(self):
        return None


class QuizSyncApiTest(unittest.TestCase):
    def setUp(self):
        self.user = User(id=7, email="learner@example.com", name="Learner", hashed_password="x")

    def _client(self, override_db):
        app = FastAPI()
        app.include_router(quiz_router, prefix="/api")
        app.dependency_overrides[get_current_user] = lambda: self.user
        app.dependency_overrides[get_db] = override_db
        return TestClient(app)

    def test_sync_returns_success_when_history_is_persisted(self):
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

        response = self._client(override_get_db).post(
            "/api/quiz/sync",
            json={"course_id": "web", "score": 4, "total": 5, "topic": "REST API", "max_streak": 3},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertIsInstance(response.json()["id"], int)

    def test_sync_returns_error_when_database_write_fails(self):
        failing_session = FailingCommitSession()

        def override_get_db():
            yield failing_session

        response = self._client(override_get_db).post(
            "/api/quiz/sync",
            json={"course_id": "web", "score": 4, "total": 5, "topic": "REST API", "max_streak": 3},
        )

        self.assertEqual(response.status_code, 503)
        self.assertTrue(failing_session.rolled_back)
        self.assertFalse(response.json()["detail"]["success"])
        self.assertEqual(response.json()["detail"]["code"], "quiz_sync_failed")


if __name__ == "__main__":
    unittest.main()
