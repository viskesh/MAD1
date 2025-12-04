# MAD1
this is the official project of iitm modern application management

Project Report(Hospital management system)

The Hospital Management System is a web-based application designed to digitize hospital operations. It centralizes important data such as patient records, doctor information, and appointment schedules, making access quicker and more organized. By automating most hospital activities, the system reduces paperwork and minimizes human errors.
This platform ensures smooth coordination between hospital administrators, doctors, and patients. It is especially suitable for small and medium-sized healthcare centers that need a reliable but lightweight digital solution for daily management.
Approach:
The app was built using flask as backend framework sqlalchemy for ORM for database management, HTML/CSS(and jinja 2 templates) for the front end and SQLlite for database 
AI/LLM Declaration:
I have used ChatGPT-5 to assist on this project. The extent of ai usage is 5-10% only, limited for some SQLalchemy model definitions only,
all final logic, debugging, integration and designing on css were done manually
TECHNOLOGIES USED:
Library	

Flask	Core backend web framework for building the Hospital Management System
SQLAlchemy	ORM (Object Relational Mapper) for interacting with the SQLite database using Python classes
Jinja2	Template engine for rendering dynamic HTML templates
Bootstrap 5	Frontend styling and responsive UI design
Werkzeug Security	Secure password hashing and verification
Flask Sessions	Handling user session storage and login state
SQLite	Lightweight local database for storing users, doctors, patients, and appointments
JSON / Flask jsonify	Returning API responses in structured JSON format

Database Schema / ER Diagram
Tables:
1.	User — stores user authentication details (id, username, email, password, role, created_at)
2.	Patient — stores patient profile information (id, user_id, full_name, age, gender, phone, address, blood_group, is_active)
3.	Doctor — stores doctor professional details (id, user_id, full_name, specialization_id, phone, qualification, experience_years, is_active)
4.	Department — stores medical specializations (id, name, description)
5.	DoctorAvailability — stores doctor's available time slots (id, doctor_id, date, start_time, end_time, is_available)
6.	Appointment — stores appointment bookings (id, patient_id, doctor_id, appointment_date, appointment_time, status, reason, created_at)
7.	Treatment — stores medical records for completed appointments (id, appointment_id, diagnosis, prescription, notes, created_at)
ER DIAGRAM:
 
API Resource Endpoints
Endpoint	Method	Description
/api/appointments	GET	Fetch all appointments in the system
/api/appointment/<id>	GET	Fetch detailed information of a specific appointment
/api/doctors	GET	Retrieve all active doctors with specialization and experience
/api/patients	GET	Fetch all active patients (Admin only)

Architecture and Features (optional)
Architecture Overview:
•	app.py – Main Flask application entry point
•	/models – SQLAlchemy database models (User, Patient, Doctor, Appointment, etc.)
•	/routes – Flask routes for admin, doctor, patient, and API functionalities
•	/templates – Jinja2 HTML templates (admin/doctor/patient dashboards and pages)
•	/static – CSS, JS, Bootstrap assets, and frontend resources
•	/database (hospital.db) – SQLite database storing system records
•	/api endpoints – JSON-based API responses for Appointments, Doctors, Patients
________________________________________
Implemented Features:
•	User registration and login (Patient default)
•	Role-based authentication (Admin / Doctor / Patient)
•	Doctor management (add, edit, delete) by Admin
•	Patient management and profile update
•	Department and specialization-based doctor filtering
•	Appointment booking with conflict checks
•	Doctor availability scheduling
•	Doctor dashboard with weekly appointments
•	Patient dashboard with upcoming visits
•	Treatment recording for completed appointments
•	Secure password hashing using Werkzeug
•	Session-based access control
•	REST API endpoints for Appointments, Patients, Doctors
________________________________________
Additional Features:
•	Export data as JSON (using API endpoints)
•	Easy extensibility for CSV/PDF export
•	Optional AI/ML integration for appointment prediction or analytics (future scope)

VIDEO PRESENTATION LINK:
Drive link:
https://drive.google.com/file/d/1SdZ62NB3zZqFJy_QF0lWCYnSVMu2uA7M/view?usp=drive_link

Conclusion
The Hospital Management System provides a complete digital solution for managing hospital operations in an efficient and organized way. By centralizing patient data, doctor information, and appointment scheduling, it reduces manual workload and minimizes errors that commonly occur with paper-based systems. The system ensures smooth communication among administrators, doctors, and patients through its clear role-based structure. With features such as treatment history, doctor availability, and responsive design, it offers convenience and reliability to all users.
