from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, require_roles
from app.core.config import settings
from app.core.rate_limit import rate_limit
from app.core.security import create_access_token, hash_password, verify_password
from app.db.mongo import get_database
from app.db.session import get_db
from app.models.enrollment import Enrollment
from app.models.quiz_history import QuizHistory
from app.models.user import User, UserRole
from app.schemas.auth import LearnerDataExport, LoginRequest, RegisterRequest, TokenResponse, UserAdminUpdate, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit(settings.rate_limit_auth_per_minute, 60, "auth-register"))],
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered")

    user = User(
        email=email,
        name=payload.name.strip(),
        hashed_password=hash_password(payload.password),
        role=UserRole.student.value,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    dependencies=[Depends(rate_limit(settings.rate_limit_auth_per_minute, 60, "auth-login"))],
)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    user = db.query(User).filter(User.email == email).first()
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is disabled")

    return _token_response(user)


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/me/export", response_model=LearnerDataExport)
async def export_current_user_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    quiz_history = [
        {
            "id": item.id,
            "course_id": item.course_id,
            "score": item.score,
            "total": item.total,
            "topic": item.topic,
            "max_streak": item.max_streak,
            "created_at": item.created_at.isoformat() if item.created_at else None,
        }
        for item in db.query(QuizHistory).filter(QuizHistory.user_id == str(current_user.id)).order_by(QuizHistory.created_at.desc()).all()
    ]
    enrollments = [
        {
            "id": item.id,
            "course_id": item.course_id,
            "status": item.status,
            "payment_provider": item.payment_provider,
            "payment_reference": item.payment_reference,
            "note": item.note,
            "requested_at": item.requested_at.isoformat() if item.requested_at else None,
            "approved_at": item.approved_at.isoformat() if item.approved_at else None,
            "expires_at": item.expires_at.isoformat() if item.expires_at else None,
        }
        for item in db.query(Enrollment).filter(Enrollment.user_id == current_user.id).order_by(Enrollment.requested_at.desc()).all()
    ]

    comments = []
    mongo = get_database()
    if mongo is not None:
        cursor = mongo.comments_read_model.find({"user_id": str(current_user.id)}).sort("created_at", -1)
        comments = await cursor.to_list(length=500)
        for comment in comments:
            comment.pop("_id", None)

    return {
        "user": current_user,
        "quiz_history": quiz_history,
        "enrollments": enrollments,
        "comments": comments,
        "retention_policy": {
            "local_browser_storage": "Learner profile, session marker, quiz history, and course interactions remain in browser IndexedDB until the learner clears them or deletes the local account.",
            "postgres": "User accounts, enrollments, and quiz history are retained while the account is active and removed when the learner deletes the account.",
            "mongo_comments": "Comment read models are removed with account deletion when MongoDB is available.",
            "backups": "Production backups should be rotated on a documented schedule and excluded from ad hoc product access.",
        },
    }


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db.query(QuizHistory).filter(QuizHistory.user_id == str(current_user.id)).delete(synchronize_session=False)
    db.query(Enrollment).filter(Enrollment.user_id == current_user.id).delete(synchronize_session=False)

    mongo = get_database()
    if mongo is not None:
        await mongo.comments_read_model.delete_many({"user_id": str(current_user.id)})

    user = db.get(User, current_user.id)
    if user is not None:
        db.delete(user)
    db.commit()
    return None


@router.get("/users", response_model=list[UserRead])
def list_users_for_admin(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin)),
):
    return db.query(User).order_by(User.id.asc()).all()


@router.patch("/users/{user_id}", response_model=UserRead)
def update_user_for_admin(
    user_id: int,
    payload: UserAdminUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin)),
):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    updates = payload.model_dump(exclude_unset=True)
    if "role" in updates and updates["role"] is not None:
        user.role = updates["role"].value
    if "is_active" in updates and updates["is_active"] is not None:
        user.is_active = updates["is_active"]
    db.commit()
    db.refresh(user)
    return user


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(current_user: User = Depends(get_current_user)):
    return _token_response(current_user)


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    return {"success": True, "message": "Logged out"}


def _token_response(user: User) -> TokenResponse:
    token = create_access_token(str(user.id), {"role": user.role})
    return TokenResponse(access_token=token, expires_in_minutes=settings.jwt_expires_minutes)
