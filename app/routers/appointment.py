import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.schemas.appointment import AppointmentCreate, AppointmentResponse


router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.post("/", response_model=AppointmentResponse)
def create_appointment(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    doctor = db.query(Doctor).filter(
        Doctor.id == appointment.doctor_id
    ).first()

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    if not doctor.is_active:
        raise HTTPException(
            status_code=400,
            detail="Cannot book appointment with inactive doctor"
        )

    patient = db.query(Patient).filter(
        Patient.id == appointment.patient_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    if patient.doctor_id != doctor.id:
        raise HTTPException(
            status_code=400,
            detail="Patient is not assigned to this doctor"
        )

    overlapping = db.query(Appointment).filter(
        Appointment.doctor_id == appointment.doctor_id,
        Appointment.appointment_date == appointment.appointment_date,
        Appointment.status == "scheduled"
    ).first()

    if overlapping:
        raise HTTPException(
            status_code=400,
            detail="Doctor already has an appointment at this time"
        )

    new_appointment = Appointment(
    doctor_id=appointment.doctor_id,
    patient_id=appointment.patient_id,
    appointment_date=appointment.appointment_date,
    status=appointment.status,
    created_by=current_user["email"],
    updated_by=current_user["email"]
)

    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)

    return new_appointment


@router.get("/", response_model=list[AppointmentResponse])
def get_appointments(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    start_time = time.time()

    appointments = db.query(Appointment).all()

    response_time = time.time() - start_time
    print(f"Appointments list response time: {response_time:.4f} seconds")

    return appointments


@router.get("/doctors/{doctor_id}", response_model=list[AppointmentResponse])
def get_doctor_appointments(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    return db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id
    ).all()

@router.get("/patients/{patient_id}", response_model=list[AppointmentResponse])
def get_patient_appointments(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return db.query(Appointment).filter(
        Appointment.patient_id == patient_id
    ).all()


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()

    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    return appointment


@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: int,
    appointment: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    existing_appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()

    if not existing_appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    doctor = db.query(Doctor).filter(
        Doctor.id == appointment.doctor_id
    ).first()

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    if not doctor.is_active:
        raise HTTPException(
            status_code=400,
            detail="Cannot book appointment with inactive doctor"
        )

    patient = db.query(Patient).filter(
        Patient.id == appointment.patient_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    if patient.doctor_id != doctor.id:
        raise HTTPException(
            status_code=400,
            detail="Patient is not assigned to this doctor"
        )

    overlapping = db.query(Appointment).filter(
        Appointment.doctor_id == appointment.doctor_id,
        Appointment.appointment_date == appointment.appointment_date,
        Appointment.status == "scheduled",
        Appointment.id != appointment_id
    ).first()

    if overlapping:
        raise HTTPException(
            status_code=400,
            detail="Doctor already has an appointment at this time"
        )

    existing_appointment.doctor_id = appointment.doctor_id
    existing_appointment.patient_id = appointment.patient_id
    existing_appointment.appointment_date = appointment.appointment_date
    existing_appointment.status = appointment.status
    existing_appointment.updated_by = current_user["email"]

    db.commit()
    db.refresh(existing_appointment)

    return existing_appointment


@router.delete("/{appointment_id}")
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()

    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    db.delete(appointment)
    db.commit()

    return {
        "message": "Appointment deleted successfully"
    }

