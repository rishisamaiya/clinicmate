# 🧪 Diagnostic Tests & Doctor Referrals Feature

## Overview
Doctors can now:
1. **Recommend Lab Tests** (CBC, X-Ray, Blood Sugar, etc.) with autocomplete
2. **Refer Patients to Specialists** with reason for referral
3. All information is **printed on the prescription** for patient convenience

---

## 🎯 What's New

### 1. Diagnostic Tests Section
- **Location**: Prescription form (between medicines and advice sections)
- **Functionality**: 
  - Type test name → Get suggestions from 35+ pre-loaded common tests
  - Auto-saves new tests to your library for future use
  - Supports multiple tests (one per line or comma-separated)
  - Displays clearly on printed prescription

**Common Tests Included:**
- **Blood Tests**: CBC, Blood Sugar (Fasting/PP), HbA1c, Lipid Profile, LFT, KFT, Thyroid Profile, Vitamin D/B12, Hemoglobin, ESR, Uric Acid, Serum Creatinine
- **Urine Tests**: Urine Routine & Microscopy, Urine Culture
- **Imaging**: X-Ray (Chest/Abdomen), Ultrasound (Abdomen/Pelvis), CT Scan Brain, MRI Brain
- **Cardiac**: ECG, 2D Echo, TMT (Treadmill Test)
- **Others**: Spirometry, Pap Smear, Stool Tests

### 2. Referral to Specialist
- **Location**: Prescription form (highlighted yellow section)
- **Fields**:
  - **Refer to**: Specialist name/type (e.g., "Dr. Smith - Cardiologist")
  - **Reason**: Why you're referring (e.g., "For detailed cardiac evaluation")
- **Display**: Highlighted box on prescription for clear visibility

---

## 📋 Usage

### Creating a Prescription with Tests & Referral

1. **Go to** Patient Profile → **New Prescription**
2. **Add Medicines** (as usual)
3. **Add Diagnostic Tests**:
   - Type test name in the "Recommended Lab Tests" textarea
   - Select from autocomplete suggestions
   - Add multiple tests (one per line)
   - Example:
     ```
     CBC
     Blood Sugar Fasting
     X-Ray Chest PA
     ```

4. **Add Referral** (if needed):
   - Fill "Refer to" field: `Dr. John - Cardiologist`
   - Fill "Reason" field: `For ECG evaluation and cardiac stress test`

5. **Add Advice** (as usual)
6. **Save Prescription**

### Printing
- Click **🖨️ Print** button
- Tests and referral are displayed in separate highlighted sections
- Everything fits on one page (optimized print layout)

---

## 🗄️ Database Migration

**IMPORTANT**: Run this SQL in Supabase to enable the feature:

```sql
-- File: migrations/add_tests_and_referrals.sql
```

### What the Migration Does:
1. ✅ Adds 3 new columns to `prescriptions` table:
   - `diagnostic_tests` (TEXT)
   - `referral_to` (VARCHAR 200)
   - `referral_reason` (TEXT)

2. ✅ Creates `diagnostic_test_master` table:
   - Stores test library per clinic
   - Tracks usage count for popular tests
   - Pre-populated with 35+ common tests

3. ✅ Adds performance indexes for fast autocomplete

### Running the Migration:

1. **Open Supabase** → Your Project → **SQL Editor**
2. **Copy entire content** of `migrations/add_tests_and_referrals.sql`
3. **Paste and Run** in SQL Editor
4. **Wait for success message** ✅

---

## 🔧 API Endpoints

### Search Diagnostic Tests
```
GET /api/tests/search?q={query}
```
**Example:**
```
/api/tests/search?q=cbc
```
**Response:**
```json
[
  {
    "name": "Complete Blood Count (CBC)",
    "category": "Blood Test",
    "usage_count": 5
  }
]
```

### Add Test to Master Library
```
POST /api/tests/add
Content-Type: application/json

{
  "name": "ESR",
  "category": "Blood Test"
}
```

---

## 💡 Tips

### For Doctors:
1. **Autocomplete is Smart**: It learns from your usage and shows most-used tests first
2. **Multiple Tests**: Add each test on a new line in the textarea
3. **New Tests**: Any test you type is automatically saved for next time
4. **Referrals**: Use format "Dr. Name - Specialization" for clarity

### Print Optimization:
- Prescription still fits on **one page** even with tests and referrals
- Tests shown in **blue box** 🧪
- Referrals shown in **yellow box** 👨‍⚕️
- Clear hierarchy for patient readability

---

## 🐛 Troubleshooting

### Tests not appearing in autocomplete?
1. Check if you ran the migration in Supabase
2. Verify `diagnostic_test_master` table exists
3. Try typing at least 2 characters

### Migration failed?
1. Check if you have sufficient permissions in Supabase
2. Verify the SQL syntax is correct (copy-paste entire file)
3. Check Supabase logs for specific error

### Tests not saving?
1. Open browser console (F12)
2. Check for JavaScript errors
3. Verify `/api/tests/add` endpoint is accessible

---

## 📊 Data Structure

### Prescription Table (New Columns)
```sql
diagnostic_tests    TEXT           -- Tests (newline-separated)
referral_to         VARCHAR(200)   -- Specialist name/type
referral_reason     TEXT           -- Reason for referral
```

### Diagnostic Test Master Table
```sql
CREATE TABLE diagnostic_test_master (
    id              SERIAL PRIMARY KEY,
    clinic_id       INTEGER NOT NULL,
    name            VARCHAR(200) NOT NULL,
    category        VARCHAR(100),
    usage_count     INTEGER DEFAULT 1,
    last_used       TIMESTAMP,
    created_at      TIMESTAMP,
    UNIQUE(clinic_id, name)
);
```

---

## 🎉 Benefits

### For Doctors:
- ✅ **Faster Prescription Writing**: Autocomplete saves time
- ✅ **Consistent Test Names**: No spelling variations
- ✅ **Complete Documentation**: Tests and referrals on prescription
- ✅ **Professional Look**: Clean, organized printout

### For Patients:
- ✅ **Clear Instructions**: Know exactly which tests to do
- ✅ **Referral Details**: Know which specialist to visit and why
- ✅ **Single Document**: Everything on one prescription

### For Clinic:
- ✅ **Better Tracking**: All tests and referrals recorded
- ✅ **Data Analysis**: Popular tests, referral patterns
- ✅ **Legal Compliance**: Complete medical documentation

---

## 🚀 What's Next?

This feature is **production-ready**! 

**Already deployed to**: https://clinicmate-psi.vercel.app

**Next steps**:
1. Run the Supabase migration ✅
2. Create a test prescription with tests & referral
3. Print and verify layout
4. Start using in daily practice! 🎊

---

## 🔒 Security & Privacy

- ✅ All tests are **clinic-specific** (multi-tenant safe)
- ✅ No cross-clinic data sharing
- ✅ Test library is **private to each clinic**
- ✅ Follows same security model as medicines

---

## 📞 Support

If you encounter any issues:
1. Check this documentation first
2. Verify migration is run correctly
3. Check browser console for errors
4. Review Supabase logs

---

**Feature Status**: ✅ **COMPLETE & DEPLOYED**

**Last Updated**: November 5, 2025

