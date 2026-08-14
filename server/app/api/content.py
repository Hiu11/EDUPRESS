from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import require_roles
from app.db.session import get_db
from app.models.content_item import ContentItem
from app.models.course import Course
from app.models.user import User, UserRole
from app.schemas.content import ContentItemCreate, ContentItemRead, ContentItemUpdate

router = APIRouter(prefix="/content", tags=["content"])

CONTENT_KINDS = {"blog-post", "quiz-question"}


def _list_items(kind: str, db: Session) -> list[dict]:
    items = db.query(ContentItem).filter(ContentItem.kind == kind).order_by(ContentItem.id.asc()).all()
    return [_to_frontend_payload(item) for item in items]


def _to_frontend_payload(item: ContentItem) -> dict:
    return {
        "id": item.id,
        "slug": item.slug,
        "title": item.title,
        **(item.payload or {}),
    }


@router.get("/blog-posts")
def list_blog_posts(db: Session = Depends(get_db)):
    return _list_items("blog-post", db)


@router.get("/quiz-questions")
def list_quiz_questions(db: Session = Depends(get_db)):
    return _list_items("quiz-question", db)


@router.get("/operations/summary")
def read_operations_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.instructor, UserRole.admin)),
):
    return {
        "courses": db.query(Course).count(),
        "blog_posts": db.query(ContentItem).filter(ContentItem.kind == "blog-post").count(),
        "quiz_questions": db.query(ContentItem).filter(ContentItem.kind == "quiz-question").count(),
        "operator_role": current_user.role,
    }


@router.post("/{kind}", response_model=ContentItemRead, status_code=status.HTTP_201_CREATED)
def create_content_item(
    kind: str,
    payload: ContentItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.instructor, UserRole.admin)),
):
    if kind not in CONTENT_KINDS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unsupported content type")

    existing = db.query(ContentItem).filter(ContentItem.slug == payload.slug).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Content slug already exists")

    item = ContentItem(kind=kind, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/{kind}/admin", response_model=list[ContentItemRead])
def list_content_items_for_operations(
    kind: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.instructor, UserRole.admin)),
):
    if kind not in CONTENT_KINDS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unsupported content type")
    return db.query(ContentItem).filter(ContentItem.kind == kind).order_by(ContentItem.id.desc()).all()


@router.patch("/{kind}/{item_id}", response_model=ContentItemRead)
def update_content_item(
    kind: str,
    item_id: int,
    payload: ContentItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.instructor, UserRole.admin)),
):
    if kind not in CONTENT_KINDS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unsupported content type")
    item = db.get(ContentItem, item_id)
    if item is None or item.kind != kind:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content item not found")

    updates = payload.model_dump(exclude_unset=True)
    if "slug" in updates and updates["slug"] != item.slug:
        existing = db.query(ContentItem).filter(ContentItem.slug == updates["slug"]).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Content slug already exists")
    for field, value in updates.items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item
