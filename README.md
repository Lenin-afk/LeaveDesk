LeaveDesk API

A leave and work-from-home (WFH) management REST API built using Python, FastAPI, SQLAlchemy, and PostgreSQL.

Features

Authentication

- User login with email and password
- Password hashing using bcrypt
- JWT-based authentication
- Role-based access control for employees and managers
- Token expiration

Employee

- Submit leave requests
- Submit WFH requests
- View personal leave and WFH history
- Filter requests by status and date
- Cancel pending requests
- Leave duration validation (full day, half day, and hourly)
- WFH limit of two working days
- Conflict checks for overlapping leave and WFH requests

Manager

- View requests from direct reports
- Filter requests by status, employee, and date
- Approve or reject leave requests
- Approve or reject WFH requests
- Record decision details, including manager ID, decision timestamp, and rejection comments

Tech Stack

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- JWT
- Passlib / bcrypt
- Uvicorn

Project Structure

leavedesk/
├── app/
│   ├── routers/
│   │   ├── auth.py
│   │   ├── leave.py
│   │   ├── wfh.py
│   │   └── manager.py
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── security.py
│   └── seed.py
├── .env
├── .gitignore
└── README.md

Setup and Installation

1. Clone the repository

git clone YOUR_GITHUB_REPOSITORY_URL
cd leavedesk

2. Create a virtual environment

python -m venv .venv

Activate it on Windows:

.venv\Scripts\Activate.ps1

3. Install dependencies

pip install fastapi uvicorn sqlalchemy "psycopg[binary]" python-dotenv "passlib[bcrypt]" "python-jose[cryptography]"

4. Configure environment variables

Create a ".env" file in the project root:

DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/leavedesk
SECRET_KEY=YOUR_SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES=60

Create a PostgreSQL database named "leavedesk" before starting the application.

5. Seed the database

python -m app.seed

6. Start the application

uvicorn app.main:app --reload

The API will be available at:

"http://127.0.0.1:8000"

Interactive API documentation:

"http://127.0.0.1:8000/docs"

Test Credentials

Role| Email| Password
Manager| priya.manager@leavedesk.test| Manager@123
Employee| arjun@leavedesk.test| Employee@123
Employee| meera@leavedesk.test| Employee@123

These are development seed credentials only.

API Endpoints

Method| Endpoint| Description
POST| "/auth/login"| User login
GET| "/auth/me"| Get current user
POST| "/leaves"| Create leave request
GET| "/leaves/me"| View personal leave requests
POST| "/leaves/{id}/cancel"| Cancel pending leave
POST| "/wfh"| Create WFH request
GET| "/wfh/me"| View personal WFH requests
POST| "/wfh/{id}/cancel"| Cancel pending WFH
GET| "/manager/requests"| View direct reports' requests
POST| "/manager/leaves/{id}/approve"| Approve leave
POST| "/manager/leaves/{id}/reject"| Reject leave
POST| "/manager/wfh/{id}/approve"| Approve WFH
POST| "/manager/wfh/{id}/reject"| Reject WFH

Notes

- Authentication is required for employee and manager endpoints.
- Manager endpoints are restricted to users with the manager role.
- Managers can only access requests belonging to their direct reports.
- Requests can only be cancelled while pending.
- Approval and rejection actions are recorded in the database.
- The health-check endpoint and CSV reporting section are not included in this implementation.
