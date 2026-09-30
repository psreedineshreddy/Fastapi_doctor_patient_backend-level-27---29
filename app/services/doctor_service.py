from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.doctor import Doctor


def create_doctor_service(
    db: Session,
    name: str,
    specialization: str,
    email: str,
    created_by: str
):
    existing_doctor = db.query(Doctor).filter(
        Doctor.email == email
    ).first()

    if existing_doctor:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_doctor = Doctor(
        name=name,
        specialization=specialization,
        email=email,
        created_by=created_by,
        updated_by=created_by
    )

    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)

    return new_doctor