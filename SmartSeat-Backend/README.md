# SmartSeat Backend (FastAPI)

This is the backend service for the **SmartSeat** project, implemented with FastAPI and SQLite.

## 🚀 Features
- View, create, book, and cancel seats
- SQLite database integration
- RESTful API tested via Swagger UI

## 🧩 API Endpoints
| Method | Endpoint | Description |
|--------|-----------|-------------|
| GET | `/` | Welcome message |
| GET | `/seats` | View all seats |
| POST | `/seats` | Create a seat |
| POST | `/book` | Book a seat |
| POST | `/cancel` | Cancel a booking |

## 🧠 How to Run
```bash
pip install -r requirements.txt
uvicorn smartseat_backend_fastapi:app --reload
```
Then open:  
👉 http://127.0.0.1:8000/docs
