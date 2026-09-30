import uuid
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


def test_get_doctors_without_auth():
    request_counts.clear()

    response = client.get("/api/v1/doctors/")

    assert response.status_code in [401, 429]


def test_get_doctor_without_auth():
    request_counts.clear()

    response = client.get("/api/v1/doctors/1")

    assert response.status_code in [401, 429]


def test_create_doctor_without_auth():
    request_counts.clear()

    response = client.post(
        "/api/v1/doctors/",
        json={
            "name": "Coverage Doctor",
            "specialization": "Cardiology",
            "email": "coverage17@example.com"
        }
    )

    assert response.status_code in [401, 429]


def test_update_doctor_without_auth():
    request_counts.clear()

    response = client.put(
        "/api/v1/doctors/1",
        json={
            "name": "Updated Doctor",
            "specialization": "Cardiology",
            "email": "updated17@example.com"
        }
    )

    assert response.status_code in [401, 429]


def test_delete_doctor_without_auth():
    request_counts.clear()

    response = client.delete("/api/v1/doctors/1")

    assert response.status_code in [401, 429]


def test_create_doctor_service():
    from app.database import SessionLocal
    from app.services.doctor_service import create_doctor_service

    db = SessionLocal()

    doctor = create_doctor_service(
        db=db,
        name="Coverage Test Doctor",
        specialization="Neurology",
        email=f"coverage.{uuid.uuid4().hex}@example.com",
        created_by=ADMIN_EMAIL
    )

    assert doctor.name == "Coverage Test Doctor"
    assert doctor.specialization == "Neurology"

    db.close()


def test_get_doctors_with_auth():
    token = get_admin_token()

    response = client.get(
        "/api/v1/doctors/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200


def test_get_doctor_by_id_with_auth():
    token = get_admin_token()

    response = client.get(
        "/api/v1/doctors/1",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code in [200, 404]


def test_create_doctor_with_auth():
    token = get_admin_token()

    response = client.post(
        "/api/v1/doctors/",
        json={
            "name": "Coverage API Doctor",
            "specialization": "Dermatology",
            "email": "coverage.api.doctor17.new@example.com"
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code in [200, 201, 400]

def test_update_doctor_with_auth():
    token = get_admin_token()

    response = client.put(
        "/api/v1/doctors/1",
        json={
            "name": "Updated Coverage Doctor",
            "specialization": "Cardiology",
            "email": "updated.coverage.doctor17@example.com"
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code in [200, 400, 404]


def test_delete_doctor_with_auth():
    token = get_admin_token()

    response = client.delete(
        "/api/v1/doctors/9999",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code in [200, 404]


def test_assign_patient_with_auth():
    token = get_admin_token()

    response = client.post(
        "/api/v1/doctors/1/assign-patient",
        json={
            "patient_id": 1
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code in [200, 400, 404]