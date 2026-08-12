from sqlalchemy import inspect, text

from app.db.base import Base
from app.db.session import engine
from app.models.content_item import ContentItem  # noqa: F401
from app.models.course import Course  # noqa: F401
from app.models.user import User  # noqa: F401
from app.db.session import SessionLocal


SEED_COURSES = [
    {
        "slug": "ai",
        "title": "Trí tuệ nhân tạo ứng dụng",
        "author": "MindX",
        "category": "AI",
        "description": "Nền tảng AI, machine learning, xử lý dữ liệu và cách đưa mô hình vào sản phẩm học tập thực tế.",
        "image_url": "course-ai-bg.png",
        "level": "Intermediate",
        "lessons": 18,
        "duration": "8 tuần",
        "rating": 4.8,
        "students": 482,
        "progress": 72,
        "tag": "Bán chạy",
        "outcomes": ["Hiểu quy trình xây mô hình AI", "Biết chuẩn bị dữ liệu và đánh giá kết quả", "Tạo prototype AI assistant cho lớp học"],
        "syllabus": ["Tổng quan AI và ứng dụng giáo dục", "Machine learning căn bản", "Xử lý dữ liệu học viên", "Prompt workflow và đánh giá mô hình", "Triển khai demo AI assistant"],
        "resources": ["Bộ dataset mẫu", "Notebook thực hành", "Rubric đánh giá project"],
    },
    {
        "slug": "oop",
        "title": "Lập trình hướng đối tượng",
        "author": "MindX",
        "category": "Software Engineering",
        "description": "Nắm vững class, object, kế thừa, đa hình và cách tổ chức phần mềm theo module rõ ràng.",
        "image_url": "course-oop-bg.png",
        "level": "Beginner",
        "lessons": 14,
        "duration": "6 tuần",
        "rating": 4.7,
        "students": 356,
        "progress": 46,
        "tag": "Căn bản",
        "outcomes": ["Thiết kế class đúng trách nhiệm", "Refactor code procedural sang OOP", "Xây mini project quản lý khóa học"],
        "syllabus": ["Class, object và constructor", "Encapsulation và validation", "Inheritance và composition", "Polymorphism", "Project cuối khóa"],
        "resources": ["Source code starter", "Bài tập UML", "Checklist clean code"],
    },
    {
        "slug": "web",
        "title": "Phát triển ứng dụng web",
        "author": "MindX",
        "category": "Web Development",
        "description": "Xây dựng web app hiện đại từ giao diện, API, database đến deployment với quy trình làm việc giống dự án thật.",
        "image_url": "course-web-bg.png",
        "level": "Advanced",
        "lessons": 22,
        "duration": "10 tuần",
        "rating": 4.9,
        "students": 628,
        "progress": 88,
        "tag": "Project-based",
        "outcomes": ["Xây SPA bằng component", "Thiết kế REST API", "Kết nối database và deploy sản phẩm"],
        "syllabus": ["HTML/CSS nâng cao", "Vue component architecture", "FastAPI REST endpoint", "PostgreSQL data modeling", "Deploy và review sản phẩm"],
        "resources": ["UI kit", "API checklist", "Deployment guide"],
    },
    {
        "slug": "ui",
        "title": "Thiết kế giao diện học tập",
        "author": "MindX",
        "category": "Design",
        "description": "Học nguyên tắc layout, màu sắc, typography và thiết kế trải nghiệm học tập trực tuyến dễ dùng.",
        "image_url": "course-ui-bg.png",
        "level": "Beginner",
        "lessons": 12,
        "duration": "5 tuần",
        "rating": 4.6,
        "students": 241,
        "progress": 34,
        "tag": "Workshop",
        "outcomes": ["Thiết kế wireframe LMS", "Xây visual system", "Review accessibility cơ bản"],
        "syllabus": ["Design principles", "Wireframe và user flow", "Responsive UI", "Design system", "Prototype review"],
        "resources": ["Figma template", "Color token guide", "Accessibility checklist"],
    },
]

