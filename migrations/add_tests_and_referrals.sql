-- Migration: Add Diagnostic Tests and Doctor Referrals to Prescriptions
-- Run this in Supabase SQL Editor after pushing code changes
-- Date: 2025-11-04

-- ============================================================================
-- STEP 1: Add new columns to prescriptions table
-- ============================================================================

-- Add diagnostic tests column
ALTER TABLE prescriptions 
ADD COLUMN IF NOT EXISTS diagnostic_tests TEXT;

-- Add referral columns
ALTER TABLE prescriptions 
ADD COLUMN IF NOT EXISTS referral_to VARCHAR(200);

ALTER TABLE prescriptions 
ADD COLUMN IF NOT EXISTS referral_reason TEXT;

COMMENT ON COLUMN prescriptions.diagnostic_tests IS 'Recommended lab tests (newline-separated list)';
COMMENT ON COLUMN prescriptions.referral_to IS 'Specialist name/type to refer to (e.g., "Dr. XYZ - Cardiologist")';
COMMENT ON COLUMN prescriptions.referral_reason IS 'Reason for referring to specialist';


-- ============================================================================
-- STEP 2: Create diagnostic_test_master table for autocomplete
-- ============================================================================

CREATE TABLE IF NOT EXISTS diagnostic_test_master (
    id SERIAL PRIMARY KEY,
    clinic_id INTEGER NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    
    -- Test details
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100),
    
    -- Usage tracking
    usage_count INTEGER DEFAULT 1,
    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Unique constraint
    CONSTRAINT unique_test_per_clinic UNIQUE (clinic_id, name)
);

-- Add index for faster autocomplete searches
CREATE INDEX IF NOT EXISTS idx_diagnostic_test_clinic ON diagnostic_test_master(clinic_id);
CREATE INDEX IF NOT EXISTS idx_diagnostic_test_name ON diagnostic_test_master(name);
CREATE INDEX IF NOT EXISTS idx_diagnostic_test_usage ON diagnostic_test_master(clinic_id, usage_count DESC);


-- ============================================================================
-- STEP 3: Pre-populate common diagnostic tests for all clinics
-- ============================================================================

-- Blood Tests
INSERT INTO diagnostic_test_master (clinic_id, name, category, usage_count)
SELECT id, 'Complete Blood Count (CBC)', 'Blood Test', 0
FROM clinics
ON CONFLICT (clinic_id, name) DO NOTHING;

INSERT INTO diagnostic_test_master (clinic_id, name, category, usage_count)
SELECT id, 'Blood Sugar Fasting', 'Blood Test', 0
FROM clinics
ON CONFLICT (clinic_id, name) DO NOTHING;

INSERT INTO diagnostic_test_master (clinic_id, name, category, usage_count)
SELECT id, 'Blood Sugar PP (Post Prandial)', 'Blood Test', 0
FROM clinics
ON CONFLICT (clinic_id, name) DO NOTHING;

INSERT INTO diagnostic_test_master (clinic_id, name, category, usage_count)
SELECT id, 'HbA1c (Glycated Hemoglobin)', 'Blood Test', 0
FROM clinics
ON CONFLICT (clinic_id, name) DO NOTHING;

INSERT INTO diagnostic_test_master (clinic_id, name, category, usage_count)
SELECT id, 'Lipid Profile', 'Blood Test', 0
FROM clinics
ON CONFLICT (clinic_id, name) DO NOTHING;

INSERT INTO diagnostic_test_master (clinic_id, name, category, usage_count)
SELECT id, 'Liver Function Test (LFT)', 'Blood Test', 0
FROM clinics
ON CONFLICT (clinic_id, name) DO NOTHING;

INSERT INTO diagnostic_test_master (clinic_id, name, category, usage_count)
SELECT id, 'Kidney Function Test (KFT)', 'Blood Test', 0
FROM clinics
ON CONFLICT (clinic_id, name) DO NOTHING;

INSERT INTO diagnostic_test_master (clinic_id, name, category, usage_count)
SELECT id, 'Thyroid Profile (T3, T4, TSH)', 'Blood Test', 0
FROM clinics
ON CONFLICT (clinic_id, name) DO NOTHING;

INSERT INTO diagnostic_test_master (clinic_id, name, category, usage_count)
SELECT id, 'Vitamin D', 'Blood Test', 0
FROM clinics
ON CONFLICT (clinic_id, name) DO NOTHING;

INSERT INTO diagnostic_test_master (clinic_id, name, category, usage_count)
SELECT id, 'Vitamin B12', 'Blood Test', 0
FROM clinics
ON CONFLICT (clinic_id, name) DO NOTHING;

INSERT INTO diagnostic_test_master (clinic_id, name, category, usage_count)
SELECT id, 'Hemoglobin', 'Blood Test', 0
FROM clinics
ON CONFLICT (clinic_id, name) DO NOTHING;

INSERT INTO diagnostic_test_master (clinic_id, name, category, usage_count)
SELECT id, 'ESR (Erythrocyte Sedimentation Rate)', 'Blood Test', 0
FROM clinics
ON CONFLICT (clinic_id, name) DO NOTHING;

