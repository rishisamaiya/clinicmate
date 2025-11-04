-- Migration: Add Medicine Master Table for Autocomplete
-- Date: 2025-11-04
-- Description: Adds medicine library/master table for autocomplete suggestions

-- Create medicine_master table
CREATE TABLE IF NOT EXISTS medicine_master (
    id SERIAL PRIMARY KEY,
    clinic_id INTEGER NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    generic_name VARCHAR(200),
    common_dosage VARCHAR(100),
    common_frequency VARCHAR(50),
    common_duration VARCHAR(50),
    common_timing VARCHAR(50),
    category VARCHAR(100),
    usage_count INTEGER DEFAULT 1,
    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_medicine_per_clinic UNIQUE (clinic_id, name)
);

-- Create indexes for better search performance
CREATE INDEX IF NOT EXISTS idx_medicine_master_clinic_id ON medicine_master(clinic_id);
CREATE INDEX IF NOT EXISTS idx_medicine_master_name ON medicine_master(name);
CREATE INDEX IF NOT EXISTS idx_medicine_master_usage ON medicine_master(usage_count DESC);
CREATE INDEX IF NOT EXISTS idx_medicine_master_last_used ON medicine_master(last_used DESC);

-- Add comment
COMMENT ON TABLE medicine_master IS 'Master list of medicines for autocomplete suggestions and usage tracking';

-- Optional: Insert some common medicines for initial setup (customize as needed)
-- These are sample medicines, you can add more based on your clinic's needs

-- Analgesics & Antipyretics
INSERT INTO medicine_master (clinic_id, name, common_dosage, common_frequency, common_duration, common_timing, category, usage_count)
SELECT id, 'Paracetamol', '650mg', '1-0-1', '5 days', 'After food', 'Analgesic', 0 FROM clinics
ON CONFLICT (clinic_id, name) DO NOTHING;

INSERT INTO medicine_master (clinic_id, name, common_dosage, common_frequency, common_duration, common_timing, category, usage_count)
SELECT id, 'Ibuprofen', '400mg', '1-1-1', '3 days', 'After food', 'Analgesic', 0 FROM clinics
ON CONFLICT (clinic_id, name) DO NOTHING;

-- Antibiotics
INSERT INTO medicine_master (clinic_id, name, common_dosage, common_frequency, common_duration, common_timing, category, usage_count)
SELECT id, 'Amoxicillin', '500mg', '1-1-1', '5 days', 'After food', 'Antibiotic', 0 FROM clinics
ON CONFLICT (clinic_id, name) DO NOTHING;

INSERT INTO medicine_master (clinic_id, name, common_dosage, common_frequency, common_duration, common_timing, category, usage_count)
SELECT id, 'Azithromycin', '500mg', '1-0-0', '3 days', 'After food', 'Antibiotic', 0 FROM clinics
ON CONFLICT (clinic_id, name) DO NOTHING;

-- Antihistamines
INSERT INTO medicine_master (clinic_id, name, common_dosage, common_frequency, common_duration, common_timing, category, usage_count)
SELECT id, 'Cetrizine', '10mg', '0-0-1', '5 days', 'After food', 'Antihistamine', 0 FROM clinics
ON CONFLICT (clinic_id, name) DO NOTHING;

-- Antacids
INSERT INTO medicine_master (clinic_id, name, common_dosage, common_frequency, common_duration, common_timing, category, usage_count)
SELECT id, 'Pantoprazole', '40mg', '1-0-0', '7 days', 'Before food', 'Antacid', 0 FROM clinics
ON CONFLICT (clinic_id, name) DO NOTHING;

-- Cough & Cold
INSERT INTO medicine_master (clinic_id, name, common_dosage, common_frequency, common_duration, common_timing, category, usage_count)
SELECT id, 'Dextromethorphan', '10ml', '1-1-1', '3 days', 'After food', 'Cough Suppressant', 0 FROM clinics
ON CONFLICT (clinic_id, name) DO NOTHING;

-- Migration completed successfully

