from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Vishal@2007'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    phone = db.Column(db.String(15))
    address = db.Column(db.Text)
    blood_group = db.Column(db.String(5))
    is_active = db.Column(db.Boolean, default=True)

    user = db.relationship('User', backref='patient_profile')
    appointments = db.relationship('Appointment', backref='patient', lazy=True)




class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)

    doctors = db.relationship('Doctor', backref='department', lazy=True)



class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    specialization_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    phone = db.Column(db.String(15))
    qualification = db.Column(db.String(200))
    experience_years = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True)

    user = db.relationship('User', backref='doctor_profile')
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)
    availability = db.relationship('DoctorAvailability', backref='doctor', lazy=True)



class DoctorAvailability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_available = db.Column(db.Boolean, default=True)



class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='Booked')
    reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)

    treatment = db.relationship('Treatment', backref='appointment', uselist=False)



class Treatment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
    diagnosis = db.Column(db.Text)
    prescription = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)




def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for('login'))
        return func(*args, **kwargs)

    return wrapper


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get('role') != 'admin':
            flash("Admins only!", "danger")
            return redirect(url_for('index'))
        return func(*args, **kwargs)

    return wrapper


def doctor_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get('role') != 'doctor':
            flash("Doctor access only.", "danger")
            return redirect(url_for('index'))
        return func(*args, **kwargs)

    return wrapper


def patient_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get('role') != 'patient':
            flash("Patient access only.", "danger")
            return redirect(url_for('index'))
        return func(*args, **kwargs)

    return wrapper




@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form.get('username')
        pwd = request.form.get('password')

        user = User.query.filter_by(username=uname).first()
        if user and check_password_hash(user.password, pwd):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash(f"Welcome back, {user.username}!", "success")


            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'doctor':
                return redirect(url_for('doctor_dashboard'))
            else:
                return redirect(url_for('patient_dashboard'))
        else:
            flash("Invalid credentials. Try again.", "danger")
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        uname = request.form.get('username')
        mail = request.form.get('email')
        pwd = request.form.get('password')


        if User.query.filter_by(username=uname).first():
            flash("Username already taken.", "danger")
            return redirect(url_for('register'))

        if User.query.filter_by(email=mail).first():
            flash("Email already registered.", "danger")
            return redirect(url_for('register'))


        hashed = generate_password_hash(pwd)
        new_user = User(username=uname, email=mail, password=hashed, role='patient')
        db.session.add(new_user)
        db.session.flush()


        patient = Patient(
            user_id=new_user.id,
            full_name=request.form.get('full_name'),
            age=request.form.get('age'),
            gender=request.form.get('gender'),
            phone=request.form.get('phone'),
            address=request.form.get('address'),
            blood_group=request.form.get('blood_group')
        )
        db.session.add(patient)
        db.session.commit()

        flash("Account created! You can now log in.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    total_doctors = Doctor.query.filter_by(is_active=True).count()
    total_patients = Patient.query.filter_by(is_active=True).count()
    total_appointments = Appointment.query.count()
    upcoming_appointments = Appointment.query.filter(
        Appointment.appointment_date >= datetime.now().date(),
        Appointment.status == 'Booked'
    ).count()
    
    recent_appointments = Appointment.query.order_by(Appointment.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_doctors=total_doctors,
                         total_patients=total_patients,
                         total_appointments=total_appointments,
                         upcoming_appointments=upcoming_appointments,
                         recent_appointments=recent_appointments)

@app.route('/admin/doctors')
@login_required
@admin_required
def admin_doctors():
    search = request.args.get('search', '')
    if search:
        doctors = Doctor.query.filter(
            (Doctor.full_name.contains(search)) |
            (Doctor.department.has(Department.name.contains(search)))
        ).all()
    else:
        doctors = Doctor.query.all()
    
    return render_template('admin/doctors.html', doctors=doctors, search=search)

@app.route('/admin/doctor/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_doctor():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        specialization_id = request.form.get('specialization_id')
        phone = request.form.get('phone')
        qualification = request.form.get('qualification')
        experience_years = request.form.get('experience_years')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('admin_add_doctor'))
        
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password, role='doctor')
        db.session.add(new_user)
        db.session.flush()
        
        new_doctor = Doctor(
            user_id=new_user.id,
            full_name=full_name,
            specialization_id=specialization_id,
            phone=phone,
            qualification=qualification,
            experience_years=experience_years
        )
        db.session.add(new_doctor)
        db.session.commit()
        
        flash('Doctor added successfully!', 'success')
        return redirect(url_for('admin_doctors'))
    
    departments = Department.query.all()
    return render_template('admin/add_doctor.html', departments=departments)

