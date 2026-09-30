from fastapi.testclient import TestClient

from app.main import app, request_counts

client = TestClient(app)

ADMIN_EMAIL = "coverage_admin17@example.com"
ADMIN_PASSWORD = "Admin@123"


def get_admin_token():
    request_counts.clear()

    register = client.post(
        "/api/v1/auth/register",
        json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD,
            "role": "admin"
        }
    )

    request_counts.clear()

    login = client.post(
        "/api/v1/auth/login",
        data={
            "username": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
    )

    assert login.status_code == 200
    return login.json()["access_token"]


def test_get_patients_without_auth():
    request_counts.clear()

    response = client.get("/api/v1/patients/")

    assert response.status_code in [401, 429]


def test_create_patient_without_auth():
    request_counts.clear()

    response = client.post(
        "/api/v1/patients/",
        json={
            "name": "Test Patient",
            "age": 30,
            "phone": "9876543210",
            "doctor_id": 1
        }
    )

    assert response.status_code in [401, 429]


def test_create_patient_service():
    from app.database import SessionLocal
    from app.services.patient_service import create_patient_service

    db = SessionLocal()

    patient = create_patient_service(
        db=db,
        name="Coverage Test Patient",
        age=30,
        phone="9123456789",
        doctor_id=1,
        created_by=ADMIN_EMAIL
    )

    assert patient.name == "Coverage Test Patient"
    assert patient.age == 30
    assert patient.doctor_id == 1

    db.close()


def test_get_patients_with_auth():
    token = get_admin_token()

    response = client.get(
        "/api/v1/patients/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200


def test_create_patient_with_auth():
    token = get_admin_token()

    response = client.post(
        "/api/v1/patients/",
        json={
            "name": "Coverage API Patient",
            "age": 32,
            "phone": "9012345678",
            "doctor_id": 1
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code in [200, 201, 400]


def test_get_patient_by_id_with_auth():
    token = get_admin_token()

    response = client.get(
        "/api/v1/patients/1",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code in [200, 404]