from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from db import get_db_connection

app = FastAPI(title="SmartSeat Admin")

# CORS for local file access in dev (if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# static & templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ---------- pages ----------
@app.get("/", response_class=HTMLResponse)
def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/users", response_class=HTMLResponse)
def users_page(request: Request):
    return templates.TemplateResponse("users.html", {"request": request})

@app.get("/seats", response_class=HTMLResponse)
def seats_page(request: Request):
    return templates.TemplateResponse("seats.html", {"request": request})

@app.get("/maintenance", response_class=HTMLResponse)
def maintenance_page(request: Request):
    return templates.TemplateResponse("maintenance.html", {"request": request})

# ---------- models ----------
class UserIn(BaseModel):
    name: str
    email: EmailStr
    status: str  # Active / Pending / Inactive

class UserOut(UserIn):
    id: int

class SeatIn(BaseModel):
    number: str
    status: str  # available/occupied/maintenance

class SeatOut(SeatIn):
    id: int

class LogIn(BaseModel):
    message: str

class LogOut(BaseModel):
    id: int
    message: str
    created_at: str

# ---------- helpers ----------
def fetch_all(sql, params=None):
    conn = get_db_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params or ())
        return cur.fetchall()
    finally:
        cur.close(); conn.close()

def fetch_one(sql, params=None):
    rows = fetch_all(sql, params)
    return rows[0] if rows else None

def exec_sql(sql, params=None):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        conn.commit()
        return cur.lastrowid
    finally:
        cur.close(); conn.close()

# ---------- APIs: users ----------
@app.get("/api/users", response_model=List[UserOut])
def api_list_users(q: Optional[str] = Query(None)):
    if q:
        like = f"%{q}%"
        return fetch_all("SELECT id,name,email,status FROM users WHERE name LIKE %s OR email LIKE %s ORDER BY id DESC", (like, like))
    return fetch_all("SELECT id,name,email,status FROM users ORDER BY id DESC")

@app.post("/api/users", response_model=UserOut, status_code=201)
def api_create_user(user: UserIn):
    new_id = exec_sql("INSERT INTO users(name,email,status) VALUES(%s,%s,%s)", (user.name, user.email, user.status))
    return {"id": new_id, **user.model_dump()}

@app.put("/api/users/{user_id}", response_model=UserOut)
def api_update_user(user_id: int, user: UserIn):
    exists = fetch_one("SELECT id FROM users WHERE id=%s", (user_id,))
    if not exists:
        raise HTTPException(404, "User not found")
    exec_sql("UPDATE users SET name=%s,email=%s,status=%s WHERE id=%s", (user.name, user.email, user.status, user_id))
    return {"id": user_id, **user.model_dump()}

@app.delete("/api/users/{user_id}", status_code=204)
def api_delete_user(user_id: int):
    exec_sql("DELETE FROM users WHERE id=%s", (user_id,))
    return

# ---------- APIs: seats ----------
@app.get("/api/seats", response_model=List[SeatOut])
def api_list_seats():
    return fetch_all("SELECT id,number,status FROM seats ORDER BY id DESC")

@app.post("/api/seats", response_model=SeatOut, status_code=201)
def api_create_seat(seat: SeatIn):
    new_id = exec_sql("INSERT INTO seats(number,status) VALUES(%s,%s)", (seat.number, seat.status))
    return {"id": new_id, **seat.model_dump()}

@app.put("/api/seats/{seat_id}", response_model=SeatOut)
def api_update_seat(seat_id: int, seat: SeatIn):
    exists = fetch_one("SELECT id FROM seats WHERE id=%s", (seat_id,))
    if not exists:
        raise HTTPException(404, "Seat not found")
    exec_sql("UPDATE seats SET number=%s,status=%s WHERE id=%s", (seat.number, seat.status, seat_id))
    return {"id": seat_id, **seat.model_dump()}

@app.delete("/api/seats/{seat_id}", status_code=204)
def api_delete_seat(seat_id: int):
    exec_sql("DELETE FROM seats WHERE id=%s", (seat_id,))
    return

# ---------- APIs: logs ----------
@app.get("/api/logs", response_model=List[LogOut])
def api_list_logs():
    return fetch_all("SELECT id,message,DATE_FORMAT(created_at,'%%Y-%%m-%%d %%H:%%i:%%s') as created_at FROM reservation_logs ORDER BY id DESC LIMIT 100")

@app.post("/api/logs", response_model=LogOut, status_code=201)
def api_create_log(payload: LogIn):
    new_id = exec_sql("INSERT INTO reservation_logs(message) VALUES(%s)", (payload.message,))
    row = fetch_one("SELECT id,message,DATE_FORMAT(created_at,'%%Y-%%m-%%d %%H:%%i:%%s') as created_at FROM reservation_logs WHERE id=%s", (new_id,))
    return row

# ---------- APIs: maintenance ----------
@app.post("/api/maintenance/backup")
def api_backup():
    exec_sql("INSERT INTO maintenance_audit(action,result) VALUES(%s,%s)", ("backup","ok"))
    return {"status":"ok","message":"Database backup started (simulated)"}

@app.post("/api/maintenance/clear-cache")
def api_clear_cache():
    exec_sql("INSERT INTO maintenance_audit(action,result) VALUES(%s,%s)", ("clear_cache","ok"))
    return {"status":"ok","message":"Cache cleared (simulated)"}

@app.post("/api/maintenance/diagnostics")
def api_diag():
    exec_sql("INSERT INTO maintenance_audit(action,result) VALUES(%s,%s)", ("diagnostics","ok"))
    return {"status":"ok","message":"Diagnostics completed (simulated)"}

@app.get("/api/system/health")
def api_health():
    ok = fetch_one("SELECT 1 as ok") is not None
    return {
        "database": "connected" if ok else "down",
        "server_load": "normal",
        "api_response_ms": 120,
        "last_backup": "2025-11-05 02:30:00"
    }
