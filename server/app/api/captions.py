from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List
import httpx
import base64
from app.core.config import settings
from app.core.rate_limit import rate_limit

router = APIRouter()

class CaptionLine(BaseModel):
    time: int
    text: str

# Dữ liệu Mock (Dùng khi chưa cấu hình Modal URL)
curated_transcripts = {
    "aircAruvnKk": [
        { "time": 0,   "text": "Giới thiệu: Mạng nơ-ron là gì?" },
        { "time": 15,  "text": "Mỗi lớp nơ-ron học một tính năng khác nhau của dữ liệu." },
        { "time": 40,  "text": "Hàm kích hoạt (activation function) quyết định nơ-ron có 'bật' không." },
    ],
    "default": [
        { "time": 0,   "text": "Bắt đầu bài học — hãy chuẩn bị ghi chú!" },
        { "time": 20,  "text": "Khái niệm nền tảng và ứng dụng thực tế." },
    ]
}

@router.get("/captions/{video_id}", response_model=List[CaptionLine])
async def get_captions(video_id: str):
    captions = curated_transcripts.get(video_id, curated_transcripts["default"])
    return captions

@router.post("/captions/transcribe", dependencies=[Depends(rate_limit(settings.rate_limit_ai_per_minute, 60, "captions-transcribe"))])
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Nhận audio từ client, gọi lên Serverless GPU (Modal) để xử lý.
    """
    if not settings.modal_whisper_url:
        # Fallback to Mock Data if no URL configured
        return {"text": "Đây là kết quả mock vì chưa cấu hình MODAL_WHISPER_URL."}
        
    try:
        audio_bytes = await file.read()
        if len(audio_bytes) > settings.max_upload_bytes:
            raise HTTPException(
                status_code=413,
                detail={
                    "code": "upload_too_large",
                    "message": f"Audio uploads are limited to {settings.max_upload_bytes} bytes.",
                },
            )
        audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.modal_whisper_url,
                json={"audio_b64": audio_b64},
                timeout=30.0  # Cold start trên GPU có thể mất vài giây
            )
            response.raise_for_status()
            result = response.json()
            return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference Error: {str(e)}")
