from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.auth import require_roles
from app.db.session import get_db
from app.models.course import Course
from app.models.user import User, UserRole
from app.schemas.course import CourseCreate, CourseRead

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=list[CourseRead])
def list_courses(db: Session = Depends(get_db)):
    return [_serialize_course(course) for course in db.query(Course).order_by(Course.id.desc()).all()]


@router.post("", response_model=CourseRead, status_code=status.HTTP_201_CREATED)
def create_course(
    payload: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.instructor, UserRole.admin)),
):
    course = Course(**payload.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return _serialize_course(course)


def _serialize_course(course: Course) -> dict:
    return {
        "id": course.id,
        "slug": course.slug,
        "title": course.title,
        "author": course.author,
        "category": course.category,
        "description": course.description,
        "image_url": course.image_url,
        "level": course.level,
        "lessons": course.lessons or 0,
        "duration": course.duration,
        "rating": course.rating or 0,
        "students": course.students or 0,
        "progress": course.progress or 0,
        "tag": course.tag,
        "outcomes": course.outcomes or [],
        "syllabus": course.syllabus or [],
        "resources": course.resources or [],
    }
