from sqlalchemy import Column, Integer, String, Float, DateTime, func, Boolean, BigInteger
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String(length=2000), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    category = Column(String(length=100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    source = Column(String(length=100), nullable=True)
    cluster_id = Column(Integer, nullable=True)
    has_photo = Column(Boolean, default=False)  # ✅ Добавь это поле
    photo_filename = Column(String(length=255), nullable=True)  # ✅ Или это для имени файла
    telegram_user_id = Column(BigInteger, nullable=True)  # ✅ Добавляем ID пользователя