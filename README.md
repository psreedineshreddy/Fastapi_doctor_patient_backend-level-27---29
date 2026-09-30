# FastAPI Doctor Patient Backend

A FastAPI backend application for managing doctors, patients, appointments, authentication, and authorization.

## 1. Setup Instructions

### Requirements

* Python 3.9+
* FastAPI
* Uvicorn
* SQLAlchemy
* SQLite

### Installation

Create and activate a virtual environment:

```text
python3 -m venv venv
source venv/bin/activate
```

Install the required packages:

```text
pip install -r requirements.txt
```

Start the application:

```text
uvicorn app.main:app --reload
```

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## 2. Environment Configuration

Create a `.env` file in the project root:

```env
SECRET_KEY=doctor_patient_backend_secret_2026
```

The `SECRET_KEY` is used for JWT authentication.

The `.env` file is excluded from Git using `.gitignore`.

## 3. Authentication and Authorization

The application uses JWT-based authentication.

* Users can register and login.
* Successful login returns a JWT access token.
* Protected APIs require authentication.
* Admin users can manage doctors, patients, and appointments.
* Doctors can view only their assigned patients.
* Unauthorized operations return `403 Forbidden`.

## 4. Doctor Management

* Create, view, update, and soft delete doctors.
* Assign patients to doctors.
* Doctor email addresses must be unique.
* Only active doctors can receive appointments.

## 5. Patient Management

* Create and view patients.
* View patient details.
* Assign patients to doctors.
* Doctors can view only their assigned patients.
* Patient age and phone number are validated.

## 6. Appointment Management

* Create, view, update, and delete appointments.
* View appointments by doctor or patient.
* Validate doctor and patient existence.
* Prevent appointments for inactive doctors.
* Prevent overlapping appointments for the same doctor.

Appointment statuses:

* `scheduled`
* `completed`
* `cancelled`

## 7. Data Integrity

* Unique doctor email constraint.
* Foreign key relationships.
* Request validation before database operations.
* Meaningful error responses.
* Graceful database exception handling.

## 8. Performance

* Database indexes for frequently queried fields.
* Pagination for list APIs.
* Response-time measurement for list APIs.
* Optimized database queries.

## 9. Audit and Tracking

The application tracks:

* `created_at`
* `updated_at`
* `created_by`
* `updated_by`

Timestamps and user information are automatically recorded during create and update operations.

## 10. API Hardening and Reliability

* Global exception handling.
* Custom error responses.
* Uniform validation errors.
* Basic rate limiting.
* JWT authentication.
* Role-based authorization.

## 11. Testing and coverage

Automated tests cover:

* Authentication
* Doctor APIs
* Patient APIs
* Appointment APIs
* Validation
* Authorization

Run the tests:

```text
python -m pytest --cov=app
```

Current test coverage: **71%**

## 12. Swagger Documentation

Swagger UI provides documentation for the available APIs, including request examples, response schemas, authentication, and authorization.

Swagger URL:

```text
http://127.0.0.1:8000/docs
```


