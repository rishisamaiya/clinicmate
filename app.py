"""
Clinic Management System - Simple Prototype
A basic healthcare management system for small clinics
"""
from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, Clinic, Patient, Appointment, Consultation
from datetime import datetime, date, timedelta
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database Configuration
# Use PostgreSQL (Supabase) in production, SQLite for local development
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # Production: Use PostgreSQL from Supabase
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
else:
    # Local Development: Use SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clinic.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

# Login required decorator
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'clinic_id' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ==================== AUTH ROUTES ====================

@app.route('/')
def index():
    """Home page - redirect to dashboard if logged in"""
    if 'clinic_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        clinic = Clinic.query.filter_by(email=email).first()
        
        if clinic and clinic.check_password(password):
            session['clinic_id'] = clinic.id
            session['clinic_name'] = clinic.clinic_name
            session['doctor_name'] = clinic.doctor_name
            flash(f'Welcome back, Dr. {clinic.doctor_name}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('auth/login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page for new clinics"""
    if request.method == 'POST':
        try:
            clinic = Clinic(
                clinic_name=request.form.get('clinic_name'),
                doctor_name=request.form.get('doctor_name'),
                specialization=request.form.get('specialization'),
                registration_number=request.form.get('registration_number'),
                phone=request.form.get('phone'),
                email=request.form.get('email'),
                address=request.form.get('address')
            )
            clinic.set_password(request.form.get('password'))
            
            db.session.add(clinic)
            db.session.commit()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
    
    return render_template('auth/register.html')


@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))


# ==================== DASHBOARD ====================

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    clinic_id = session['clinic_id']
    today = date.today()
    
    # Get today's appointments
    today_appointments = Appointment.query.filter_by(
        clinic_id=clinic_id,
        appointment_date=today
    ).order_by(Appointment.appointment_time).all()
    
    # Get statistics
    total_patients = Patient.query.filter_by(clinic_id=clinic_id).count()
    today_consultations = Consultation.query.filter_by(clinic_id=clinic_id).filter(
        db.func.date(Consultation.consultation_date) == today
    ).count()
    
    # Today's collection
    today_collection = db.session.query(db.func.sum(Consultation.total_amount)).filter(
        Consultation.clinic_id == clinic_id,
        db.func.date(Consultation.consultation_date) == today
    ).scalar() or 0
    
    return render_template('dashboard.html',
                         appointments=today_appointments,
                         total_patients=total_patients,
                         today_consultations=today_consultations,
                         today_collection=today_collection,
                         today=today)


# ==================== PATIENT ROUTES ====================

@app.route('/patients')
@login_required
def patients():
    """List all patients"""
    clinic_id = session['clinic_id']
    search = request.args.get('search', '')
    
    if search:
        patients = Patient.query.filter_by(clinic_id=clinic_id).filter(
            (Patient.name.ilike(f'%{search}%')) | 
            (Patient.phone.ilike(f'%{search}%')) |
            (Patient.patient_id.ilike(f'%{search}%'))
        ).order_by(Patient.registration_date.desc()).all()
    else:
        patients = Patient.query.filter_by(clinic_id=clinic_id).order_by(
            Patient.registration_date.desc()
        ).limit(100).all()
    
    return render_template('patients/list.html', patients=patients, search=search)


@app.route('/patients/add', methods=['GET', 'POST'])
@login_required
def add_patient():
    """Add new patient"""
    if request.method == 'POST':
        try:
            clinic_id = session['clinic_id']
            
            patient = Patient(
                clinic_id=clinic_id,
                patient_id=Patient.generate_patient_id(clinic_id),
                name=request.form.get('name'),
                age=int(request.form.get('age')) if request.form.get('age') else None,
                gender=request.form.get('gender'),
                blood_group=request.form.get('blood_group'),
                phone=request.form.get('phone'),
                email=request.form.get('email'),
                address=request.form.get('address'),
                allergies=request.form.get('allergies'),
                chronic_conditions=request.form.get('chronic_conditions'),
                emergency_contact=request.form.get('emergency_contact'),
                emergency_phone=request.form.get('emergency_phone')
            )
            
            db.session.add(patient)
            db.session.commit()
            
            flash(f'Patient {patient.name} registered successfully! (ID: {patient.patient_id})', 'success')
            return redirect(url_for('view_patient', patient_id=patient.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
    
    return render_template('patients/add.html')


@app.route('/patients/<int:patient_id>')
@login_required
def view_patient(patient_id):
    """View patient details"""
    clinic_id = session['clinic_id']
    patient = Patient.query.filter_by(id=patient_id, clinic_id=clinic_id).first_or_404()
    
    # Get consultation history
    consultations = Consultation.query.filter_by(patient_id=patient_id).order_by(
        Consultation.consultation_date.desc()
    ).all()
    
    # Get upcoming appointments
    upcoming_appointments = Appointment.query.filter_by(
        patient_id=patient_id
    ).filter(
        Appointment.appointment_date >= date.today(),
        Appointment.status.in_(['scheduled', 'checked-in'])
    ).order_by(Appointment.appointment_date).all()
    
    return render_template('patients/view.html',
                         patient=patient,
                         consultations=consultations,
                         upcoming_appointments=upcoming_appointments)


# ==================== APPOINTMENT ROUTES ====================

@app.route('/appointments')
@login_required
def appointments():
    """List appointments"""
    clinic_id = session['clinic_id']
    selected_date = request.args.get('date', str(date.today()))
    
    appointments = Appointment.query.filter_by(
        clinic_id=clinic_id,
        appointment_date=selected_date
    ).order_by(Appointment.appointment_time).all()
    
    return render_template('appointments/list.html',
                         appointments=appointments,
                         selected_date=selected_date)


@app.route('/appointments/book', methods=['GET', 'POST'])
@login_required
def book_appointment():
    """Book new appointment"""
    clinic_id = session['clinic_id']
    
    if request.method == 'POST':
        try:
            appointment = Appointment(
                clinic_id=clinic_id,
                patient_id=int(request.form.get('patient_id')),
                appointment_date=datetime.strptime(request.form.get('appointment_date'), '%Y-%m-%d').date(),
                appointment_time=request.form.get('appointment_time'),
                reason=request.form.get('reason'),
                status='scheduled'
            )
            
            db.session.add(appointment)
            db.session.commit()
            
            flash('Appointment booked successfully!', 'success')
            return redirect(url_for('appointments'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
    
    # Get patients for dropdown
    patients = Patient.query.filter_by(clinic_id=clinic_id).order_by(Patient.name).all()
    return render_template('appointments/book.html', patients=patients, today=date.today())


@app.route('/appointments/<int:appointment_id>/checkin', methods=['POST'])
@login_required
def checkin_appointment(appointment_id):
    """Check-in patient for appointment"""
    appointment = Appointment.query.get_or_404(appointment_id)
    appointment.status = 'checked-in'
    appointment.checked_in_at = datetime.utcnow()
    db.session.commit()
    
    flash('Patient checked in!', 'success')
    return redirect(url_for('appointments'))


# ==================== CONSULTATION ROUTES ====================

@app.route('/consultations/new/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
def new_consultation(appointment_id):
    """Create new consultation"""
    clinic_id = session['clinic_id']
    appointment = Appointment.query.get_or_404(appointment_id)
    patient = appointment.patient
    
    if request.method == 'POST':
        try:
            clinic = Clinic.query.get(clinic_id)
            
            consultation = Consultation(
                clinic_id=clinic_id,
                patient_id=patient.id,
                appointment_id=appointment_id,
                bp_systolic=int(request.form.get('bp_systolic')) if request.form.get('bp_systolic') else None,
                bp_diastolic=int(request.form.get('bp_diastolic')) if request.form.get('bp_diastolic') else None,
                pulse=int(request.form.get('pulse')) if request.form.get('pulse') else None,
                temperature=float(request.form.get('temperature')) if request.form.get('temperature') else None,
                weight=float(request.form.get('weight')) if request.form.get('weight') else None,
                chief_complaint=request.form.get('chief_complaint'),
                diagnosis=request.form.get('diagnosis'),
                prescription=request.form.get('prescription'),
                investigation=request.form.get('investigation'),
                treatment_plan=request.form.get('treatment_plan'),
                consultation_fee=clinic.consultation_fee,
                total_amount=clinic.consultation_fee,
                payment_status='paid' if request.form.get('payment_status') == 'paid' else 'unpaid',
                payment_method=request.form.get('payment_method')
            )
            
            # Follow-up date if provided
            if request.form.get('follow_up_date'):
                consultation.follow_up_date = datetime.strptime(
                    request.form.get('follow_up_date'), '%Y-%m-%d'
                ).date()
            
            # Update appointment status
            appointment.status = 'completed'
            appointment.completed_at = datetime.utcnow()
            
            # Update patient last visit
            patient.last_visit = datetime.utcnow()
            
            db.session.add(consultation)
            db.session.commit()
            
            flash('Consultation saved successfully!', 'success')
            return redirect(url_for('view_consultation', consultation_id=consultation.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
    
    # Get clinic consultation fee
    clinic = Clinic.query.get(clinic_id)
    
    return render_template('consultations/new.html',
                         appointment=appointment,
                         patient=patient,
                         consultation_fee=clinic.consultation_fee)


@app.route('/consultations/<int:consultation_id>')
@login_required
def view_consultation(consultation_id):
    """View consultation details / Print prescription"""
    clinic_id = session['clinic_id']
    consultation = Consultation.query.filter_by(
        id=consultation_id,
        clinic_id=clinic_id
    ).first_or_404()
    
    return render_template('consultations/view.html', consultation=consultation)


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)

