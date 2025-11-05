# 🚀 Deployment Guide - Prescription Feature

## Overview
This guide will help you deploy the new prescription feature to your Vercel + Supabase production environment.

---

## Prerequisites
- ✅ Vercel account with deployed app
- ✅ Supabase PostgreSQL database
- ✅ Git repository connected to Vercel
- ✅ Database connection string (DATABASE_URL)

---

## 🔄 Deployment Steps

### Step 1: Run Database Migration on Supabase

1. **Login to Supabase Dashboard**
   - Go to https://supabase.com/dashboard
   - Select your project

2. **Open SQL Editor**
   - Click on "SQL Editor" in the left sidebar
   - Click "New Query"

3. **Run Migration Script**
   - Copy the contents of `migrations/add_prescription_tables.sql`
   - Paste into the SQL editor
   - Click "Run" or press Cmd/Ctrl + Enter

4. **Verify Tables Created**
   - Go to "Table Editor" in Supabase
   - You should see two new tables:
     - `prescriptions` (with columns: id, clinic_id, patient_id, etc.)
     - `medicines` (with columns: id, prescription_id, name, etc.)

### Step 2: Push Code to GitHub

```bash
cd /Users/rishjain/Downloads/software/doctor

# Stage all changes
git add .

# Commit with descriptive message
git commit -m "Add prescription feature with structured medicine management"

# Push to main branch
git push origin main
```

### Step 3: Verify Vercel Deployment

1. **Check Vercel Dashboard**
   - Vercel will automatically detect the push
   - A new deployment will start
   - Wait for "Ready" status (usually 1-2 minutes)

2. **Check Build Logs**
   - Click on the deployment
   - Check logs for any errors
   - Ensure no missing dependencies

### Step 4: Test Production Application

Visit your production URL: https://clinicmate-psi.vercel.app

Test the following:

1. ✅ **Navigation** - Prescriptions link appears in menu
2. ✅ **Create Prescription** - From patient profile
3. ✅ **Add Medicines** - Dynamic form works
4. ✅ **View Prescription** - Professional format
5. ✅ **Edit Prescription** - Update medicines
6. ✅ **Print Prescription** - Print layout works
7. ✅ **Search** - Search prescriptions

---

## 🔍 Troubleshooting

### Issue: Migration Fails

**Problem**: SQL migration returns an error

**Solution**:
- Check if tables already exist
- Verify foreign key relationships (clinics, patients, consultations tables must exist)
- Check PostgreSQL version compatibility
- Run queries one by one to identify the problematic statement

### Issue: "No such table: prescriptions" Error

**Problem**: Application can't find prescription tables

**Solutions**:
1. Verify migration ran successfully on Supabase
2. Check DATABASE_URL environment variable in Vercel
3. Restart Vercel deployment
4. Check database connection in Supabase

### Issue: Import Error for Prescription/Medicine Models

**Problem**: `ImportError: cannot import name 'Prescription'`

**Solution**:
- Verify `models.py` was pushed correctly
- Check Vercel build logs
- Redeploy from Vercel dashboard

### Issue: 404 on Prescription Routes

**Problem**: `/prescriptions` returns 404

**Solution**:
- Verify `app.py` includes prescription routes
- Check Vercel routing configuration
- Ensure all files were committed and pushed

---

## 🔐 Security Checklist

Before going live:

- [ ] Change SECRET_KEY in production
- [ ] Enable HTTPS (Vercel does this by default)
- [ ] Set up proper database backups in Supabase
- [ ] Configure CORS if needed
- [ ] Review Supabase RLS (Row Level Security) policies
- [ ] Set up monitoring and error logging

---

## 📊 Database Backup (Recommended)

Before running migration:

1. **Backup from Supabase**
   ```bash
   # In Supabase dashboard:
   # Settings → Database → Create backup
   ```

2. **Export Current Data** (optional)
   - Go to Table Editor
   - Export existing tables to CSV
   - Store backup safely

---

## 🔄 Rollback Plan

If something goes wrong:

### Rollback Code
```bash
# Revert to previous commit
git log  # Find previous commit hash
git revert <commit-hash>
git push origin main
```

### Rollback Database
```sql
-- Drop new tables (if needed)
DROP TABLE IF EXISTS medicines CASCADE;
DROP TABLE IF EXISTS prescriptions CASCADE;
DROP FUNCTION IF EXISTS update_prescriptions_updated_at CASCADE;
```

---

## 📈 Post-Deployment Verification

### 1. Database Check
```sql
-- Check tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('prescriptions', 'medicines');

-- Check indexes
SELECT indexname FROM pg_indexes 
WHERE tablename IN ('prescriptions', 'medicines');

-- Test prescription number generation
SELECT * FROM prescriptions LIMIT 1;
```

### 2. Application Check
- ✅ All pages load without errors
- ✅ Navigation menu shows "Prescriptions"
- ✅ Can create a prescription
- ✅ Can add multiple medicines
- ✅ Print layout works correctly
- ✅ Search functionality works
- ✅ Edit/delete operations work

### 3. Performance Check
- ✅ Pages load in < 2 seconds
- ✅ Database queries are indexed
- ✅ No N+1 query problems
- ✅ Print generation is fast

---

## 🎯 Quick Deploy Commands

```bash
# Complete deployment in one go
cd /Users/rishjain/Downloads/software/doctor
git add .
git commit -m "Add prescription feature"
git push origin main

# Then run SQL migration in Supabase dashboard
```

---

## 📞 Support

If you encounter issues:

1. **Check Vercel Logs**
   - Vercel Dashboard → Deployments → Click deployment → Function Logs

2. **Check Supabase Logs**
   - Supabase Dashboard → Logs Explorer

3. **Test Locally First**
   ```bash
   # Set DATABASE_URL to Supabase
   export DATABASE_URL="postgresql://..."
   python app.py
   ```

4. **Review Documentation**
   - See PRESCRIPTION_FEATURE.md for feature details
   - Check Vercel documentation for deployment issues
   - Review Supabase docs for database issues

---

## ✅ Deployment Checklist

- [ ] Database backup created
- [ ] Migration script reviewed
- [ ] Migration executed on Supabase
- [ ] Tables and indexes verified
- [ ] Code committed to git
- [ ] Code pushed to GitHub
- [ ] Vercel deployment successful
- [ ] Production site accessible
- [ ] Prescription menu appears
- [ ] Can create prescription
- [ ] Can view/edit prescription
- [ ] Print works correctly
- [ ] Search works
- [ ] No console errors
- [ ] Mobile responsive
- [ ] Performance acceptable

---

## 🎉 Success!

Once all checks pass, your prescription feature is live! 

**Production URL**: https://clinicmate-psi.vercel.app

Share with your users and gather feedback!

---

*Deployment guide for Prescription Feature v1.0*


