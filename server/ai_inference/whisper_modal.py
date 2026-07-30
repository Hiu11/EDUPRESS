import modal
from pydantic import BaseModel

# 1. Định nghĩa môi trường Docker chạy trên Serverless GPU
image = modal.Image.debian_slim(python_version="3.10").pip_install(
    "transformers", "torch", "librosa", "soundfile", "accelerate"
)

app = modal.App("edupress-whisper-inference")

# 2. Mount model vào Memory khi container khởi động (Cold Start Optimization)
@app.cls(gpu="T4", image=image, keep_warm=0, container_idle_timeout=60)
class WhisperModel:
    @modal.enter()
    def load_model(self):
        import torch
        from transformers import pipeline
        
        print("Loading Whisper model into GPU memory...")
        # Sử dụng Whisper nhỏ gọn để demo tốc độ
        self.pipe = pipeline(
            "automatic-speech-recognition",
            model="openai/whisper-tiny",
            device="cuda:0" if torch.cuda.is_available() else "cpu"
        )
        print("Model loaded successfully!")

    @modal.method()
    def transcribe(self, audio_bytes: bytes) -> str:
        # Trong thực tế, xử lý bytes thành numpy array với librosa/soundfile ở đây
        # Để demo, ta giả lập kết quả
        result = self.pipe(audio_bytes)
        return result["text"]

# 3. Tạo REST API tự động scale về 0 khi không có Request
@app.function(image=image)
@modal.web_endpoint(method="POST")
def api_transcribe(item: dict):
    # Lấy model ra chạy
    model = WhisperModel()
    # Ở đây nhận base64 audio, decode thành bytes rồi truyền vào
    # Demo code:
    import base64
    audio_bytes = base64.b64decode(item.get("audio_b64", ""))
    
    text = model.transcribe.remote(audio_bytes)
    return {"text": text}
