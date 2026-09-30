from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.services.patient_service import create_patient_service
from app.schemas.patient import PatientCreate, PatientResponse, PatientListResponse
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.post("/", response_model=PatientResponse)
def create_patient(
    patient: PatientCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    return create_patient_service(
    db,
    patient.name,
    patient.age,
    patient.phone,
    patient.doctor_id,
    current_user["email"]
)

@router.get("/", response_model=PatientListResponse)
def get_patients(
    age_gt: int | None = None,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    query = db.query(Patient)

    if age_gt is not None:
        query = query.filter(Patient.age > age_gt)

    total = query.count()

    patients = query.offset((page - 1) * limit).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": patients
    }

@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    if current_user["role"] == "doctor":
        current_user_doctor = db.query(Doctor).filter(
            Doctor.email == current_user["email"]
        ).first()

        if not current_user_doctor or patient not in current_user_doctor.patients:
            raise HTTPException(status_code=403, detail="Access denied")

    return patient

@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: int,
    patient: PatientCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    existing_patient = db.query(Patient).filter(
        Patient.id == patient_id
    ).first()

    if not existing_patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    doctor = db.query(Doctor).filter(
        Doctor.id == patient.doctor_id
    ).first()

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    if not doctor.is_active:
        raise HTTPException(
            status_code=400,
            detail="Cannot assign patient to an inactive doctor"
        )

    existing_patient.name = patient.name
    existing_patient.age = patient.age
    existing_patient.phone = patient.phone
    existing_patient.doctor_id = patient.doctor_id
    existing_patient.updated_by = current_user["email"]

    db.commit()    
    db.refresh(existing_patient)

    return existing_patient

@router.delete("/{patient_id}")
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    patient = db.query(Patient).filter(
        Patient.id == patient_id
    ).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    db.delete(patient)
    db.commit()

    return {"message": "Patient deleted successfully"}