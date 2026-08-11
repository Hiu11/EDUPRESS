import unittest

from app.db.init_db import SEED_BLOG_POSTS, SEED_COURSES, SEED_QUIZ_QUESTIONS
from app.models.content_item import ContentItem
from app.models.course import Course


class CourseSeedDataTest(unittest.TestCase):
    def test_seed_courses_match_course_model_columns(self):
        model_columns = set(Course.__table__.columns.keys())

        for course_data in SEED_COURSES:
            with self.subTest(title=course_data["title"]):
                self.assertLessEqual(set(course_data.keys()), model_columns)
                self.assertIsInstance(Course(**course_data), Course)

    def test_seed_courses_include_required_fields(self):
        required_fields = {"title", "author", "category", "description"}

        for course_data in SEED_COURSES:
            with self.subTest(title=course_data["title"]):
                self.assertLessEqual(required_fields, set(course_data.keys()))
                for field in required_fields:
                    self.assertTrue(course_data[field])

    def test_seed_content_matches_content_model_columns(self):
        model_columns = set(ContentItem.__table__.columns.keys())

        for content_data in [*SEED_BLOG_POSTS, *SEED_QUIZ_QUESTIONS]:
            with self.subTest(title=content_data["title"]):
                row = {"kind": "blog-post", **content_data}
                self.assertLessEqual(set(row.keys()), model_columns)
                self.assertIsInstance(ContentItem(**row), ContentItem)

    def test_seed_quiz_questions_are_frontend_compatible(self):
        required_fields = {"q", "a", "options", "explanation", "difficulty", "topic_tag"}

        for question_data in SEED_QUIZ_QUESTIONS:
            with self.subTest(title=question_data["title"]):
                payload = question_data["payload"]
                self.assertLessEqual(required_fields, set(payload.keys()))
                self.assertIn(payload["a"], payload["options"])


if __name__ == "__main__":
    unittest.main()
