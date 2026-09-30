from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.services.doctor_service import create_doctor_service
from app.schemas.patient import PatientResponse
from app.schemas.doctor import DoctorCreate, DoctorUpdate, DoctorResponse, DoctorListResponse
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.post("/", response_model=DoctorResponse)
def create_doctor(
    doctor: DoctorCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    return create_doctor_service(
    db,
    doctor.name,
    doctor.specialization,
    doctor.email,
    current_user["email"]
)

@router.get("/", response_model=DoctorListResponse)
def get_doctors(
    specialization: str | None = None,
    is_active: bool | None = None,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    query = db.query(Doctor)

    if specialization:
        query = query.filter(Doctor.specialization == specialization)

    if is_active is not None:
        query = query.filter(Doctor.is_active == is_active)

    total = query.count()

    doctors = query.offset((page - 1) * limit).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": doctors
    }

@router.get("/{doctor_id}", response_model=DoctorResponse)
def get_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    return doctor

@router.put("/{doctor_id}", response_model=DoctorResponse)
def update_doctor(
    doctor_id: int,
    doctor: DoctorUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    existing_doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()

    if not existing_doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    existing_doctor.name = doctor.name
    existing_doctor.specialization = doctor.specialization
    existing_doctor.email = doctor.email
    existing_doctor.updated_by = current_user["email"]

    db.commit()
    db.refresh(existing_doctor)

    return existing_doctor

@router.delete("/{doctor_id}", response_model=DoctorResponse)
def delete_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    doctor.is_active = False

    db.commit()
    db.refresh(doctor)

    return doctor

@router.post("/{doctor_id}/patients/{patient_id}")
def assign_patient(
    doctor_id: int,
    patient_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()

    patient = db.query(Patient).filter(
        Patient.id == patient_id
    ).first()

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    if not doctor.is_active:
        raise HTTPException(
            status_code=400,
            detail="Cannot assign patient to an inactive doctor"
        )

    patient.doctor_id = doctor.id

    db.commit()

    return {"message": "Patient assigned successfully"}

@router.get("/{doctor_id}/patients", response_model=list[PatientResponse])
def get_doctor_patients(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    if current_user["role"] == "doctor":
        current_user_doctor = db.query(Doctor).filter(
            Doctor.email == current_user["email"]
        ).first()

        if not current_user_doctor or current_user_doctor.id != doctor_id:
            raise HTTPException(status_code=403, detail="Access denied")

    return sorted(doctor.patients, key=lambda patient: patient.id)