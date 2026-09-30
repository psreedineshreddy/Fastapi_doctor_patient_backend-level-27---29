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


def test_get_appointments_without_auth():
    request_counts.clear()

    response = client.get("/appointments/")

    assert response.status_code in [401, 429]


def test_get_appointment_by_id_without_auth():
    request_counts.clear()

    response = client.get("/appointments/1")

    assert response.status_code in [401, 429]


def test_get_doctor_appointments_without_auth():
    request_counts.clear()

    response = client.get("/doctors/1/appointments")

    assert response.status_code in [401, 404, 429]


def test_get_patient_appointments_without_auth():
    request_counts.clear()

    response = client.get("/patients/1/appointments")

    assert response.status_code in [401, 404, 429]


def test_get_appointments_with_auth():
    token = get_admin_token()

    response = client.get(
        "/appointments/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200


def test_get_appointment_by_id_with_auth():
    token = get_admin_token()

    response = client.get(
        "/appointments/1",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code in [200, 404]


def test_get_doctor_appointments_with_auth():
    token = get_admin_token()

    response = client.get(
        "/doctors/1/appointments",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code in [200, 404]


def test_get_patient_appointments_with_auth():
    token = get_admin_token()

    response = client.get(
        "/patients/1/appointments",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code in [200, 404]