@app.route('/admin/doctor/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_doctor(id):
    doctor = Doctor.query.get_or_404(id)
    
    if request.method == 'POST':
        doctor.full_name = request.form.get('full_name')
        doctor.specialization_id = request.form.get('specialization_id')
        doctor.phone = request.form.get('phone')
        doctor.qualification = request.form.get('qualification')
        doctor.experience_years = request.form.get('experience_years')
        
        db.session.commit()
        flash('Doctor updated successfully!', 'success')
        return redirect(url_for('admin_doctors'))
    
    departments = Department.query.all()
    return render_template('admin/edit_doctor.html', doctor=doctor, departments=departments)

@app.route('/admin/doctor/delete/<int:id>')
@login_required
@admin_required
def admin_delete_doctor(id):
    doctor = Doctor.query.get_or_404(id)
    doctor.is_active = False
    db.session.commit()
    flash('Doctor removed successfully!', 'success')
    return redirect(url_for('admin_doctors'))

@app.route('/admin/patients')
@login_required
@admin_required
def admin_patients():
    search = request.args.get('search', '')
    if search:
        patients = Patient.query.filter(
            (Patient.full_name.contains(search)) |
            (Patient.phone.contains(search))
        ).all()
    else:
        patients = Patient.query.all()
    
    return render_template('admin/patients.html', patients=patients, search=search)

@app.route('/admin/patient/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_patient(id):
    patient = Patient.query.get_or_404(id)
    
    if request.method == 'POST':
        patient.full_name = request.form.get('full_name')
        patient.age = request.form.get('age')
        patient.gender = request.form.get('gender')
        patient.phone = request.form.get('phone')
        patient.address = request.form.get('address')
        patient.blood_group = request.form.get('blood_group')
        
        db.session.commit()
        flash('Patient updated successfully!', 'success')
        return redirect(url_for('admin_patients'))
    
    return render_template('admin/edit_patients.html', patient=patient)

@app.route('/admin/appointments')
@login_required
@admin_required
def admin_appointments():
    appointments = Appointment.query.order_by(Appointment.appointment_date.desc()).all()
    return render_template('admin/appointments.html', appointments=appointments)

@app.route('/admin/patient/<int:patient_id>/history')
def admin_patient_history(patient_id):
    patient = Patient.query.get(patient_id)
    if not patient:
        abort(404)

    treatments = (
        Treatment.query
        .join(Appointment, Treatment.appointment_id == Appointment.id)
        .join(Doctor, Appointment.doctor_id == Doctor.id)
        .join(Department, Doctor.specialization_id == Department.id)
        .filter(Appointment.patient_id == patient_id)
        .order_by(Appointment.appointment_date.desc(),
                  Appointment.appointment_time.desc())
        .all()
    )

    return render_template('admin/patient_history.html',
                           patient=patient,
                           treatments=treatments)


@app.route('/doctor/dashboard')
@login_required
@doctor_required
def doctor_dashboard():
    doctor = Doctor.query.filter_by(user_id=session['user_id']).first()
    
    today = datetime.now().date()
    week_end = today + timedelta(days=7)
    
    upcoming_appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.appointment_date >= today,
        Appointment.appointment_date <= week_end,
        Appointment.status == 'Booked'
    ).order_by(Appointment.appointment_date).all()
    
    patients = db.session.query(Patient).join(Appointment).filter(
        Appointment.doctor_id == doctor.id
    ).distinct().all()
    
    return render_template('doctor/dashboard.html',
                         doctor=doctor,
                         upcoming_appointments=upcoming_appointments,
                         patients=patients)

@app.route('/doctor/appointments')
@login_required
@doctor_required
def doctor_appointments():
    doctor = Doctor.query.filter_by(user_id=session['user_id']).first()
    appointments = Appointment.query.filter_by(doctor_id=doctor.id).order_by(Appointment.appointment_date.desc()).all()
    return render_template('doctor/appointments.html', appointments=appointments)

@app.route('/doctor/appointment/complete/<int:id>', methods=['GET', 'POST'])
@login_required
@doctor_required
def doctor_complete_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    
    if request.method == 'POST':
        diagnosis = request.form.get('diagnosis')
        prescription = request.form.get('prescription')
        notes = request.form.get('notes')
        
        appointment.status = 'Completed'
        
        treatment = Treatment(
            appointment_id=appointment.id,
            diagnosis=diagnosis,
            prescription=prescription,
            notes=notes
        )
        db.session.add(treatment)
        db.session.commit()
        
        flash('Appointment marked as completed!', 'success')
        return redirect(url_for('doctor_appointments'))
    
    return render_template('doctor/complete_appointment.html', appointment=appointment)

@app.route('/doctor/patient/history/<int:id>')
@login_required
@doctor_required
def doctor_patient_history(id):
    patient = Patient.query.get_or_404(id)
    appointments = Appointment.query.filter_by(
        patient_id=patient.id,
        status='Completed'
    ).order_by(Appointment.appointment_date.desc()).all()
    
    return render_template('doctor/patient_history.html', patient=patient, appointments=appointments)

@app.route('/doctor/availability', methods=['GET', 'POST'])
@login_required
@doctor_required
def doctor_availability():
    doctor = Doctor.query.filter_by(user_id=session['user_id']).first()
    
    if request.method == 'POST':
        date_str = request.form.get('date')
        start_time_str = request.form.get('start_time')
        end_time_str = request.form.get('end_time')
        
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        start_time = datetime.strptime(start_time_str, '%H:%M').time()
        end_time = datetime.strptime(end_time_str, '%H:%M').time()
        
        availability = DoctorAvailability(
            doctor_id=doctor.id,
            date=date,
            start_time=start_time,
            end_time=end_time
        )
        db.session.add(availability)
        db.session.commit()
        
        flash('Availability added successfully!', 'success')
        return redirect(url_for('doctor_availability'))
    
    today = datetime.now().date()
    week_end = today + timedelta(days=7)
    
    availability_list = DoctorAvailability.query.filter(
        DoctorAvailability.doctor_id == doctor.id,
        DoctorAvailability.date >= today,
        DoctorAvailability.date <= week_end
    ).order_by(DoctorAvailability.date).all()
    
    return render_template('doctor/availability.html', availability_list=availability_list)



@app.route('/patient/dashboard')
@login_required
@patient_required
def patient_dashboard():
    patient = Patient.query.filter_by(user_id=session['user_id']).first()
    departments = Department.query.all()
    
    today = datetime.now().date()
    upcoming_appointments = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.appointment_date >= today,
        Appointment.status == 'Booked'
    ).order_by(Appointment.appointment_date).all()
    
    return render_template('patient/dashboard.html',
                         patient=patient,
                         departments=departments,
                         upcoming_appointments=upcoming_appointments)

