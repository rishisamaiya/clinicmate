"""
Database models for Clinic Management System
Simple prototype with essential features
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import hashlib

db = SQLAlchemy()

class Clinic(db.Model):
    """Clinic/Doctor account (like tenant in BizBooks)"""
    __tablename__ = 'clinics'
    
    id = db.Column(db.Integer, primary_key=True)
    clinic_name = db.Column(db.String(200), nullable=False)
    doctor_name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100))  # General Physician, Pediatrician, etc.
    registration_number = db.Column(db.String(50))  # Medical Council Registration
    
    # Contact
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    address = db.Column(db.Text)
    
    # Login
    password_hash = db.Column(db.String(200), nullable=False)
    
    # Settings
    consultation_fee = db.Column(db.Float, default=300)
    consultation_duration = db.Column(db.Integer, default=15)  # minutes
    working_hours_start = db.Column(db.String(10), default='09:00')
    working_hours_end = db.Column(db.String(10), default='18:00')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    patients = db.relationship('Patient', backref='clinic', lazy=True)
    appointments = db.relationship('Appointment', backref='clinic', lazy=True)
    
    def set_password(self, password):
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password):
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()


class Patient(db.Model):
    """Patient records"""
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinics.id'), nullable=False)
    
    # Demographics
    patient_id = db.Column(db.String(50), unique=True)  # e.g., PAT-0001
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))  # Male, Female, Other
    date_of_birth = db.Column(db.Date)
    blood_group = db.Column(db.String(10))
    
    # Contact
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    
    # Medical Info
    allergies = db.Column(db.Text)
    chronic_conditions = db.Column(db.Text)
    emergency_contact = db.Column(db.String(100))
    emergency_phone = db.Column(db.String(20))
    
    # Timestamps
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_visit = db.Column(db.DateTime)
    
    # Relationships
    appointments = db.relationship('Appointment', backref='patient', lazy=True)
    consultations = db.relationship('Consultation', backref='patient', lazy=True)
    
    @staticmethod
    def generate_patient_id(clinic_id):
        """
        Generate unique patient ID for a clinic
        Format: PAT-0001, PAT-0002, etc.
        Handles gaps from deleted patients and ensures uniqueness
        """
        # Get all existing patient IDs for this clinic
        existing_patients = Patient.query.filter_by(clinic_id=clinic_id).all()
        existing_ids = {p.patient_id for p in existing_patients if p.patient_id}
        
        # Find the highest number currently in use
        max_num = 0
        for patient_id in existing_ids:
            try:
                num = int(patient_id.split('-')[1])
                max_num = max(max_num, num)
            except (IndexError, ValueError):
                continue
        
        # Generate new IDs starting from max_num + 1
        # Keep trying until we find one that doesn't exist (handles edge cases)
        attempt = 0
        while attempt < 10000:  # Safety limit
            new_num = max_num + 1 + attempt
            new_id = f"PAT-{new_num:04d}"
            
            # Check if this ID already exists
            if new_id not in existing_ids:
                return new_id
            
            attempt += 1
        
        # Fallback: use timestamp-based ID (should never reach here)
        import time
        return f"PAT-{int(time.time()) % 100000:05d}"


class Appointment(db.Model):
    """Appointment scheduling"""
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinics.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    
    # Schedule
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.String(10), nullable=False)  # HH:MM format
    
    # Status
    status = db.Column(db.String(20), default='scheduled')  # scheduled, checked-in, completed, cancelled
    
    # Details
    reason = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    checked_in_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    consultation = db.relationship('Consultation', backref='appointment', uselist=False)


class Consultation(db.Model):
    """Consultation records"""
    __tablename__ = 'consultations'
    
    id = db.Column(db.Integer, primary_key=True)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinics.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'))
    
    # Vitals
    bp_systolic = db.Column(db.Integer)
    bp_diastolic = db.Column(db.Integer)
    pulse = db.Column(db.Integer)
    temperature = db.Column(db.Float)
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    
    # Consultation details
    chief_complaint = db.Column(db.Text)
    symptoms = db.Column(db.Text)
    diagnosis = db.Column(db.Text)
    prescription = db.Column(db.Text)  # JSON format for medicines
    investigation = db.Column(db.Text)  # Tests advised
    treatment_plan = db.Column(db.Text)
    
    # Follow-up
    follow_up_date = db.Column(db.Date)
    follow_up_notes = db.Column(db.Text)
    
    # Billing
    consultation_fee = db.Column(db.Float, default=0)
    medicine_charges = db.Column(db.Float, default=0)
    total_amount = db.Column(db.Float, default=0)
    payment_status = db.Column(db.String(20), default='unpaid')  # paid, unpaid
    payment_method = db.Column(db.String(20))  # cash, card, upi
    
    # Timestamps
    consultation_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    clinic = db.relationship('Clinic', backref='consultations')


