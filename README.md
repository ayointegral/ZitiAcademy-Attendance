# ZitiAcademy Course Attendance System

![CI/CD Pipeline](https://github.com/ayointegral/ZitiAcademy-Attendance/workflows/CI%2FCD%20Pipeline/badge.svg)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A full-stack web application for managing course attendance with role-based access control, QR code check-in, and comprehensive reporting. Fully containerized with Docker and automated CI/CD pipeline.

## Tech Stack

### Backend
- **Framework:** Flask 3.0 (Python)
- **Database:** SQLite (file-based)
- **Authentication:** JWT (Flask-JWT-Extended)
- **API:** RESTful with JSON responses

### Frontend
- **Framework:** Next.js 15 (React 19, TypeScript)
- **Styling:** Tailwind CSS
- **State Management:** Zustand + React Query
- **Forms:** React Hook Form + Zod validation

## Features

### Role-Based Access Control
- **Admin:** Manage users, courses, and view all reports
- **Teacher:** Create courses, manage rosters, take attendance, view course reports
- **Student:** View enrolled courses, check attendance history, QR code check-in

### Core Features
- User management (register, login, profile)
- Course management (CRUD operations)
- Student enrollment management
- Attendance tracking (mark present/absent/late/excused)
- Bulk attendance marking
- QR code-based check-in- Comprehensive reports with statistics
- Data export (CSV/XLSX)

## Directory Structure

```
Attendance/
├── backend/                    # Flask API server
│   ├── app/
│   │   ├── __init__.py        # App factory
│   │   ├── config.py          # Configuration
│   │   ├── models.py          # Database models
│   │   ├── routes/            # API endpoints
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── courses.py
│   │   │   ├── attendance.py
│   │   │   └── reports.py
│   │   └── utils/             # Helper functions
│   ├── .venv/                 # Python virtual environment
│   ├── .env                   # Environment variables
│   ├── requirements.txt       # Python dependencies
│   ├── run.py                 # App entry point
│   └── seed.py                # Database seeding script
├── frontend/                   # Next.js app
│   ├── src/
│   │   ├── app/               # App router pages
│   │   ├── components/        # Reusable components
│   │   └── lib/               # Utilities & config
│   ├── .env.local             # Frontend environment
│   └── package.json
└── README.md
```
## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Start all services
docker compose up

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:5001
```

**Default credentials:**
- Admin: `admin@zitiacademy.com` / `admin123`
- Teacher: `teacher@zitiacademy.com` / `teacher123`
- Student: `student1@zitiacademy.com` / `student123`

For detailed Docker setup, see [DOCKER_SETUP.md](./DOCKER_SETUP.md)

### CI/CD Pipeline

This project includes a complete GitHub Actions CI/CD pipeline:

- ✅ Automated testing (backend & frontend)
- ✅ Code linting and security scanning
- ✅ Docker image building and pushing
- ✅ Integration tests
- ✅ Automated deployment (staging & production)

**Get started:**
```bash
git init
git add .
git commit -m "feat: initial commit"
git remote add origin https://github.com/YOUR_USERNAME/ZitiAcademy-Attendance.git
git push -u origin main
```

For detailed CI/CD setup, see [CICD_QUICKSTART.md](./CICD_QUICKSTART.md)

---

## 📖 Documentation

- **[CICD_QUICKSTART.md](./CICD_QUICKSTART.md)** - Quick CI/CD setup (5 minutes)
- **[CICD_GUIDE.md](./CICD_GUIDE.md)** - Complete CI/CD documentation
- **[DOCKER_SETUP.md](./DOCKER_SETUP.md)** - Docker setup and configuration
- **[DEPLOYMENT_SUCCESS.md](./DEPLOYMENT_SUCCESS.md)** - Deployment guide
- **[FULLSTACK_SETUP.md](./FULLSTACK_SETUP.md)** - Full-stack setup details

---

## 📦 Manual Setup (Alternative)

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Activate virtual environment**
   ```bash
   source .venv/bin/activate
   ```

3. **Install dependencies** (already done during build)
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Edit `backend/.env` and update the secret keys for production:
   ```env
   SECRET_KEY=your-secret-key-here
   JWT_SECRET_KEY=your-jwt-secret-here
   ```

5. **Initialize database with sample data**
   ```bash
   python seed.py
   ```

   This creates:
   - 1 Admin: `admin@zitiacademy.com` / `admin123`
   - 1 Teacher: `teacher@zitiacademy.com` / `teacher123`
   - 10 Students: `student1@zitiacademy.com` to `student10@zitiacademy.com` / `student123`
   - 2 Courses with enrollment and 10 days of attendance data

6. **Run the Flask server**
   ```bash
   python run.py
   ```
   
   Server runs on `http://localhost:5000`
### Frontend Setup

1. **Initialize Next.js app** (if not done yet)
   ```bash
   npx create-next-app@latest frontend --ts --eslint --tailwind --app --src-dir --use-npm
   ```

2. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

3. **Install dependencies**
   ```bash
   npm install @tanstack/react-query axios zustand zod react-hook-form jwt-decode dayjs recharts react-qr-code html5-qrcode classnames
   npm install @headlessui/react @heroicons/react
   ```

4. **Configure environment**
   Create `frontend/.env.local`:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:5000/api
   ```

5. **Run the development server**
   ```bash
   npm run dev
   ```
   
   App runs on `http://localhost:3000`

## API Endpoints

### Authentication (`/api/auth`)
- `POST /register` - Register new user
- `POST /login` - Login and get JWT token
- `GET /me` - Get current user
- `POST /logout` - Logout

### Users (`/api/users`) - Admin only
- `GET /` - List all users (with filters)
- `GET /:id` - Get user by ID
- `PUT /:id` - Update user
- `DELETE /:id` - Delete user
### Courses (`/api/courses`)
- `GET /` - List courses (filtered by role)
- `POST /` - Create course (Teacher/Admin)
- `GET /:id` - Get course details
- `PUT /:id` - Update course
- `DELETE /:id` - Delete course
- `POST /:id/enroll` - Enroll students
- `DELETE /:id/enroll/:student_id` - Remove student
- `GET /:id/students` - List enrolled students
- `GET /:id/qrcode` - Generate QR code for check-in

### Attendance (`/api/attendance`)
- `POST /` - Mark attendance
- `POST /bulk` - Bulk mark attendance
- `POST /checkin` - QR code check-in
- `GET /course/:course_id` - Get course attendance
- `GET /student/:student_id` - Get student attendance
- `PUT /:id` - Update attendance
- `DELETE /:id` - Delete attendance

### Reports (`/api/reports`)
- `GET /course/:course_id` - Course attendance report
- `GET /student/:student_id` - Student attendance report
- `GET /export/:course_id?format=csv|xlsx` - Export attendance data

## Database Models

### User
- `id`, `username`, `email`, `password_hash`, `role` (admin|teacher|student), `created_at`

### Course
- `id`, `name`, `code`, `description`, `teacher_id`, `semester`, `year`, `created_at`

### Enrollment
- `id`, `student_id`, `course_id`, `enrolled_at`

### Attendance
- `id`, `student_id`, `course_id`, `date`, `status` (present|absent|late|excused)
- `check_in_time`, `notes`, `marked_by`, `created_at`
## Development Status

### ✅ Completed
- ✅ Backend Flask API with all routes
- ✅ Database models with SQLAlchemy
- ✅ JWT authentication & authorization
- ✅ Role-based access control
- ✅ QR code generation for check-in
- ✅ Attendance CRUD operations
- ✅ Report generation with CSV/XLSX export
- ✅ Frontend Next.js application with TypeScript
- ✅ Protected routes and authentication flow
- ✅ Dashboard and login pages
- ✅ API integration with React Query
- ✅ State management with Zustand
- ✅ Complete Docker containerization
- ✅ Docker Compose orchestration
- ✅ GitHub Actions CI/CD pipeline
- ✅ Integration tests
- ✅ Security scanning
- ✅ Database seed script with sample data

### 🚧 In Progress / Future Enhancements
- Course management UI
- Attendance tracking interface
- QR code scanner for students
- Reports and analytics dashboard
- Email notifications
- Real-time attendance updates
- Mobile app support

## 🧪 Quick Test

```bash
# Make sure services are running
docker compose up

# Test backend health
curl http://localhost:5001/api/health

# Test authentication
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@zitiacademy.com","password":"admin123"}'

# Get courses (replace TOKEN with token from login)
curl http://localhost:5001/api/courses \
  -H "Authorization: Bearer TOKEN"

# Or simply visit:
# http://localhost:3000 (Frontend)
# http://localhost:5001/api/health (Backend health check)
```

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License - feel free to use this project for educational purposes.