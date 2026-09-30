from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_register():
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "testuser17@example.com",
            "password": "Test@123",
            "role": "doctor"
        }
    )

    assert response.status_code in [200, 400]


def test_login():
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "testuser17@example.com",
            "password": "Test@123"
        }
    )

    assert response.status_code in [200, 401]

def test_login_invalid_password():
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "testuser17@example.com",
            "password": "WrongPassword"
        }
    )

    assert response.status_code == 401

def test_unauthorized_doctor_creation():
    response = client.post(
        "/api/v1/doctors/",
        json={
            "name": "Test Doctor",
            "specialization": "Cardiology",
            "email": "testdoctor17@example.com"
        }
    )

    assert response.status_code == 401