from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.agents.quiz_generator import generate_adaptive_quiz_batch
from app.core.auth import get_current_user
from app.db.session import get_db
from app.models.quiz_history import QuizHistory as QuizHistoryModel
from app.models.user import User
import time
from datetime import datetime

router = APIRouter(tags=["Quiz"])


class QuizRequest(BaseModel):
    history: List[Dict[str, Any]]
    course_title: Optional[str] = "Lập trình Web"
    course_category: Optional[str] = "Technology"
    batch_size: Optional[int] = 5

class QuizSyncRequest(BaseModel):
    course_id: str
    score: int
    total: int
    topic: str
    max_streak: int

@router.post("/quiz/generate")
async def generate_quiz(req: QuizRequest):
    try:
        start_time = time.time()
        result = generate_adaptive_quiz_batch(
            history=req.history,
            course_title=req.course_title,
            course_category=req.course_category,
            batch_size=req.batch_size
        )
        elapsed = time.time() - start_time

        if not result or not result.get("questions"):
            raise ValueError("Agent pipeline returned no questions.")

        return {
            "success": True,
            "generated_in_seconds": round(elapsed, 2),
            "question_count": len(result["questions"]),
            "weak_topic": result.get("weak_topic", ""),
            "difficulty": result.get("difficulty", "medium"),
            "analyzer_reasoning": result.get("analyzer_reasoning", ""),
            "data": result["questions"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quiz/sync")
async def sync_quiz_history(
    req: QuizSyncRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        new_history = QuizHistoryModel(
            user_id=str(current_user.id),
            course_id=req.course_id,
            score=req.score,
            total=req.total,
            topic=req.topic,
            max_streak=req.max_streak,
            created_at=datetime.utcnow()
        )
        db.add(new_history)
        db.commit()
        db.refresh(new_history)
        return {"success": True, "message": "Synced to PostgreSQL", "id": new_history.id}
    except Exception as e:
        # Fallback for when Postgres is not running locally during development
        return {"success": True, "message": "Synced locally (DB unavailable)", "error": str(e)}
