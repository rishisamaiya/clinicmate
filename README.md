# 🏥 Clinic Management System - Prototype

A simple, easy-to-use clinic management system for small medical practices.

## ✨ Features

- **Patient Management**: Register and maintain patient records
- **Appointment Scheduling**: Book and manage appointments
- **Consultation Records**: Record vitals, diagnosis, and prescriptions
- **Digital Prescriptions**: Generate printable prescriptions
- **Dashboard**: Quick overview of daily activities
- **Simple Billing**: Track consultation fees and payments

## 🚀 Quick Start

### 1. Setup Virtual Environment

```bash
cd /Users/rishjain/Downloads/software/doctor
python3 -m venv venv
source venv/bin/activate  # On Mac/Linux
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python app.py
```

The application will start at: **http://127.0.0.1:5000**

## 📋 First Time Setup

1. **Register Your Clinic**
   - Go to http://127.0.0.1:5000
   - Click "Register here"
   - Fill in clinic and doctor details
   - Create an account

2. **Login**
   - Use your email and password
   - You'll see the dashboard

3. **Add Patients**
   - Click "Register New Patient"
   - Fill in patient details
   - Save

4. **Book Appointments**
   - From dashboard or appointments page
   - Select patient, date, and time
   - Save appointment

5. **Conduct Consultation**
   - Check-in patient from dashboard
   - Click "Start Consultation"
   - Record vitals and diagnosis
   - Add prescription
   - Save (generates printable prescription)

## 📁 Database

The application uses SQLite database stored at:
`/Users/rishjain/Downloads/software/doctor/instance/clinic.db`

This is a local file-based database - perfect for prototyping and testing.

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML, CSS (No JavaScript frameworks)
- **Authentication**: Session-based

## 📱 Screens

1. **Login/Register** - Clinic registration and authentication
2. **Dashboard** - Daily overview with appointments and stats
3. **Patients** - List, add, and view patient details
4. **Appointments** - Schedule and manage appointments
5. **Consultations** - Record consultation and generate prescription

## 🔐 Security Note

This is a **prototype for local testing only**. For production use:
- Use stronger password hashing (bcrypt)
- Add HTTPS
- Implement proper session management
- Add user roles and permissions
- Deploy to cloud with PostgreSQL

## 🎯 Next Steps

After testing the prototype:
1. Get feedback from doctors
2. Add more features based on needs
3. Improve UI/UX
4. Deploy to cloud (Vercel + Supabase)
5. Add SMS/WhatsApp notifications
6. Integrate with lab systems
7. Add reports and analytics

## 📞 Support

This is a prototype built for testing clinic management workflows.
Customize as needed based on your requirements!

---

**Built with ❤️ for healthcare professionals**

