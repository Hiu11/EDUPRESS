import unittest

from app.db.init_db import SEED_COURSES
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


if __name__ == "__main__":
    unittest.main()
