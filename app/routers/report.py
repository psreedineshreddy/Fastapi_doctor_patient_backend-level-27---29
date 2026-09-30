from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.billing import Billing


router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


@router.get("/revenue")
def get_revenue_report(
    doctor_id: int | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    base_query = db.query(Billing).filter(
        Billing.is_active == True,
        Billing.payment_status == "paid"
    )

    if doctor_id:
        base_query = base_query.filter(
            Billing.doctor_id == doctor_id
        )

    if from_date:
        base_query = base_query.filter(
            Billing.created_at >= from_date
        )

    if to_date:
        base_query = base_query.filter(
            Billing.created_at <= to_date
        )

    total_revenue = base_query.with_entities(
        func.sum(Billing.total_amount)
    ).scalar() or 0

    doctor_results = base_query.with_entities(
        Billing.doctor_id,
        func.sum(Billing.total_amount).label("revenue")
    ).group_by(
        Billing.doctor_id
    ).all()

    day_results = base_query.with_entities(
        func.date(Billing.created_at).label("date"),
        func.sum(Billing.total_amount).label("revenue")
    ).group_by(
        func.date(Billing.created_at)
    ).order_by(
        func.date(Billing.created_at)
    ).all()

    return {
        "total_revenue": total_revenue,
        "revenue_per_doctor": [
            {
                "doctor_id": row.doctor_id,
                "revenue": row.revenue
            }
            for row in doctor_results
        ],
        "revenue_per_day": [
            {
                "date": row.date,
                "revenue": row.revenue
            }
            for row in day_results
        ]
    }