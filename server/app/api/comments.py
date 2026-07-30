from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid
import json

from app.eventbus.producer import event_producer
from app.db.mongo import get_database

router = APIRouter(tags=["Comments (CQRS)"])

class CommentCreateCommand(BaseModel):
    post_id: str
    user_id: str
    content: str

class CommentResponse(BaseModel):
    id: str
    post_id: str
    user_id: str
    content: str
    created_at: str

# COMMAND: Write model (Push to Event Bus)
@router.post("/comments", response_model=dict)
async def create_comment(cmd: CommentCreateCommand):
    comment_id = str(uuid.uuid4())
    event_data = {
        "id": comment_id,
        "post_id": cmd.post_id,
        "user_id": cmd.user_id,
        "content": cmd.content,
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

# QUERY: Read model (Fetch from MongoDB)
@router.get("/comments/{post_id}", response_model=List[CommentResponse])
async def get_comments(post_id: str):
    db = get_database()
    if db is None:
        return []
        
    cursor = db.comments_read_model.find({"post_id": post_id}).sort("created_at", -1)
    comments = await cursor.to_list(length=100)
    
    # Clean up MongoDB _id for Pydantic
    for c in comments:
        if "_id" in c:
            del c["_id"]
            
    return comments