SEED_BLOG_POSTS = [
    {
        "slug": "xu-huong-hoc-truc-tuyen-2026",
        "title": "Xu hướng học trực tuyến năm 2026",
        "payload": {
            "image": "news1.jpg",
            "category": "EdTech",
            "date": "12/06/2026",
            "excerpt": "Cá nhân hóa lộ trình, quiz tương tác và nội dung ngắn đang thay đổi cách người học tiếp cận tri thức.",
        },
    },
    {
        "slug": "ai-ho-tro-giang-vien-tao-khoa-hoc",
        "title": "AI hỗ trợ giảng viên tạo khóa học",
        "payload": {
            "image": "news2.jpg",
            "category": "AI",
            "date": "18/06/2026",
            "excerpt": "Công cụ AI giúp tạo đề cương, gợi ý bài tập và theo dõi mức độ hoàn thành của học viên.",
        },
    },
    {
        "slug": "hoc-hieu-qua-voi-lms",
        "title": "Cách học hiệu quả với LMS",
        "payload": {
            "image": "news4.jpg",
            "category": "Learning",
            "date": "24/06/2026",
            "excerpt": "Một hệ thống LMS tốt cần có tiến trình rõ ràng, phản hồi nhanh và dữ liệu học tập dễ theo dõi.",
        },
    },
]

SEED_QUIZ_QUESTIONS = [
    {
        "slug": "html-structure",
        "title": "HTML dùng để làm gì trong lập trình web?",
        "payload": {
            "q": "HTML dùng để làm gì trong lập trình web?",
            "a": "Cấu trúc nội dung trang web",
            "options": ["Thiết kế giao diện màu sắc", "Cấu trúc nội dung trang web", "Xử lý logic phía server", "Quản lý database"],
            "explanation": "HTML phụ trách cấu trúc và ngữ nghĩa nội dung. CSS phụ trách giao diện, JavaScript xử lý tương tác.",
            "difficulty": "easy",
            "topic_tag": "HTML Basics",
        },
    },
    {
        "slug": "css-layout",
        "title": "CSS Flexbox và CSS Grid khác nhau ở điểm nào chính?",
        "payload": {
            "q": "CSS Flexbox và CSS Grid khác nhau ở điểm nào chính?",
            "a": "Flexbox là 1 chiều, Grid là 2 chiều",
            "options": ["Flexbox nhanh hơn Grid", "Flexbox là 1 chiều, Grid là 2 chiều", "Grid chỉ dùng được trên Desktop", "Chúng hoàn toàn giống nhau"],
            "explanation": "Flexbox phù hợp bố cục một chiều, còn Grid xử lý hàng và cột cùng lúc.",
            "difficulty": "medium",
            "topic_tag": "CSS Layout",
        },
    },
    {
        "slug": "rest-put",
        "title": "REST API dùng HTTP method nào để cập nhật toàn bộ resource?",
        "payload": {
            "q": "REST API dùng HTTP method nào để cập nhật toàn bộ một resource?",
            "a": "PUT",
            "options": ["GET", "POST", "PUT", "DELETE"],
            "explanation": "PUT thay thế toàn bộ resource. PATCH chỉ cập nhật một phần.",
            "difficulty": "medium",
            "topic_tag": "REST API",
        },
    },
]


def init_db():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        _ensure_course_columns(db)
        if db.query(Course).count() == 0:
            print("Seeding starter courses...")
            db.add_all(Course(**course_data) for course_data in SEED_COURSES)
            db.commit()
        if db.query(ContentItem).count() == 0:
            print("Seeding starter content...")
            db.add_all(ContentItem(kind="blog-post", **post_data) for post_data in SEED_BLOG_POSTS)
            db.add_all(ContentItem(kind="quiz-question", **question_data) for question_data in SEED_QUIZ_QUESTIONS)
            db.commit()
    finally:
        db.close()


def _ensure_course_columns(db):
    inspector = inspect(engine)
    if not inspector.has_table(Course.__tablename__):
        return

    existing_columns = {column["name"] for column in inspector.get_columns(Course.__tablename__)}
    for column in Course.__table__.columns:
        if column.name in existing_columns:
            continue
        column_type = column.type.compile(dialect=engine.dialect)
        db.execute(text(f"ALTER TABLE {Course.__tablename__} ADD COLUMN {column.name} {column_type}"))
    db.commit()


if __name__ == "__main__":
    init_db()
