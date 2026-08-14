from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, require_roles
from app.db.session import get_db
from app.models.course import Course
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.models.user import User, UserRole
from app.schemas.enrollment import EnrollmentAccessRead, EnrollmentRead, EnrollmentRequest


router = APIRouter(prefix="/enrollments", tags=["enrollments"])


@router.get("/me", response_model=list[EnrollmentRead])
def list_my_enrollments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Enrollment)
        .filter(Enrollment.user_id == current_user.id)
        .order_by(Enrollment.requested_at.desc())
        .all()
    )


@router.post("", response_model=EnrollmentAccessRead, status_code=status.HTTP_201_CREATED)
def request_enrollment(
    payload: EnrollmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    course = db.get(Course, payload.course_id)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    existing = (
        db.query(Enrollment)
        .filter(Enrollment.user_id == current_user.id, Enrollment.course_id == course.id)
        .one_or_none()
    )
    if existing is not None:
        return _access_response(course, existing)

    if (course.access_type or "free") == "free":
        enrollment = Enrollment(
            user_id=current_user.id,
            course_id=course.id,
            status=EnrollmentStatus.active.value,
            payment_provider="free",
            approved_at=datetime.utcnow(),
            note=payload.note,
        )
    elif not course.manual_enrollment_enabled:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Manual enrollment is disabled for this course")
    else:
        enrollment = Enrollment(
            user_id=current_user.id,
            course_id=course.id,
            status=EnrollmentStatus.pending_manual_review.value,
            payment_provider="manual",
            note=payload.note,
        )

    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return _access_response(course, enrollment)


@router.get("/course/{course_id}/access", response_model=EnrollmentAccessRead)
def read_course_access(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    course = db.get(Course, course_id)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    enrollment = (
        db.query(Enrollment)
        .filter(Enrollment.user_id == current_user.id, Enrollment.course_id == course.id)
        .one_or_none()
    )
    return _access_response(course, enrollment)


@router.post("/{enrollment_id}/approve", response_model=EnrollmentRead)
def approve_enrollment(
    enrollment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.instructor, UserRole.admin)),
):
    enrollment = db.get(Enrollment, enrollment_id)
    if enrollment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
    enrollment.status = EnrollmentStatus.active.value
    enrollment.approved_at = datetime.utcnow()
    enrollment.payment_provider = enrollment.payment_provider or "manual"
    db.commit()
    db.refresh(enrollment)
    return enrollment


def _access_response(course: Course, enrollment: Enrollment | None) -> dict:
    if (course.access_type or "free") == "free":
        access_state = "free"
        is_enrolled = True
    elif enrollment is None:
        access_state = "paid_required"
        is_enrolled = False
    else:
        access_state = "enrolled" if enrollment.status == EnrollmentStatus.active.value else enrollment.status
        is_enrolled = enrollment.status == EnrollmentStatus.active.value

    return {
        "course_id": course.id,
        "access_type": course.access_type or "free",
        "is_enrolled": is_enrolled,
        "access_state": access_state,
        "enrollment": enrollment,
    }
