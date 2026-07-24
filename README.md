# EduPress

Live demo: https://edupress-lms.vercel.app

EduPress là nền tảng học trực tuyến mô phỏng hệ thống LMS (Learning Management System). Dự án hiện đã được nâng cấp từ bản HTML/CSS/JavaScript tĩnh sang kiến trúc full-stack với Vue 3 ở frontend và FastAPI ở backend.

## Tính năng chính

- Hiển thị trang giới thiệu nền tảng học trực tuyến EduPress.
- Danh sách khóa học lấy từ API backend.
- API kiểm tra trạng thái hệ thống.
- Cấu trúc sẵn sàng mở rộng cho xác thực, quản lý khóa học, học viên và nội dung học tập.
- Tách riêng frontend, backend và tài nguyên giao diện.

## Công nghệ sử dụng

| Phần | Công nghệ |
| --- | --- |
| Frontend | Vue 3, Vite, JavaScript, CSS |
| Backend | FastAPI, Python |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| API | REST |

## Cấu trúc thư mục

```txt
EDUPRESS/
├── client/                 # Ứng dụng Vue 3
│   ├── public/             # Favicon, icon, ảnh public
│   ├── src/                # Source code frontend
│   ├── package.json
│   └── vite.config.js
│
├── server/                 # Ứng dụng FastAPI
│   ├── app/
│   │   ├── api/            # Router API
│   │   ├── core/           # Cấu hình ứng dụng
│   │   ├── db/             # Kết nối và khởi tạo database
│   │   ├── models/         # SQLAlchemy models
│   │   └── schemas/        # Pydantic schemas
│   ├── .env.example
│   ├── requirements.txt
│   └── README.md
│
└── README.md
```

## Yêu cầu môi trường

- Node.js
- npm
- Python 3.10 trở lên
- PostgreSQL

## Cài đặt và chạy dự án

### 1. Clone hoặc mở thư mục dự án

```powershell
cd EDUPRESS
```

### 2. Chạy backend

Tạo database PostgreSQL tên `edupress`, sau đó chạy:

```powershell
cd server
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Backend mặc định chạy tại:

```txt
http://localhost:8000
```

### 3. Chạy frontend

Mở terminal khác:

```powershell
cd client
npm install
npm run dev
```

Frontend mặc định chạy tại:

```txt
http://localhost:5173
```

## Biến môi trường backend

File cấu hình mẫu nằm tại `server/.env.example`.

```env
APP_NAME=EduPress API
APP_ENV=development
CLIENT_ORIGIN=http://localhost:5173
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/edupress
JWT_SECRET=change-me-in-production
JWT_EXPIRES_MINUTES=1440
```

Nếu tài khoản PostgreSQL của bạn khác `postgres/postgres`, hãy sửa lại `DATABASE_URL` trong `server/.env`.

## API hiện có

| Method | Endpoint | Mô tả |
| --- | --- | --- |
| GET | `/health` | Kiểm tra trạng thái API |
| GET | `/api/courses` | Lấy danh sách khóa học |

## Build frontend

```powershell
cd client
npm run build
```

## Tác giả

Đây là dự án cá nhân, được thực hiện nhằm xây dựng và nâng cấp nền tảng học trực tuyến EduPress từ giao diện tĩnh sang mô hình full-stack.

## Hướng phát triển

- Hoàn thiện chức năng đăng ký, đăng nhập và phân quyền.
- Thêm trang chi tiết khóa học, bài học, quiz và tiến trình học tập.
- Xây dựng chức năng quản trị khóa học.
- Bổ sung seed data và migration database.
- Triển khai frontend và backend lên môi trường production.
