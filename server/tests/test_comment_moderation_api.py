import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient

import app.api.comments as comments_api
from app.api.comments import router as comments_router
from app.core.auth import get_current_user
from app.models.user import User, UserRole


class FakeCursor:
    def __init__(self, rows):
        self.rows = rows

    def sort(self, *_args, **_kwargs):
        return self

    async def to_list(self, length):
        return self.rows[:length]


class FakeCommentsCollection:
    def __init__(self):
        self.rows = [
            {
                "_id": "mongo-id",
                "id": "comment-1",
                "post_id": "web",
                "user_id": "7",
                "user_name": "Student",
                "content": "Needs moderation",
                "created_at": "2026-08-14T00:00:00",
                "moderation_status": "visible",
            }
        ]

    def find(self, query):
        if query == {}:
            return FakeCursor([row.copy() for row in self.rows])
        rows = [
            row.copy()
            for row in self.rows
            if row["post_id"] == query["post_id"] and row.get("moderation_status", "visible") == "visible"
        ]
        return FakeCursor(rows)

    async def find_one_and_update(self, selector, update, return_document=None):
        for row in self.rows:
            if row["id"] == selector["id"]:
                row.update(update["$set"])
                return row.copy()
        return None


class FakeDatabase:
    def __init__(self):
        self.comments_read_model = FakeCommentsCollection()


class CommentModerationApiTest(unittest.TestCase):
    def setUp(self):
        self.db = FakeDatabase()
        self.original_get_database = comments_api.get_database
        comments_api.get_database = lambda: self.db

        app = FastAPI()
        app.include_router(comments_router, prefix="/api")
        app.dependency_overrides[get_current_user] = lambda: User(
            id=1,
            email="admin@example.com",
            name="Admin",
            hashed_password="hashed",
            role=UserRole.admin.value,
        )
        self.client = TestClient(app)

    def tearDown(self):
        comments_api.get_database = self.original_get_database

    def test_admin_can_hide_comment_from_public_thread(self):
        moderation_list = self.client.get("/api/comments/moderation")
        self.assertEqual(moderation_list.status_code, 200)
        self.assertEqual(moderation_list.json()[0]["moderation_status"], "visible")

        updated = self.client.patch("/api/comments/comment-1/moderation", json={"moderation_status": "hidden"})
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json()["moderation_status"], "hidden")

        public_thread = self.client.get("/api/comments/web")
        self.assertEqual(public_thread.status_code, 200)
        self.assertEqual(public_thread.json(), [])


if __name__ == "__main__":
    unittest.main()
