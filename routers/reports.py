from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pathlib import Path  
import shutil, random

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api", tags=["reports"])

@router.post("/reports", response_model=schemas.ReportOut, status_code=201)
async def create_report(
    description: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    category: str = Form("telegram"),
    source: str = Form("telegram_bot"),
    photo: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
    telegram_user_id: int = Form(None),  # ✅ Добавляем параметр для user_id
):
    print(f"🔍 DEBUG: Starting report creation")  # ✅ Лог
    print(f"🔍 DEBUG: Photo object: {photo}")  # ✅ Лог
    print(f"🔍 DEBUG: Photo filename: {photo.filename if photo else 'None'}")  # ✅ Лог
    
    try:
        report = models.Report(
            description=description,
            latitude=latitude,
            longitude=longitude,
            category=category,
            source=source,
            has_photo=photo is not None,
            telegram_user_id=telegram_user_id  # ✅ Сохраняем user_id
        )
        
        db.add(report)
        await db.flush()
        print(f"🔍 DEBUG: Report ID: {report.id}")  # ✅ Лог
        
        # Сохраняем фото если есть
        if photo and photo.filename:
            print(f"🔍 DEBUG: Processing photo...")  # ✅ Лог
            
            upload_dir = Path("static/uploads")
            upload_dir.mkdir(parents=True, exist_ok=True)
            print(f"🔍 DEBUG: Upload dir: {upload_dir.absolute()}")  # ✅ Лог
            
            file_extension = photo.filename.split('.')[-1] if '.' in photo.filename else 'jpg'
            filename = f"report_{report.id}.{file_extension}"
            file_path = upload_dir / filename
            
            print(f"🔍 DEBUG: Saving to: {file_path}")  # ✅ Лог
            
            # Сохраняем файл
            with open(file_path, "wb") as buffer:
                content = await photo.read()
                print(f"🔍 DEBUG: Photo size: {len(content)} bytes")  # ✅ Лог
                buffer.write(content)
            
            # Проверяем что файл создался
            if file_path.exists():
                print(f"✅ DEBUG: Photo successfully saved as {filename}")  # ✅ Лог
                print(f"🔍 DEBUG: File size: {file_path.stat().st_size} bytes")  # ✅ Лог
            else:
                print(f"❌ DEBUG: File was not created!")  # ✅ Лог
        
        else:
            print(f"🔍 DEBUG: No photo to save")  # ✅ Лог
        
        await db.commit()
        await db.refresh(report)
        print(f"✅ DEBUG: Report created successfully")  # ✅ Лог
        return report
        
    except Exception as e:
        print(f"❌ DEBUG: Error: {e}")  # ✅ Лог
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/reports", response_model=List[schemas.ReportOut])
async def list_reports(db: AsyncSession = Depends(get_db), id: Optional[int] = Query(None)):
    if id is not None:
        q = await db.execute(select(models.Report).where(models.Report.id == id))
        r = q.scalars().first()
        if not r:
            raise HTTPException(status_code=404, detail="Report not found")
        return [r]
    q = await db.execute(select(models.Report).order_by(models.Report.created_at.desc()).limit(1000))
    results = q.scalars().all()
    return results

@router.get("/reports/geojson")
async def reports_geojson(db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.Report))
    reports = q.scalars().all()
    features = []
    for rep in reports:
        feature = {
            "type": "Feature",
            "properties": {
                "id": rep.id,
                "description": rep.description,
                "category": rep.category,
                "source": rep.source,
                "cluster_id": rep.cluster_id,
                "has_photo": rep.has_photo,
                "created_at": rep.created_at.isoformat() if rep.created_at else None,
                "telegram_user_id": rep.telegram_user_id,
                "verified": random.choice(['Подтверждено', 'В ожидании', 'Отклонено'])
            },
            "geometry": {
                "type": "Point",
                "coordinates": [rep.longitude, rep.latitude],
            }
        }
        
        # Добавляем URL фото если есть
        if rep.has_photo:
            feature["properties"]["photo_url"] = f"/static/uploads/report_{rep.id}.jpg"
        
        features.append(feature)
    
    return {"type": "FeatureCollection", "features": features}

@router.get("/reports/{report_id}", response_model=schemas.ReportOut)
async def get_report(report_id: int, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.Report).where(models.Report.id == report_id))
    r = q.scalars().first()
    if not r:
        raise HTTPException(status_code=404, detail="Report not found")
    return r
