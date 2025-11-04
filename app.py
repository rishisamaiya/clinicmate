"""
Clinic Management System - Simple Prototype
A basic healthcare management system for small clinics
"""
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, Clinic, Patient, Appointment, Consultation, Prescription, Medicine, MedicineMaster
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

# Create tables (for serverless compatibility)
def init_db():
    """Initialize database tables if they don't exist"""
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables initialized")
        except Exception as e:
            print(f"⚠️ Database initialization error: {e}")

# Initialize database on first import
init_db()

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


# ==================== SETTINGS & PROFILE ====================

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Clinic settings and profile management"""
    clinic_id = session['clinic_id']
    clinic = Clinic.query.get_or_404(clinic_id)
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_profile':
            try:
                # Update clinic details
                clinic.clinic_name = request.form.get('clinic_name')
                clinic.doctor_name = request.form.get('doctor_name')
                clinic.specialization = request.form.get('specialization')
                clinic.registration_number = request.form.get('registration_number')
                clinic.phone = request.form.get('phone')
                clinic.address = request.form.get('address')
                clinic.consultation_fee = float(request.form.get('consultation_fee', 300))
                clinic.working_hours_start = request.form.get('working_hours_start')
                clinic.working_hours_end = request.form.get('working_hours_end')
                
                # Update session
                session['clinic_name'] = clinic.clinic_name
                session['doctor_name'] = clinic.doctor_name
                
                db.session.commit()
                flash('Profile updated successfully!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating profile: {str(e)}', 'error')
        
        elif action == 'change_password':
            try:
                current_password = request.form.get('current_password')
                new_password = request.form.get('new_password')
                confirm_password = request.form.get('confirm_password')
                
                # Verify current password
                if not clinic.check_password(current_password):
                    flash('Current password is incorrect', 'error')
                elif new_password != confirm_password:
                    flash('New passwords do not match', 'error')
                elif len(new_password) < 6:
                    flash('Password must be at least 6 characters', 'error')
                else:
                    clinic.set_password(new_password)
                    db.session.commit()
                    flash('Password changed successfully!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error changing password: {str(e)}', 'error')
        
        elif action == 'update_sms':
            try:
                clinic.sms_enabled = request.form.get('sms_enabled') == 'on'
                clinic.sms_sender_id = request.form.get('sms_sender_id')
                clinic.sms_template_id = request.form.get('sms_template_id')
                
                # Only update API key if provided
                api_key = request.form.get('sms_api_key')
                if api_key and api_key.strip():
                    clinic.sms_api_key = api_key
                
                db.session.commit()
                flash('SMS settings updated successfully!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating SMS settings: {str(e)}', 'error')
        
        return redirect(url_for('settings'))
    
    return render_template('settings.html', clinic=clinic)


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
        clinic_id = session['clinic_id']
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # Generate unique patient ID
                patient_id = Patient.generate_patient_id(clinic_id)
                
                patient = Patient(
                    clinic_id=clinic_id,
                    patient_id=patient_id,
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
                
                flash(f'✅ Patient {patient.name} registered successfully! (ID: {patient.patient_id})', 'success')
                return redirect(url_for('view_patient', patient_id=patient.id))
                
            except Exception as e:
                db.session.rollback()
                error_msg = str(e)
                
                # Check if it's a duplicate key error
                if 'unique constraint' in error_msg.lower() or 'duplicate' in error_msg.lower():
                    if attempt < max_retries - 1:
                        # Retry with a new ID
                        continue
                    else:
                        flash('⚠️ Unable to generate unique patient ID. Please try again.', 'error')
                else:
                    # Other error - show and don't retry
                    flash(f'❌ Error: {error_msg}', 'error')
                    break
    
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


# ==================== PRESCRIPTION ROUTES ====================

@app.route('/prescriptions')
@login_required
def prescriptions():
    """List all prescriptions"""
    clinic_id = session['clinic_id']
    search = request.args.get('search', '')
    
    if search:
        # Search by patient name, prescription number, or diagnosis
        prescriptions_list = Prescription.query.filter_by(clinic_id=clinic_id).join(Patient).filter(
            (Patient.name.ilike(f'%{search}%')) | 
            (Prescription.prescription_number.ilike(f'%{search}%')) |
            (Prescription.diagnosis.ilike(f'%{search}%'))
        ).order_by(Prescription.created_at.desc()).all()
    else:
        prescriptions_list = Prescription.query.filter_by(clinic_id=clinic_id).order_by(
            Prescription.created_at.desc()
        ).limit(100).all()
    
    return render_template('prescriptions/list.html', prescriptions=prescriptions_list, search=search)


@app.route('/prescriptions/new/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def new_prescription(patient_id):
    """Create new prescription"""
    clinic_id = session['clinic_id']
    patient = Patient.query.filter_by(id=patient_id, clinic_id=clinic_id).first_or_404()
    
    # Get consultation_id if passed
    consultation_id = request.args.get('consultation_id', type=int)
    consultation = None
    if consultation_id:
        consultation = Consultation.query.filter_by(
            id=consultation_id,
            clinic_id=clinic_id
        ).first()
    
    if request.method == 'POST':
        try:
            # Generate prescription number
            prescription_number = Prescription.generate_prescription_number(clinic_id)
            
            # Create prescription
            prescription = Prescription(
                clinic_id=clinic_id,
                patient_id=patient_id,
                consultation_id=consultation_id,
                prescription_number=prescription_number,
                diagnosis=request.form.get('diagnosis'),
                notes=request.form.get('notes')
            )
            
            # Follow-up date if provided
            if request.form.get('follow_up_date'):
                prescription.follow_up_date = datetime.strptime(
                    request.form.get('follow_up_date'), '%Y-%m-%d'
                ).date()
            
            db.session.add(prescription)
            db.session.flush()  # Get prescription.id
            
            # Add medicines
            medicine_count = int(request.form.get('medicine_count', 0))
            for i in range(medicine_count):
                name = request.form.get(f'medicine_name_{i}')
                if name and name.strip():  # Only add if name is provided
                    medicine = Medicine(
                        prescription_id=prescription.id,
                        name=name,
                        dosage=request.form.get(f'medicine_dosage_{i}'),
                        frequency=request.form.get(f'medicine_frequency_{i}'),
                        duration=request.form.get(f'medicine_duration_{i}'),
                        timing=request.form.get(f'medicine_timing_{i}'),
                        instructions=request.form.get(f'medicine_instructions_{i}'),
                        order=i
                    )
                    db.session.add(medicine)
            
            db.session.commit()
            
            flash(f'✅ Prescription {prescription.prescription_number} created successfully!', 'success')
            return redirect(url_for('view_prescription', prescription_id=prescription.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error: {str(e)}', 'error')
    
    return render_template('prescriptions/new.html', 
                         patient=patient,
                         consultation=consultation)


@app.route('/prescriptions/<int:prescription_id>')
@login_required
def view_prescription(prescription_id):
    """View prescription details / Print"""
    clinic_id = session['clinic_id']
    prescription = Prescription.query.filter_by(
        id=prescription_id,
        clinic_id=clinic_id
    ).first_or_404()
    
    return render_template('prescriptions/view.html', prescription=prescription)


@app.route('/prescriptions/<int:prescription_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_prescription(prescription_id):
    """Edit existing prescription"""
    clinic_id = session['clinic_id']
    prescription = Prescription.query.filter_by(
        id=prescription_id,
        clinic_id=clinic_id
    ).first_or_404()
    
    if request.method == 'POST':
        try:
            # Update prescription details
            prescription.diagnosis = request.form.get('diagnosis')
            prescription.notes = request.form.get('notes')
            prescription.updated_at = datetime.utcnow()
            
            # Follow-up date
            if request.form.get('follow_up_date'):
                prescription.follow_up_date = datetime.strptime(
                    request.form.get('follow_up_date'), '%Y-%m-%d'
                ).date()
            else:
                prescription.follow_up_date = None
            
            # Delete existing medicines
            Medicine.query.filter_by(prescription_id=prescription.id).delete()
            
            # Add updated medicines
            medicine_count = int(request.form.get('medicine_count', 0))
            for i in range(medicine_count):
                name = request.form.get(f'medicine_name_{i}')
                if name and name.strip():
                    medicine = Medicine(
                        prescription_id=prescription.id,
                        name=name,
                        dosage=request.form.get(f'medicine_dosage_{i}'),
                        frequency=request.form.get(f'medicine_frequency_{i}'),
                        duration=request.form.get(f'medicine_duration_{i}'),
                        timing=request.form.get(f'medicine_timing_{i}'),
                        instructions=request.form.get(f'medicine_instructions_{i}'),
                        order=i
                    )
                    db.session.add(medicine)
            
            db.session.commit()
            
            flash(f'✅ Prescription {prescription.prescription_number} updated successfully!', 'success')
            return redirect(url_for('view_prescription', prescription_id=prescription.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error: {str(e)}', 'error')
    
    return render_template('prescriptions/edit.html', prescription=prescription)


@app.route('/prescriptions/<int:prescription_id>/delete', methods=['POST'])
@login_required
def delete_prescription(prescription_id):
    """Delete prescription"""
    clinic_id = session['clinic_id']
    prescription = Prescription.query.filter_by(
        id=prescription_id,
        clinic_id=clinic_id
    ).first_or_404()
    
    try:
        prescription_number = prescription.prescription_number
        db.session.delete(prescription)
        db.session.commit()
        flash(f'Prescription {prescription_number} deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('prescriptions'))


# ==================== MEDICINE AUTOCOMPLETE API ====================

@app.route('/api/medicines/search')
@login_required
def search_medicines():
    """Search medicines for autocomplete"""
    clinic_id = session['clinic_id']
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 2:
        return jsonify([])
    
    # Search in medicine master (case-insensitive)
    medicines = MedicineMaster.query.filter_by(clinic_id=clinic_id).filter(
        db.or_(
            MedicineMaster.name.ilike(f'{query}%'),
            MedicineMaster.name.ilike(f'%{query}%')
        )
    ).order_by(
        MedicineMaster.usage_count.desc(),
        MedicineMaster.name
    ).limit(10).all()
    
    results = []
    for med in medicines:
        results.append({
            'name': med.name,
            'generic_name': med.generic_name,
            'common_dosage': med.common_dosage,
            'common_frequency': med.common_frequency,
            'common_duration': med.common_duration,
            'common_timing': med.common_timing,
            'usage_count': med.usage_count
        })
    
    return jsonify(results)


@app.route('/api/medicines/add', methods=['POST'])
@login_required
def add_medicine_to_master():
    """Add or update medicine in master list"""
    clinic_id = session['clinic_id']
    data = request.get_json()
    
    medicine_name = data.get('name', '').strip()
    if not medicine_name:
        return jsonify({'success': False, 'error': 'Medicine name required'}), 400
    
    try:
        # Check if medicine already exists
        medicine = MedicineMaster.query.filter_by(
            clinic_id=clinic_id,
            name=medicine_name
        ).first()
        
        if medicine:
            # Update usage count and last used
            medicine.usage_count += 1
            medicine.last_used = datetime.utcnow()
            
            # Update common values if provided
            if data.get('dosage'):
                medicine.common_dosage = data.get('dosage')
            if data.get('frequency'):
                medicine.common_frequency = data.get('frequency')
            if data.get('duration'):
                medicine.common_duration = data.get('duration')
            if data.get('timing'):
                medicine.common_timing = data.get('timing')
        else:
            # Create new medicine entry
            medicine = MedicineMaster(
                clinic_id=clinic_id,
                name=medicine_name,
                generic_name=data.get('generic_name'),
                common_dosage=data.get('dosage'),
                common_frequency=data.get('frequency'),
                common_duration=data.get('duration'),
                common_timing=data.get('timing'),
                category=data.get('category'),
                usage_count=1
            )
            db.session.add(medicine)
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Medicine added to library'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)

