from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.models.doctor import Doctor


def create_patient_service(
    db: Session,
    name: str,
    age: int,
    phone: str,
    doctor_id: int,
    created_by: str
):
    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    if not doctor.is_active:
        raise HTTPException(
            status_code=400,
            detail="Cannot assign patient to an inactive doctor"
        )

    new_patient = Patient(
        name=name,
        age=age,
        phone=phone,
        doctor_id=doctor_id,
        created_by=created_by,
        updated_by=created_by
    )

    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    return new_patient