@app.route('/patient/doctors')
@login_required
@patient_required
def patient_doctors():
    dept_id = request.args.get('department')
    search = request.args.get('search', '')
    
    query = Doctor.query.filter_by(is_active=True)
    
    if dept_id:
        query = query.filter_by(specialization_id=dept_id)
    
    if search:
        query = query.filter(Doctor.full_name.contains(search))
    
    doctors = query.all()
    departments = Department.query.all()
    
    return render_template('patient/doctors.html',
                         doctors=doctors,
                         departments=departments,
                         selected_dept=dept_id,
                         search=search)

@app.route('/patient/doctor/<int:id>')
@login_required
@patient_required
def patient_doctor_detail(id):
    doctor = Doctor.query.get_or_404(id)
    
    today = datetime.now().date()
    week_end = today + timedelta(days=7)
    
    availability = DoctorAvailability.query.filter(
        DoctorAvailability.doctor_id == doctor.id,
        DoctorAvailability.date >= today,
        DoctorAvailability.date <= week_end,
        DoctorAvailability.is_available == True
    ).order_by(DoctorAvailability.date).all()
    
    return render_template('patient/doctor_detail.html', doctor=doctor, availability=availability)

@app.route('/patient/book-appointment/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
@patient_required
def patient_book_appointment(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    patient = Patient.query.filter_by(user_id=session['user_id']).first()
    
    if request.method == 'POST':
        appointment_date_str = request.form.get('appointment_date')
        appointment_time_str = request.form.get('appointment_time')
        reason = request.form.get('reason')
        
        appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%d').date()
        appointment_time = datetime.strptime(appointment_time_str, '%H:%M').time()
        
        # Check for conflicts
        existing = Appointment.query.filter_by(
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time
        ).filter(Appointment.status != 'Cancelled').first()
        
        if existing:
            flash('This time slot is already booked. Please choose another time.', 'danger')
            return redirect(url_for('patient_book_appointment', doctor_id=doctor_id))
        
        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            reason=reason
        )
        db.session.add(appointment)
        db.session.commit()
        
        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('patient_appointments'))
    
    return render_template('patient/book_appointment.html', doctor=doctor)

