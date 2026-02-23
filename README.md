# MediCore HMS

Flask + MySQL based Hospital Management System aligned with the provided PRD/TODO/UI docs.

## Stack

- Backend: Flask, Jinja2, mysql-connector-python
- Frontend: HTML, CSS, Vanilla JS
- Database: MySQL (XAMPP/phpMyAdmin)
- PDF: WeasyPrint (HTML fallback if native dependency is missing)

## Features Implemented

- Role-based auth for `admin`, `doctor`, `patient`
- Admin portal: dashboard, patients, doctors, departments, appointments, rooms/admissions, pharmacy, billing, feedback
- Doctor portal: dashboard, own appointments, own patients, prescription entry
- Patient portal: dashboard, own appointments, prescriptions, bills, profile, feedback
- Appointment booking wizard with live slot lookup
- Soft-delete for patients/doctors/medicines
- Bill generation + mark paid + invoice download

## Project Structure

```text
app.py
routes/
templates/
static/
db/schema.sql
db/seed.sql
```

## Local Setup (Windows + XAMPP)

1. Start XAMPP and run `Apache` + `MySQL`.
2. Create virtual environment and install dependencies:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Create `.env` from `.env.example`:
   ```powershell
   Copy-Item .env.example .env
   ```
4. Import SQL:
   - Open `http://localhost/phpmyadmin`
   - Import `db/schema.sql`
   - Import `db/seed.sql`
5. Run app:
   ```powershell
   python app.py
   ```
6. Open `http://127.0.0.1:5000`

## Default Accounts

- Admin: `admin@medicore.com` / `admin123`
- Doctor: `arjun.mehta@medicore.com` / `doctor123`
- Patient: `aarav.sharma@example.com` / `patient123`

## Notes

- DB name defaults to `hms`.
- Change `SECRET_KEY` and disable debug for production.
- WeasyPrint can require additional native libs on Windows; if unavailable, invoice route returns HTML fallback.
