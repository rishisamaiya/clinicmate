-- Migration: Add Admin Features & Performance Indexes
-- Date: 2025-11-04
-- Description: Adds email verification, SMS settings, updated_at, and performance indexes

-- ====================
-- 1. ADD NEW COLUMNS TO CLINICS
-- ====================

-- Email Verification
ALTER TABLE clinics ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE clinics ADD COLUMN IF NOT EXISTS verification_token VARCHAR(100);
ALTER TABLE clinics ADD COLUMN IF NOT EXISTS verification_sent_at TIMESTAMP;

-- SMS Settings (for DLT reminders)
ALTER TABLE clinics ADD COLUMN IF NOT EXISTS sms_enabled BOOLEAN DEFAULT FALSE;
ALTER TABLE clinics ADD COLUMN IF NOT EXISTS sms_api_key VARCHAR(200);
ALTER TABLE clinics ADD COLUMN IF NOT EXISTS sms_sender_id VARCHAR(20);
ALTER TABLE clinics ADD COLUMN IF NOT EXISTS sms_template_id VARCHAR(50);

-- Timestamps
ALTER TABLE clinics ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- ====================
-- 2. CREATE UPDATE TRIGGER FOR CLINICS
-- ====================

CREATE OR REPLACE FUNCTION update_clinics_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS clinics_updated_at_trigger ON clinics;
CREATE TRIGGER clinics_updated_at_trigger
    BEFORE UPDATE ON clinics
    FOR EACH ROW
    EXECUTE FUNCTION update_clinics_updated_at();

-- ====================
-- 3. PERFORMANCE INDEXES
-- ====================

-- Clinics
CREATE INDEX IF NOT EXISTS idx_clinics_email ON clinics(email);
CREATE INDEX IF NOT EXISTS idx_clinics_verification_token ON clinics(verification_token);

-- Patients (common queries)
CREATE INDEX IF NOT EXISTS idx_patients_clinic_name ON patients(clinic_id, name);
CREATE INDEX IF NOT EXISTS idx_patients_phone ON patients(phone);
CREATE INDEX IF NOT EXISTS idx_patients_registration_date ON patients(registration_date DESC);
CREATE INDEX IF NOT EXISTS idx_patients_last_visit ON patients(last_visit DESC);

-- Appointments (calendar queries)
CREATE INDEX IF NOT EXISTS idx_appointments_clinic_date ON appointments(clinic_id, appointment_date, appointment_time);
CREATE INDEX IF NOT EXISTS idx_appointments_patient_date ON appointments(patient_id, appointment_date);
CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);
CREATE INDEX IF NOT EXISTS idx_appointments_created_at ON appointments(created_at DESC);

-- Consultations (history queries)
CREATE INDEX IF NOT EXISTS idx_consultations_clinic_date ON consultations(clinic_id, consultation_date DESC);
CREATE INDEX IF NOT EXISTS idx_consultations_patient_date ON consultations(patient_id, consultation_date DESC);
CREATE INDEX IF NOT EXISTS idx_consultations_payment ON consultations(payment_status);

-- Prescriptions (already mostly indexed, adding a few)
CREATE INDEX IF NOT EXISTS idx_prescriptions_patient_created ON prescriptions(patient_id, created_at DESC);

-- ====================
-- 4. SET EXISTING CLINICS AS VERIFIED (BACKWARD COMPATIBILITY)
-- ====================

-- Set all existing clinics as email_verified = TRUE
-- (They were created before verification was implemented)
UPDATE clinics 
SET email_verified = TRUE, 
    updated_at = CURRENT_TIMESTAMP
WHERE email_verified IS NULL OR email_verified = FALSE;

-- ====================
-- 5. ADD COMMENTS
-- ====================

COMMENT ON COLUMN clinics.email_verified IS 'Whether the clinic email has been verified';
COMMENT ON COLUMN clinics.verification_token IS 'Token for email verification';
COMMENT ON COLUMN clinics.sms_enabled IS 'Whether SMS reminders are enabled';
COMMENT ON COLUMN clinics.sms_api_key IS 'Encrypted API key for SMS gateway';
COMMENT ON COLUMN clinics.sms_sender_id IS 'DLT approved sender ID (6 characters)';
COMMENT ON COLUMN clinics.sms_template_id IS 'DLT approved template ID';

-- Migration completed successfully

