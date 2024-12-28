Medical Management System (Desktop Python/Tkinter + PostgreSQL)
A desktop application for managing patients, appointments, and prescriptions, built with:

Python 3.x
Tkinter (for the GUI)
SQLAlchemy (for ORM/database access)
PostgreSQL (hosted on Tembo, but could be any Postgres instance)
ReportLab (for exporting patient data to PDF)
Features
View Patients

Displays a table (“Excel-like”) of all patients in the database, including:
Name, OIB, Date of Birth, Sex
Medical History
Appointments (with dates)
Prescriptions
Add Patient

Opens a form to input patient details (name, OIB, sex, date of birth, medical history, etc.) and save to DB.
Add Appointment

Select a patient from the table, then click “Add Appointment.”
Lets you choose hardcoded appointment types (e.g. GP, KRV, X-RAY) and specify a date/time.
Add Prescription

Select a patient from the table, then click “Add Prescription.”
Enter medication name, dosage, and optional doctor or date.
Search

Filter patients by Name or OIB via a search bar.
Export to PDF

Generates a PDF listing all patients, along with their appointments and prescriptions.
Prerequisites
Python 3.8+
PostgreSQL database
Tembo or another Postgres provider works fine.
