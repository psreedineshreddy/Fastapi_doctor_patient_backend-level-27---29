from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)

    doctor_id = Column(
    Integer,
    ForeignKey("doctors.id"),
    nullable=False,
    index=True
)
    patient_id = Column(
    Integer,
    ForeignKey("patients.id"),
    nullable=False,
    index=True
)

    appointment_date = Column(
    DateTime,
    nullable=False,
    index=True
)
    created_at = Column(
    DateTime,
    default=datetime.utcnow,
    nullable=False
)

    updated_at = Column(
    DateTime,
    default=datetime.utcnow,
    onupdate=datetime.utcnow,
    nullable=False
)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    status = Column(String, nullable=False, default="scheduled")

    doctor = relationship("Doctor")
    patient = relationship("Patient")