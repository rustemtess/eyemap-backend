from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import asyncio, os
from dotenv import load_dotenv  # ✅ добавлено
load_dotenv()                   # ✅ добавлено

from app.database import engine, init_db
from app.routers import reports, webhook
from app import models

app = FastAPI(title="EyeMap API — Postgres/PostGIS")

app.include_router(reports.router)
app.include_router(webhook.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Или конкретные домены ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    # create tables and PostGIS extension if needed
    await init_db()

@app.get("/")
async def root():
    return {"status": "ok", "service": "EyeMap API (Postgres/PostGIS)"}
@app.get("/photo/{report_id}")
async def view_photo(report_id: int):
    """Страница просмотра фото репорта"""
    photo_path = f"static/uploads/report_{report_id}.jpg"
    
    if not os.path.exists(photo_path):
        raise HTTPException(status_code=404, detail="Photo not found")
    
    return FileResponse(photo_path)
