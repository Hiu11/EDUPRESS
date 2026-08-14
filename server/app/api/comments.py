from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from pymongo import ReturnDocument
from typing import List
from datetime import datetime
import uuid

from app.core.auth import get_current_user, require_roles
from app.core.config import settings
from app.core.rate_limit import rate_limit
from app.eventbus.producer import event_producer
from app.db.mongo import get_database
from app.models.user import User, UserRole

router = APIRouter(tags=["Comments (CQRS)"])

class CommentCreateCommand(BaseModel):
    post_id: str
    content: str

class CommentResponse(BaseModel):
    id: str
    post_id: str
    user_id: str
    user_name: str | None = None
    content: str
    created_at: str
    moderation_status: str = "visible"

class CommentModerationUpdate(BaseModel):
    moderation_status: str

# COMMAND: Write model (Push to Event Bus)
@router.post("/comments", response_model=dict, dependencies=[Depends(rate_limit(settings.rate_limit_write_per_minute, 60, "comments-write"))])
async def create_comment(cmd: CommentCreateCommand, current_user: User = Depends(get_current_user)):
    comment_id = str(uuid.uuid4())
    event_data = {
        "id": comment_id,
        "post_id": cmd.post_id,
        "user_id": str(current_user.id),
        "user_name": current_user.name,
        "content": cmd.content,
        "moderation_status": "visible",
        "created_at": datetime.utcnow().isoformat()
    }
    
    event = {
        "event_id": str(uuid.uuid4()),
        "event_type": "CommentCreated",
        "timestamp": datetime.utcnow().isoformat(),
        "data": event_data
    }
    
    # Push to Redis (Event Bus)
    await event_producer.send_event("edupress_events", event)
    
    # Return immediately (Async Write)
    return {"status": "accepted", "event_id": event["event_id"], "comment_id": comment_id}

@router.get("/comments/moderation", response_model=List[CommentResponse])
async def list_comments_for_moderation(current_user: User = Depends(require_roles(UserRole.instructor, UserRole.admin))):
    db = get_database()
    if db is None:
        return []

    cursor = db.comments_read_model.find({}).sort("created_at", -1)
    comments = await cursor.to_list(length=100)
    for comment in comments:
        if "_id" in comment:
            del comment["_id"]
        comment["moderation_status"] = comment.get("moderation_status") or "visible"
    return comments


@router.patch("/comments/{comment_id}/moderation", response_model=CommentResponse)
async def update_comment_moderation(
    comment_id: str,
    payload: CommentModerationUpdate,
    current_user: User = Depends(require_roles(UserRole.instructor, UserRole.admin)),
):
    allowed_statuses = {"visible", "hidden", "needs_review"}
    if payload.moderation_status not in allowed_statuses:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Unsupported moderation status")

    db = get_database()
    if db is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Comment store is unavailable")

    result = await db.comments_read_model.find_one_and_update(
        {"id": comment_id},
        {"$set": {"moderation_status": payload.moderation_status}},
        return_document=ReturnDocument.AFTER,
    )
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if "_id" in result:
        del result["_id"]
    result["moderation_status"] = result.get("moderation_status") or "visible"
    return result

# QUERY: Read model (Fetch from MongoDB)
@router.get("/comments/{post_id}", response_model=List[CommentResponse])
async def get_comments(post_id: str):
    db = get_database()
    if db is None:
        return []
        
    cursor = db.comments_read_model.find({
        "post_id": post_id,
        "$or": [{"moderation_status": {"$exists": False}}, {"moderation_status": "visible"}],
    }).sort("created_at", -1)
    comments = await cursor.to_list(length=100)
    
    # Clean up MongoDB _id for Pydantic
    for c in comments:
        if "_id" in c:
            del c["_id"]
        c["moderation_status"] = c.get("moderation_status") or "visible"
            
    return comments
