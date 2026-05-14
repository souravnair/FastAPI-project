from sqlalchemy import Integer, String, Float
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class Patient(Base):
    __tablename__ = "patients"
    
    id: Mapped[str] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    city: Mapped[str] = mapped_column(String(255), index=True)
    age: Mapped[int] = mapped_column(Integer, index=True)
    gender: Mapped[str] = mapped_column(String(255), index=True)
    height: Mapped[float] = mapped_column(Float, index=True)
    weight: Mapped[float] = mapped_column(Float, index=True)
    bmi: Mapped[float] = mapped_column(Float, index=True)
    verdict: Mapped[str] = mapped_column(String(255), index=True)