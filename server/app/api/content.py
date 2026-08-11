from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import require_roles
from app.db.session import get_db
from app.models.content_item import ContentItem
from app.models.user import User, UserRole
from app.schemas.content import ContentItemCreate, ContentItemRead

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
