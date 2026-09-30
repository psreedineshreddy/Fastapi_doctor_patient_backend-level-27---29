from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.billing import Billing
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.schemas.billing import BillingCreate, BillingResponse, BillingUpdate
from app.auth.dependencies import get_current_user


router = APIRouter(
    prefix="/billings",
    tags=["Billing"]
)


@router.post("/", response_model=BillingResponse, status_code=201)
def create_billing(
    billing: BillingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    
    if current_user["role"].lower() != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    
    patient = db.query(Patient).filter(
        Patient.id == billing.patient_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    
    doctor = db.query(Doctor).filter(
        Doctor.id == billing.doctor_id
    ).first()

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    if not doctor.is_active:
        raise HTTPException(
            status_code=400,
            detail="Cannot create billing for an inactive doctor"
        )

    if billing.appointment_id is not None:
        appointment = db.query(Appointment).filter(
            Appointment.id == billing.appointment_id
        ).first()

        if not appointment:
            raise HTTPException(
                status_code=404,
                detail="Appointment not found"
            )

        if appointment.doctor_id != billing.doctor_id:
            raise HTTPException(
                status_code=400,
                detail="Appointment does not belong to this doctor"
            )

        if appointment.patient_id != billing.patient_id:
            raise HTTPException(
                status_code=400,
                detail="Appointment does not belong to this patient"
            )

        if appointment.status.lower() == "cancelled":
            raise HTTPException(
                status_code=400,
                detail="Cannot create billing for a cancelled appointment"
            )

        existing_billing = db.query(Billing).filter(
            Billing.appointment_id == billing.appointment_id,
            Billing.is_active == True
        ).first()

        if existing_billing:
            raise HTTPException(
                status_code=400,
                detail="Billing already exists for this appointment"
            )

    
    total_amount = (
        billing.consultation_fee +
        billing.additional_charges
    )

    try:
        new_billing = Billing(
            patient_id=billing.patient_id,
            doctor_id=billing.doctor_id,
            appointment_id=billing.appointment_id,
            consultation_fee=billing.consultation_fee,
            additional_charges=billing.additional_charges,
            total_amount=total_amount,
            payment_status=billing.payment_status,
            payment_mode=billing.payment_mode,
            is_active=True
        )

        db.add(new_billing)

    
        if billing.appointment_id is not None:
            appointment.status = "completed"

        db.commit()
        db.refresh(new_billing)

        return new_billing

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Billing transaction failed"
        )

@router.get("/", response_model=list[BillingResponse])
def get_billings(
    payment_status: str | None = None,
    doctor_id: int | None = None,
    patient_id: int | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if page < 1:
        raise HTTPException(
            status_code=400,
            detail="Page must be greater than 0"
        )

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 100"
        )

    query = db.query(Billing).filter(
        Billing.is_active == True
    )

    if payment_status:
        query = query.filter(
            Billing.payment_status == payment_status
        )

    if doctor_id:
        query = query.filter(
            Billing.doctor_id == doctor_id
        )

    if patient_id:
        query = query.filter(
            Billing.patient_id == patient_id
        )

    if from_date:
        query = query.filter(
            Billing.created_at >= from_date
        )

    if to_date:
        query = query.filter(
            Billing.created_at <= to_date
        )

    offset = (page - 1) * limit

    return query.offset(offset).limit(limit).all()

@router.get("/{billing_id}", response_model=BillingResponse)
def get_billing(
    billing_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    billing = db.query(Billing).filter(
        Billing.id == billing_id,
        Billing.is_active == True
    ).first()

    if not billing:
        raise HTTPException(
            status_code=404,
            detail="Billing not found"
        )

    return billing

@router.get("/patients/{patient_id}", response_model=list[BillingResponse])
def get_patient_billings(
    patient_id: int,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if page < 1:
        raise HTTPException(
            status_code=400,
            detail="Page must be greater than 0"
        )

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 100"
        )

    billings = (
        db.query(Billing)
        .filter(
            Billing.patient_id == patient_id,
            Billing.is_active == True
        )
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return billings

@router.get("/doctors/{doctor_id}", response_model=list[BillingResponse])
def get_doctor_billings(
    doctor_id: int,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if page < 1:
        raise HTTPException(
            status_code=400,
            detail="Page must be greater than 0"
        )

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 100"
        )

    billings = (
        db.query(Billing)
        .filter(
            Billing.doctor_id == doctor_id,
            Billing.is_active == True
        )
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return billings

@router.put("/{billing_id}", response_model=BillingResponse)
def update_billing(
    billing_id: int,
    billing_data: BillingUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user["role"].lower() != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    billing = db.query(Billing).filter(
        Billing.id == billing_id,
        Billing.is_active == True
    ).first()

    if not billing:
        raise HTTPException(
            status_code=404,
            detail="Billing not found"
        )

    if billing_data.consultation_fee is not None:
        billing.consultation_fee = billing_data.consultation_fee

    if billing_data.additional_charges is not None:
        billing.additional_charges = billing_data.additional_charges

    if billing_data.payment_status is not None:
        billing.payment_status = billing_data.payment_status

    if billing_data.payment_mode is not None:
        billing.payment_mode = billing_data.payment_mode

    billing.total_amount = (
        billing.consultation_fee +
        billing.additional_charges
    )

    db.commit()
    db.refresh(billing)

    return billing

@router.patch("/{billing_id}", response_model=BillingResponse)
def patch_billing(
    billing_id: int,
    billing_data: BillingUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user["role"].lower() != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    billing = db.query(Billing).filter(
        Billing.id == billing_id,
        Billing.is_active == True
    ).first()

    if not billing:
        raise HTTPException(
            status_code=404,
            detail="Billing not found"
        )

    if billing_data.consultation_fee is not None:
        billing.consultation_fee = billing_data.consultation_fee

    if billing_data.additional_charges is not None:
        billing.additional_charges = billing_data.additional_charges

    if billing_data.payment_status is not None:
        billing.payment_status = billing_data.payment_status

    if billing_data.payment_mode is not None:
        billing.payment_mode = billing_data.payment_mode

    billing.total_amount = (
        billing.consultation_fee +
        billing.additional_charges
    )

    db.commit()
    db.refresh(billing)

    return billing

@router.delete("/{billing_id}")
def delete_billing(
    billing_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user["role"].lower() != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    billing = db.query(Billing).filter(
        Billing.id == billing_id,
        Billing.is_active == True
    ).first()

    if not billing:
        raise HTTPException(
            status_code=404,
            detail="Billing not found"
        )

    billing.is_active = False

    db.commit()

    return {
        "message": "Billing deleted successfully"
    }