@app.route('/patient/appointments')
@login_required
@patient_required
def patient_appointments():
    patient = Patient.query.filter_by(user_id=session['user_id']).first()
    appointments = Appointment.query.filter_by(patient_id=patient.id).order_by(Appointment.appointment_date.desc()).all()
    return render_template('patient/appointments.html', appointments=appointments)

@app.route('/patient/appointment/cancel/<int:id>')
@login_required
@patient_required
def patient_cancel_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    patient = Patient.query.filter_by(user_id=session['user_id']).first()
    
    if appointment.patient_id != patient.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('patient_appointments'))
    
    appointment.status = 'Cancelled'
    db.session.commit()
    
    flash('Appointment cancelled successfully!', 'info')
    return redirect(url_for('patient_appointments'))

@app.route('/patient/history')
@login_required
@patient_required
def patient_history():
    patient = Patient.query.filter_by(user_id=session['user_id']).first()
    appointments = Appointment.query.filter_by(
        patient_id=patient.id,
        status='Completed'
    ).order_by(Appointment.appointment_date.desc()).all()
    
    return render_template('patient/history.html', appointments=appointments)

@app.route('/patient/profile', methods=['GET', 'POST'])
@login_required
@patient_required
def patient_profile():
    patient = Patient.query.filter_by(user_id=session['user_id']).first()
    
    if request.method == 'POST':
        patient.full_name = request.form.get('full_name')
        patient.age = request.form.get('age')
        patient.gender = request.form.get('gender')
        patient.phone = request.form.get('phone')
        patient.address = request.form.get('address')
        patient.blood_group = request.form.get('blood_group')
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('patient_profile'))
    
    return render_template('patient/profile.html', patient=patient)



@app.route('/api/appointments', methods=['GET'])
@login_required
def api_get_appointments():
    appointments = Appointment.query.all()
    return jsonify([{
        'id': a.id,
        'patient_name': a.patient.full_name,
        'doctor_name': a.doctor.full_name,
        'date': a.appointment_date.strftime('%Y-%m-%d'),
        'time': a.appointment_time.strftime('%H:%M'),
        'status': a.status
    } for a in appointments])

@app.route('/api/appointment/<int:id>', methods=['GET'])
@login_required
def api_get_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    return jsonify({
        'id': appointment.id,
        'patient_name': appointment.patient.full_name,
        'doctor_name': appointment.doctor.full_name,
        'date': appointment.appointment_date.strftime('%Y-%m-%d'),
        'time': appointment.appointment_time.strftime('%H:%M'),
        'status': appointment.status,
        'reason': appointment.reason
    })

@app.route('/api/doctors', methods=['GET'])
def api_get_doctors():
    doctors = Doctor.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': d.id,
        'name': d.full_name,
        'specialization': d.department.name,
        'phone': d.phone,
        'experience': d.experience_years
    } for d in doctors])

@app.route('/api/patients', methods=['GET'])
@login_required
@admin_required
def api_get_patients():
    patients = Patient.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': p.id,
        'name': p.full_name,
        'age': p.age,
        'phone': p.phone,
        'blood_group': p.blood_group
    } for p in patients])

def init_db():
    with app.app_context():
        db.create_all()
        
        if Department.query.count()==0:
            departments = [
                    Department(name='Cardiology', description='Heart and cardiovascular system'),
                    Department(name='Neurology', description='Brain and nervous system'),
                    Department(name='Orthopedics', description='Bones and joints'),
                    Department(name='Pediatrics', description='Children healthcare'),
                    Department(name='Dermatology', description='Skin conditions'),
                    Department(name='General Medicine', description='General health consultation')
                ]
            db.session.add_all(departments)

            db.session.commit()
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()
    app.run(debug=True)