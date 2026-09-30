import logging

from time import time
from fastapi import FastAPI, Depends, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import Base, engine
from app.models import User, Doctor, Patient
from app.models.appointment import Appointment
from app.routers import auth, doctor, patient, billing, report
from app.routers.appointment import router as appointment_router
from app.auth.dependencies import get_current_user


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DOCTOR–PATIENT MANAGEMENT API",
    description="A FastAPI backend for managing doctors, patients, appointments, and secure user access.",
    version="1.0.0"
)

request_counts = {}

RATE_LIMIT = 10
RATE_WINDOW = 60

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = time()

    if client_ip not in request_counts:
        request_counts[client_ip] = []

    request_counts[client_ip] = [
        request_time
        for request_time in request_counts[client_ip]
        if current_time - request_time < RATE_WINDOW
    ]

    if len(request_counts[client_ip]) >= RATE_LIMIT:
        return JSONResponse(
            status_code=429,
            content={
                "error": "Too Many Requests",
                "message": "Rate limit exceeded. Try again later."
            }
        )

    request_counts[client_ip].append(current_time)

    return await call_next(request)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}")

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred"
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "message": "Invalid request data",
            "details": exc.errors()
        }
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("Doctor Patient Backend API started")

app.include_router(auth.router, prefix="/api/v1")
app.include_router(doctor.router, prefix="/api/v1")
app.include_router(patient.router, prefix="/api/v1")
app.include_router(appointment_router, prefix="/api/v1")
app.include_router(billing.router, prefix="/api/v1")
app.include_router(report.router, prefix="/api/v1")


@app.get("/")
def root(current_user=Depends(get_current_user)):
    return {"message": "Doctor Patient Backend API"}