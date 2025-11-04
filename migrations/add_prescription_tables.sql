-- Migration: Add Prescription and Medicine Tables
-- Date: 2025-11-04
-- Description: Adds structured prescription management with medicine details

-- Create prescriptions table
CREATE TABLE IF NOT EXISTS prescriptions (
    id SERIAL PRIMARY KEY,
    clinic_id INTEGER NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    consultation_id INTEGER REFERENCES consultations(id) ON DELETE SET NULL,
    prescription_number VARCHAR(50) UNIQUE NOT NULL,
    diagnosis TEXT,
    notes TEXT,
    follow_up_date DATE,
    follow_up_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create medicines table
CREATE TABLE IF NOT EXISTS medicines (
    id SERIAL PRIMARY KEY,
    prescription_id INTEGER NOT NULL REFERENCES prescriptions(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    dosage VARCHAR(100),
    frequency VARCHAR(50),
    duration VARCHAR(50),
    timing VARCHAR(50),
    instructions TEXT,
    "order" INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_prescriptions_clinic_id ON prescriptions(clinic_id);
CREATE INDEX IF NOT EXISTS idx_prescriptions_patient_id ON prescriptions(patient_id);
CREATE INDEX IF NOT EXISTS idx_prescriptions_consultation_id ON prescriptions(consultation_id);
CREATE INDEX IF NOT EXISTS idx_prescriptions_number ON prescriptions(prescription_number);
CREATE INDEX IF NOT EXISTS idx_prescriptions_created_at ON prescriptions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_medicines_prescription_id ON medicines(prescription_id);

-- Add updated_at trigger for prescriptions table
CREATE OR REPLACE FUNCTION update_prescriptions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER prescriptions_updated_at_trigger
    BEFORE UPDATE ON prescriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_prescriptions_updated_at();

-- Add comment on tables
COMMENT ON TABLE prescriptions IS 'Stores prescription records with structured data';
COMMENT ON TABLE medicines IS 'Stores individual medicine entries for prescriptions';

-- Migration completed successfully

