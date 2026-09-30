from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class Billing(Base):
    __tablename__ = "billings"

    __table_args__ = (
    UniqueConstraint(
        "appointment_id",
        name="uq_billing_appointment"
    ),
)
    id = Column(Integer, primary_key=True, index=True)

    patient_id = Column(
        Integer,
        ForeignKey("patients.id"),
        nullable=False,
        index=True
    )

    doctor_id = Column(
        Integer,
        ForeignKey("doctors.id"),
        nullable=False,
        index=True
    )

    appointment_id = Column(
        Integer,
        ForeignKey("appointments.id"),
        nullable=True,
        index=True
    )

    consultation_fee = Column(Numeric(10, 2), nullable=False)
    additional_charges = Column(Numeric(10, 2), nullable=False, default=0)
    total_amount = Column(Numeric(10, 2), nullable=False)

    payment_status = Column(
        String,
        nullable=False,
        default="pending"
    )

    payment_mode = Column(
        String,
        nullable=True
    )

    is_active = Column(Boolean, nullable=False, default=True)

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

    patient = relationship("Patient")
    doctor = relationship("Doctor")
    appointment = relationship("Appointment")