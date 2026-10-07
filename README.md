# Bulk Certificate Generator

A Django REST API for generating certificates in bulk using background processing with Celery and Redis.

## Tech Stack

- Python
- Django
- Django REST Framework
- Celery
- Redis
- SQLite
- ReportLab

## Features

- Bulk certificate generation
- Recipient data validation
- Background certificate processing
- Job status and progress tracking
- Individual certificate status tracking
- Individual failure handling
- PDF certificate generation
- Certificate retrieval
- Certificate download API
- Automated tests

## Project Structure

```text
Bulk Certificate Generator/
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   ├── wsgi.py
│   └── celery.py
├── certificates/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── tasks.py
│   ├── services.py
│   └── tests.py
├── manage.py
├── db.sqlite3
├── requirements.txt
├── README.md
└── .gitignore
```

## Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd "Bulk Certificate Generator"
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate Virtual Environment

For WSL/Linux:

```bash
source .venv/bin/activate
```

For Windows:

```bash
.venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run Database Migrations

```bash
python manage.py migrate
```

### 6. Start Redis

For WSL/Linux:

```bash
sudo service redis-server start
```

Check whether Redis is running:

```bash
redis-cli ping
```

Expected output:

```text
PONG
```

### 7. Start Celery Worker

Open a new terminal and activate the virtual environment:

```bash
source .venv/bin/activate
```

Start the Celery worker:

```bash
celery -A config worker --loglevel=info
```

Keep the Celery worker running.

### 8. Start Django Server

Open another terminal and activate the virtual environment:

```bash
source .venv/bin/activate
```

Start the Django development server:

```bash
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

## API Endpoints

### 1. Create Generation Job

```http
POST /api/jobs/
```

Request body:

```json
{
    "recipients": [
        {
            "name": "Rahul Kumar",
            "email": "rahul@gmail.com",
            "course": "Python Backend Development"
        },
        {
            "name": "Amit Sharma",
            "email": "amit@gmail.com",
            "course": "Python Backend Development"
        }
    ]
}
```

Example response:

```json
{
    "job_id": 1,
    "status": "PENDING",
    "total_count": 2
}
```

After the request is created, each certificate is queued as a separate Celery task.

### 2. Get Job Status

```http
GET /api/jobs/<job_id>/
```

Example:

```http
GET /api/jobs/1/
```

Example response:

```json
{
    "job_id": 1,
    "status": "COMPLETED",
    "total_count": 2,
    "success_count": 2,
    "failed_count": 0,
    "pending_count": 0
}
```

### 3. Get Job Certificates

```http
GET /api/jobs/<job_id>/certificates/
```

Example:

```http
GET /api/jobs/1/certificates/
```

Returns all certificates belonging to the specified job.

Example response:

```json
{
    "job_id": 1,
    "certificates": [
        {
            "id": 1,
            "recipient_name": "Rahul Kumar",
            "recipient_email": "rahul@gmail.com",
            "course_name": "Python Backend Development",
            "certificate_number": "CERT-00001-00001",
            "status": "COMPLETED",
            "download_url": "/api/certificates/1/download/",
            "error_message": null
        }
    ]
}
```

### 4. Download Certificate

```http
GET /api/certificates/<certificate_id>/download/
```

Example:

```http
GET /api/certificates/1/download/
```

If the certificate has been generated successfully, the API returns the PDF file.

If the certificate is still processing, the API returns an appropriate error response.

## Background Processing

Celery is used to process certificate generation in the background.

When a generation job is created:

1. The generation job is created in the database.
2. Certificate records are created for each recipient.
3. Each certificate is submitted as an individual Celery task.
4. Celery processes the certificate generation in the background.
5. The certificate status is updated after processing.
6. The overall job status and progress are updated.

Redis is used as the message broker for Celery.

## Job Statuses

The generation job can have the following statuses:

```text
PENDING
PROCESSING
COMPLETED
PARTIALLY_COMPLETED
FAILED
```

### PENDING

The job has been created and certificate processing is waiting to start.

### PROCESSING

One or more certificates are currently being processed.

### COMPLETED

All certificates in the job have been generated successfully.

### PARTIALLY_COMPLETED

Some certificates were generated successfully while one or more certificates failed.

### FAILED

All certificates in the job failed to generate.

## Certificate Statuses

Each certificate can have the following statuses:

```text
PENDING
PROCESSING
COMPLETED
FAILED
```

### PENDING

The certificate has been created but processing has not started.

### PROCESSING

The certificate is currently being generated.

### COMPLETED

The certificate PDF was generated successfully.

### FAILED

Certificate generation failed and the error message is stored.

## Failure Handling

Each certificate is processed independently.

If one certificate fails:

1. The certificate is marked as `FAILED`.
2. The error message is stored.
3. Other certificates continue processing.
4. The overall job can become `PARTIALLY_COMPLETED`.

This ensures that failure of one certificate does not stop the entire bulk generation process.

## Certificate Generation

Certificates are generated as PDF files using ReportLab.

Each certificate contains:

- Certificate title
- Recipient name
- Course name
- Certificate number

Generated certificates can be downloaded using the certificate download endpoint.

## Database

SQLite is used as the relational database.

### GenerationJob

Stores information about the bulk certificate generation job.

Main fields:

- `status`
- `total_count`
- `success_count`
- `failed_count`
- `created_at`
- `completed_at`

### Certificate

Stores information about each generated certificate.

Main fields:

- `recipient_name`
- `recipient_email`
- `course_name`
- `certificate_number`
- `status`
- `file`
- `error_message`
- `job`

## Testing

Run the complete test suite:

```bash
python manage.py test
```

The tests cover:

- Generation job creation
- Recipient data validation
- Job status
- Job progress
- Individual certificate failure handling
- Certificate generation
- Certificate retrieval

## Development Commands

Check the Django project:

```bash
python manage.py check
```

Create migrations:

```bash
python manage.py makemigrations
```

Apply migrations:

```bash
python manage.py migrate
```

Run tests:

```bash
python manage.py test
```

Start Django server:

```bash
python manage.py runserver
```

Start Celery worker:

```bash
celery -A config worker --loglevel=info
```

## Design Decisions

### Django REST Framework

Django REST Framework is used to build the REST API and validate recipient data.

### Celery

Celery is used for background certificate generation so that the API does not wait for every certificate to be generated.

### Redis

Redis is used as the message broker for Celery.

### SQLite

SQLite is used as the relational database for this assignment.

### ReportLab

ReportLab is used to generate PDF certificates.

### Individual Certificate Tasks

Each certificate is processed as a separate Celery task. If one certificate fails, the remaining certificates continue processing independently.

## Requirements

Install all dependencies using:

```bash
pip install -r requirements.txt
```

## Complete Run Flow

The application requires Redis, Celery, and Django to be running.

### Terminal 1 - Redis

```bash
sudo service redis-server start
```

### Terminal 2 - Celery

```bash
source .venv/bin/activate
celery -A config worker --loglevel=info
```

### Terminal 3 - Django

```bash
source .venv/bin/activate
python manage.py runserver
```

The API is available at:

```text
http://127.0.0.1:8000/
```

## License

This project was developed as a backend assignment for bulk certificate generation.