INSERT INTO diagnostic_test_master (clinic_id, name, category, usage_count)
SELECT id, 'Uric Acid', 'Blood Test', 0
FROM clinics
ON CONFLICT (clinic_id, name) DO NOTHING;

INSERT INTO diagnostic_test_master (clinic_id, name, category, usage_count)
SELECT id, 'Serum Creatinine', 'Blood Test', 0
FROM clinics
ON CONFLICT (clinic_id, name) DO NOTHING;

-- Urine Tests
INSERT INTO diagnostic_test_master (clinic_id, name, category, usage_count)
SELECT id, 'Urine Routine & Microscopy', 'Urine Test', 0
FROM clinics
ON CONFLICT (clinic_id, name) DO NOTHING;

INSERT INTO diagnostic_test_master (clinic_id, name, category, usage_count)
SELECT id, 'Urine Culture', 'Urine Test', 0
FROM clinics
ON CONFLICT (clinic_id, name) DO NOTHING;

-- Imaging Tests
INSERT INTO diagnostic_test_master (clinic_id, name, category, usage_count)
SELECT id, 'X-Ray Chest PA', 'Imaging', 0
FROM clinics
ON CONFLICT (clinic_id, name) DO NOTHING;

INSERT INTO diagnostic_test_master (clinic_id, name, category, usage_count)
SELECT id, 'X-Ray Abdomen', 'Imaging', 0
FROM clinics
ON CONFLICT (clinic_id, name) DO NOTHING;

INSERT INTO diagnostic_test_master (clinic_id, name, category, usage_count)
SELECT id, 'Ultrasound Abdomen', 'Imaging', 0
FROM clinics
ON CONFLICT (clinic_id, name) DO NOTHING;

INSERT INTO diagnostic_test_master (clinic_id, name, category, usage_count)
SELECT id, 'Ultrasound Pelvis', 'Imaging', 0
FROM clinics
ON CONFLICT (clinic_id, name) DO NOTHING;

INSERT INTO diagnostic_test_master (clinic_id, name, category, usage_count)
SELECT id, 'CT Scan Brain', 'Imaging', 0
FROM clinics
ON CONFLICT (clinic_id, name) DO NOTHING;

INSERT INTO diagnostic_test_master (clinic_id, name, category, usage_count)
SELECT id, 'MRI Brain', 'Imaging', 0
FROM clinics
ON CONFLICT (clinic_id, name) DO NOTHING;

INSERT INTO diagnostic_test_master (clinic_id, name, category, usage_count)
SELECT id, 'ECG (Electrocardiogram)', 'Cardiac', 0
FROM clinics
ON CONFLICT (clinic_id, name) DO NOTHING;

INSERT INTO diagnostic_test_master (clinic_id, name, category, usage_count)
SELECT id, 'Echo (2D Echo)', 'Cardiac', 0
FROM clinics
ON CONFLICT (clinic_id, name) DO NOTHING;

INSERT INTO diagnostic_test_master (clinic_id, name, category, usage_count)
SELECT id, 'TMT (Treadmill Test)', 'Cardiac', 0
FROM clinics
ON CONFLICT (clinic_id, name) DO NOTHING;

-- Stool Tests
INSERT INTO diagnostic_test_master (clinic_id, name, category, usage_count)
SELECT id, 'Stool Routine & Microscopy', 'Stool Test', 0
FROM clinics
ON CONFLICT (clinic_id, name) DO NOTHING;

INSERT INTO diagnostic_test_master (clinic_id, name, category, usage_count)
SELECT id, 'Stool Culture', 'Stool Test', 0
FROM clinics
ON CONFLICT (clinic_id, name) DO NOTHING;

-- Other Tests
INSERT INTO diagnostic_test_master (clinic_id, name, category, usage_count)
SELECT id, 'Pap Smear', 'Gynecology', 0
FROM clinics
ON CONFLICT (clinic_id, name) DO NOTHING;

INSERT INTO diagnostic_test_master (clinic_id, name, category, usage_count)
SELECT id, 'Spirometry (Lung Function Test)', 'Respiratory', 0
FROM clinics
ON CONFLICT (clinic_id, name) DO NOTHING;


-- ============================================================================
-- VERIFICATION: Check if everything is set up correctly
-- ============================================================================

-- Check new columns exist
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'prescriptions' 
  AND column_name IN ('diagnostic_tests', 'referral_to', 'referral_reason');

-- Count diagnostic tests added per clinic
SELECT clinic_id, COUNT(*) as test_count
FROM diagnostic_test_master
GROUP BY clinic_id
ORDER BY clinic_id;

-- Show sample diagnostic tests
SELECT name, category 
FROM diagnostic_test_master 
WHERE clinic_id = (SELECT MIN(id) FROM clinics)
ORDER BY category, name
LIMIT 10;

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Migration completed successfully!';
    RAISE NOTICE '📋 Added columns: diagnostic_tests, referral_to, referral_reason';
    RAISE NOTICE '🧪 Created diagnostic_test_master table';
    RAISE NOTICE '📊 Pre-populated % common diagnostic tests', 
        (SELECT COUNT(DISTINCT name) FROM diagnostic_test_master);
END $$;

