from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_optional_current_user, require_roles
from app.db.session import get_db
from app.models.course import Course
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.models.user import User, UserRole
from app.schemas.course import CourseContentRead, CourseCreate, CourseRead

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=list[CourseRead])
def list_courses(db: Session = Depends(get_db)):
    return [_serialize_course(course) for course in db.query(Course).order_by(Course.id.desc()).all()]


@router.get("/{course_id}/content", response_model=CourseContentRead)
def read_course_content(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    course = db.get(Course, course_id)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    access_state = _course_access_state(db, course, current_user)
    if access_state == "authentication_required":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required for paid course content",
        )
    if access_state in {"paid_required", "pending_manual_review"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Enrollment required for paid course content",
        )

    serialized = _serialize_course(course)
    return {
        "id": serialized["id"],
        "slug": serialized["slug"],
        "title": serialized["title"],
        "access_type": serialized["access_type"],
        "outcomes": serialized["outcomes"],
        "syllabus": serialized["syllabus"],
        "resources": serialized["resources"],
        "access_state": access_state,
    }


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
        "access_type": course.access_type or "free",
        "price_cents": course.price_cents or 0,
        "currency": course.currency or "VND",
        "manual_enrollment_enabled": course.manual_enrollment_enabled,
        "outcomes": course.outcomes or [],
        "syllabus": course.syllabus or [],
        "resources": course.resources or [],
    }


def _course_access_state(db: Session, course: Course, current_user: User | None) -> str:
    if (course.access_type or "free") == "free":
        return "free"
    if current_user is None:
        return "authentication_required"
    enrollment = (
        db.query(Enrollment)
        .filter(Enrollment.course_id == course.id, Enrollment.user_id == current_user.id)
        .one_or_none()
    )
    if enrollment is None:
        return "paid_required"
    if enrollment.status == EnrollmentStatus.active.value:
        return "enrolled"
    return enrollment.status
