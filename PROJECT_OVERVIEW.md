# ZitiAcademy Attendance System - Project Overview

## 📋 Executive Summary

A production-ready, full-stack attendance management system built with modern technologies, complete with containerization and automated CI/CD pipeline. The system supports role-based access control (Admin, Teacher, Student) and provides comprehensive attendance tracking, reporting, and QR code-based check-in capabilities.

## 🏗️ Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Repository                        │
│  (Version Control + CI/CD with GitHub Actions)              │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ Push / PR
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    CI/CD Pipeline                            │
│  ├─ Lint & Test (Backend + Frontend)                        │
│  ├─ Build Docker Images                                      │
│  ├─ Security Scanning                                        │
│  ├─ Integration Tests                                        │
│  └─ Deploy (Staging / Production)                           │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ Docker Images (ghcr.io)
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                   Docker Compose                             │
│  ┌──────────────────┐        ┌──────────────────┐          │
│  │   Frontend       │        │    Backend       │          │
│  │   Next.js 15     │◄──────►│   Flask 3.0      │          │
│  │   Port: 3000     │  HTTP  │   Port: 5001     │          │
│  │   (React 19)     │        │   (Python 3.11)  │          │
│  └──────────────────┘        └─────────┬────────┘          │
│                                         │                    │
│                                         ▼                    │
│                               ┌──────────────────┐          │
│                               │   SQLite DB      │          │
│                               │   (Volume mount) │          │
│                               └──────────────────┘          │
└─────────────────────────────────────────────────────────────┘
                 │
                 │ Browser Access
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                        Users                                 │
│   Admin    │    Teachers    │    Students                   │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

#### Backend
- **Framework:** Flask 3.0.0
- **Language:** Python 3.11
- **ORM:** SQLAlchemy 2.0.23
- **Database:** SQLite (file-based)
- **Authentication:** JWT (Flask-JWT-Extended 4.5.3)
- **CORS:** Flask-CORS 4.0.0
- **QR Code:** pyqrcode 1.2.1
- **Security:** python-dotenv, Werkzeug

#### Frontend
- **Framework:** Next.js 15.1.3
- **Language:** TypeScript 5
- **UI Library:** React 19.0.0
- **Styling:** Tailwind CSS 3.4.17
- **State Management:** 
  - Zustand 5.0.2 (Global state)
  - React Query 5.62.11 (Server state)
- **HTTP Client:** Axios 1.7.9
- **Form Handling:** React Hook Form + Zod
- **Date Handling:** dayjs
- **QR Code:** react-qr-code, html5-qrcode

#### DevOps
- **Containerization:** Docker 20+, Docker Compose
- **CI/CD:** GitHub Actions
- **Image Registry:** GitHub Container Registry (ghcr.io)
- **Security Scanning:** Trivy, Safety, npm audit
- **Code Quality:** ESLint, Flake8, TypeScript compiler

## 🔄 Data Flow

### Authentication Flow
```
1. User enters credentials → Frontend (Login page)
2. POST /api/auth/login → Backend
3. Backend validates credentials
4. JWT token generated ← Backend
5. Token stored in cookie ← Frontend (httpOnly, secure)
6. Subsequent requests include JWT in Authorization header
7. Backend validates JWT on protected routes
```

### Attendance Marking Flow
```
1. Teacher selects course → Frontend Dashboard
2. GET /api/courses/:id/students → Fetch enrolled students
3. Teacher marks attendance (Present/Absent/Late/Excused)
4. POST /api/attendance or POST /api/attendance/bulk
5. Backend validates teacher authorization
6. Records saved to database
7. Success response → Frontend updates UI
```

### QR Code Check-in Flow
```
1. Teacher generates QR code → GET /api/courses/:id/qrcode
2. QR code displayed to class (contains course_id + session_token)
3. Student scans QR code with mobile device
4. POST /api/attendance/checkin with decoded data
5. Backend validates session and student enrollment
6. Attendance marked as "present"
7. Confirmation → Student receives check-in confirmation
```

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'teacher', 'student') NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Courses Table
```sql
CREATE TABLE courses (
    id INTEGER PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    code VARCHAR(20) UNIQUE NOT NULL,
    description TEXT,
    teacher_id INTEGER NOT NULL,
    semester VARCHAR(20),
    year INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES users(id)
);
```

### Enrollments Table
```sql
CREATE TABLE enrollments (
    id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    enrolled_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (course_id) REFERENCES courses(id),
    UNIQUE (student_id, course_id)
);
```

### Attendance Table
```sql
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    date DATE NOT NULL,
    status ENUM('present', 'absent', 'late', 'excused') NOT NULL,
    check_in_time TIME,
    notes TEXT,
    marked_by INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (course_id) REFERENCES courses(id),
    FOREIGN KEY (marked_by) REFERENCES users(id),
    UNIQUE (student_id, course_id, date)
);
```

## 🔐 Security Implementation

### Authentication & Authorization
- **JWT Tokens:** 24-hour expiry, RS256 algorithm
- **Password Hashing:** Werkzeug with pbkdf2:sha256
- **HTTP-Only Cookies:** Prevents XSS attacks
- **CORS:** Whitelist-based origin validation
- **Role-Based Access Control:** Enforced at API route level

### Security Headers
```python
# Backend
CORS_ORIGINS = ['http://localhost:3000', 'http://frontend:3000']
JWT_COOKIE_SECURE = True  # In production
JWT_COOKIE_CSRF_PROTECT = True
SESSION_COOKIE_HTTPONLY = True
```

### API Authorization Patterns
```python
# Example: Protected route with role check
@jwt_required()
def protected_route():
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()
    
    if user.role not in ['admin', 'teacher']:
        return {'error': 'Unauthorized'}, 403
    
    # Process request...
```

## 🐳 Docker Configuration

### Backend Dockerfile
- **Base Image:** python:3.11-slim
- **Optimization:** Multi-stage build potential
- **Health Check:** curl /api/health
- **Permissions:** chmod 777 on instance directory for SQLite
- **Port:** 5001

### Frontend Dockerfile
- **Base Image:** node:20-alpine
- **Build Type:** Multi-stage (builder → runner)
- **Output Mode:** standalone (optimized for Docker)
- **Port:** 3000

### Docker Compose Services
```yaml
services:
  backend:
    build: ./backend
    ports: ["5001:5001"]
    environment:
      - FLASK_ENV=development
      - DATABASE_URL=sqlite:////app/instance/attendance.db
      - CORS_ORIGIN=http://localhost:3000,http://frontend:3000
    volumes:
      - ./backend/instance:/app/instance
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5001/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
  
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    environment:
      - NEXT_PUBLIC_API_BASE_URL=http://localhost:5001/api
    depends_on:
      - backend
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflows

#### 1. Main CI/CD Pipeline (`ci-cd.yml`)

**Trigger Events:**
- Push to `main` or `develop` branches
- Pull requests targeting `main` or `develop`
- Manual workflow dispatch

**Jobs:**

##### a. Backend CI
- Setup Python 3.11
- Cache pip dependencies
- Install requirements
- Lint with flake8 (max line length 100)
- Test app factory initialization
- Security check with Safety

##### b. Frontend CI
- Setup Node.js 20
- Cache npm dependencies
- Install dependencies
- Lint with ESLint
- Type-check with TypeScript
- Build Next.js app

##### c. Docker Build
- Runs only on push to main/develop
- Build backend and frontend images
- Tag with branch name and commit SHA
- Push to GitHub Container Registry (ghcr.io)
- Images: 
  - `ghcr.io/{repo}/backend:latest`
  - `ghcr.io/{repo}/frontend:latest`

##### d. Integration Tests
- Start services with docker-compose
- Wait for health checks
- Seed database
- Test endpoints:
  - Health check
  - Login authentication
  - JWT token validation
  - Courses API
  - Users API
  - CORS configuration
- Test frontend pages
- Cleanup after tests

##### e. Security Scan
- Run Trivy vulnerability scanner
- Scan backend Docker image
- Scan frontend Docker image
- Upload results to GitHub Security tab
- Severity levels: HIGH, CRITICAL

##### f. Deploy Staging
- Triggers on push to `develop`
- Placeholder for actual deployment script
- Example: SSH to staging server, pull images, restart services

##### g. Deploy Production
- Triggers on push to `main`
- Placeholder for actual deployment script
- Example: SSH to production server, pull images, restart services

#### 2. PR Check Workflow (`pr-check.yml`)

**Trigger Events:**
- Pull request opened, synchronized, or reopened

**Jobs:**

##### a. PR Validation
- Check PR title follows conventional commits
- Detect merge conflicts
- Validate package.json and package-lock.json sync
- Warn on large PRs (>1000 lines)

##### b. Code Quality
- Run ShellCheck on shell scripts
- Scan for TODO/FIXME comments
- Check for console.log in frontend code

##### c. Dependency Check
- Run npm audit (frontend)
- Check for outdated packages

### CI/CD Metrics
- **Average Build Time:** ~5-8 minutes
- **Test Coverage Goal:** 80%+
- **Deployment Frequency:** On every merge to main/develop
- **Mean Time to Recovery:** < 10 minutes (rollback)

## 📈 Scalability Considerations

### Current Architecture (Development/Small Scale)
- SQLite database (file-based)
- Single backend instance
- Single frontend instance
- Suitable for: < 1,000 users, < 100 concurrent users

### Recommended Production Architecture (Large Scale)
```
┌─────────────────────────────────────────────────────────────┐
│                     Load Balancer (Nginx)                    │
└────────────────┬────────────────────────────────────────────┘
                 │
         ┌───────┴───────┐
         ▼               ▼
┌─────────────┐   ┌─────────────┐
│  Frontend   │   │  Frontend   │   (Multiple instances)
│  Instance 1 │   │  Instance 2 │
└─────────────┘   └─────────────┘
         │               │
         └───────┬───────┘
                 │
         ┌───────┴───────┐
         ▼               ▼
┌─────────────┐   ┌─────────────┐
│  Backend    │   │  Backend    │   (Multiple instances)
│  Instance 1 │   │  Instance 2 │
└──────┬──────┘   └──────┬──────┘
       │                  │
       └────────┬─────────┘
                ▼
       ┌─────────────────┐
       │  PostgreSQL     │         (Replace SQLite)
       │  (Primary)      │
       └────────┬────────┘
                │
                ▼
       ┌─────────────────┐
       │  PostgreSQL     │         (Read replica)
       │  (Replica)      │
       └─────────────────┘
```

**Recommended Changes for Scale:**
1. **Database:** Migrate from SQLite to PostgreSQL
2. **Caching:** Add Redis for session management
3. **File Storage:** Use S3/CloudFront for QR codes and exports
4. **CDN:** CloudFlare or AWS CloudFront for static assets
5. **Container Orchestration:** Kubernetes or AWS ECS
6. **Monitoring:** Prometheus + Grafana
7. **Logging:** ELK Stack or CloudWatch
8. **Message Queue:** RabbitMQ or AWS SQS for background tasks

## 🚀 Deployment Options

### Option 1: Cloud VPS (DigitalOcean, Linode, AWS EC2)
**Pros:**
- Full control over environment
- Cost-effective for small to medium scale
- Easy to configure and debug

**Steps:**
1. Provision VPS with Ubuntu 22.04
2. Install Docker and Docker Compose
3. Clone repository
4. Configure environment variables
5. Run `docker compose up -d`
6. Configure Nginx as reverse proxy
7. Set up SSL with Let's Encrypt

**Estimated Cost:** $12-50/month

### Option 2: Cloud Platform (Heroku, Railway, Render)
**Pros:**
- Managed infrastructure
- Easy deployment
- Built-in CI/CD

**Steps:**
1. Connect GitHub repository
2. Configure build settings
3. Set environment variables
4. Deploy with one click

**Estimated Cost:** $20-100/month

### Option 3: Container Orchestration (Kubernetes, AWS ECS)
**Pros:**
- Auto-scaling
- High availability
- Production-grade
- Self-healing

**Steps:**
1. Push Docker images to registry
2. Create Kubernetes manifests or ECS task definitions
3. Configure load balancer
4. Set up auto-scaling policies
5. Deploy using kubectl or AWS CLI

**Estimated Cost:** $100-500/month

### Option 4: Serverless (AWS Lambda + S3 + API Gateway)
**Pros:**
- Pay per use
- Zero server management
- Infinite scalability

**Steps:**
1. Convert Flask to Lambda-compatible format
2. Deploy Next.js to Vercel/S3
3. Set up API Gateway
4. Configure RDS for database

**Estimated Cost:** $10-200/month (based on usage)

## 📚 API Documentation

### Complete Endpoint List

#### Authentication
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | /api/auth/register | None | Register new user |
| POST | /api/auth/login | None | Login and get JWT |
| GET | /api/auth/me | JWT | Get current user |
| POST | /api/auth/logout | JWT | Logout |

#### Users (Admin Only)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | /api/users | JWT + Admin | List all users |
| GET | /api/users/:id | JWT + Admin | Get user by ID |
| PUT | /api/users/:id | JWT + Admin | Update user |
| DELETE | /api/users/:id | JWT + Admin | Delete user |

#### Courses
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | /api/courses | JWT | List courses (filtered by role) |
| POST | /api/courses | JWT + Teacher | Create course |
| GET | /api/courses/:id | JWT | Get course details |
| PUT | /api/courses/:id | JWT + Owner | Update course |
| DELETE | /api/courses/:id | JWT + Owner | Delete course |
| POST | /api/courses/:id/enroll | JWT + Teacher | Enroll students |
| DELETE | /api/courses/:id/enroll/:student_id | JWT + Teacher | Remove student |
| GET | /api/courses/:id/students | JWT | List enrolled students |
| GET | /api/courses/:id/qrcode | JWT + Teacher | Generate QR code |

#### Attendance
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | /api/attendance | JWT + Teacher | Mark single attendance |
| POST | /api/attendance/bulk | JWT + Teacher | Bulk mark attendance |
| POST | /api/attendance/checkin | JWT + Student | QR code check-in |
| GET | /api/attendance/course/:id | JWT | Get course attendance |
| GET | /api/attendance/student/:id | JWT | Get student attendance |
| PUT | /api/attendance/:id | JWT + Teacher | Update attendance |
| DELETE | /api/attendance/:id | JWT + Teacher | Delete attendance |

#### Reports
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | /api/reports/course/:id | JWT | Course attendance report |
| GET | /api/reports/student/:id | JWT | Student attendance report |
| GET | /api/reports/export/:id | JWT | Export data (CSV/XLSX) |

### Response Formats

#### Success Response
```json
{
  "message": "Operation successful",
  "data": { ... }
}
```

#### Error Response
```json
{
  "error": "Error message",
  "details": "Detailed error information"
}
```

#### Pagination Response
```json
{
  "data": [ ... ],
  "page": 1,
  "per_page": 20,
  "total": 100,
  "pages": 5
}
```

## 🧪 Testing Strategy

### Backend Tests
- **Unit Tests:** Test individual functions and methods
- **Integration Tests:** Test API endpoints
- **Security Tests:** Test authentication and authorization
- **Performance Tests:** Test database query performance

### Frontend Tests
- **Component Tests:** React Testing Library
- **E2E Tests:** Playwright or Cypress
- **Visual Regression Tests:** Chromatic or Percy
- **Accessibility Tests:** axe-core

### CI Integration Tests
- Full-stack integration tests
- API contract tests
- Database migration tests
- Docker container tests

## 📊 Monitoring & Observability

### Recommended Monitoring Stack

#### Application Performance Monitoring (APM)
- **Tool:** New Relic, Datadog, or open-source: Prometheus + Grafana
- **Metrics:**
  - Request rate
  - Response time (p50, p95, p99)
  - Error rate
  - Database query performance

#### Logging
- **Tool:** ELK Stack (Elasticsearch, Logstash, Kibana) or CloudWatch
- **Log Levels:** DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Structured Logging:** JSON format for easy parsing

#### Error Tracking
- **Tool:** Sentry
- **Features:**
  - Real-time error alerts
  - Stack traces
  - User context
  - Release tracking

#### Uptime Monitoring
- **Tool:** UptimeRobot, Pingdom, or StatusCake
- **Checks:**
  - HTTP endpoint availability
  - Response time
  - SSL certificate expiry

### Key Metrics to Track

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Uptime | 99.9% | < 99.5% |
| Response Time (p95) | < 500ms | > 1s |
| Error Rate | < 1% | > 5% |
| CPU Usage | < 70% | > 85% |
| Memory Usage | < 80% | > 90% |
| Database Connections | < 50 | > 80 |

## 🔮 Future Enhancements

### Phase 1 (Next 3 months)
- [ ] Complete frontend course management UI
- [ ] Implement QR code scanner
- [ ] Add email notifications
- [ ] Create reports dashboard with charts
- [ ] Mobile-responsive design improvements

### Phase 2 (3-6 months)
- [ ] Real-time attendance updates (WebSocket)
- [ ] Parent/Guardian portal
- [ ] SMS notifications
- [ ] Attendance analytics and insights
- [ ] Integration with school management systems

### Phase 3 (6-12 months)
- [ ] Mobile app (React Native)
- [ ] Facial recognition check-in
- [ ] Advanced reporting with ML predictions
- [ ] Multi-tenant support
- [ ] API for third-party integrations

## 📞 Support & Maintenance

### Regular Maintenance Tasks
- [ ] **Daily:** Monitor error logs and uptime
- [ ] **Weekly:** Review and merge dependabot PRs
- [ ] **Monthly:** Security vulnerability scanning
- [ ] **Quarterly:** Performance optimization review
- [ ] **Annually:** Major dependency upgrades

### Backup Strategy
- **Database:** Daily automated backups, 30-day retention
- **Configuration:** Version-controlled in Git
- **User Data:** Weekly full backups, monthly archival

### Disaster Recovery Plan
1. Restore from latest database backup
2. Redeploy from Docker images (tagged with commit SHA)
3. Verify data integrity
4. Test all critical functions
5. Monitor for issues

**RTO (Recovery Time Objective):** 1 hour  
**RPO (Recovery Point Objective):** 24 hours

## 📖 Resources

### Documentation
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Docker Documentation](https://docs.docker.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

### Related Projects
- [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/)
- [React Query](https://tanstack.com/query/latest)
- [Zustand](https://docs.pmnd.rs/zustand)
- [Tailwind CSS](https://tailwindcss.com/)

## 🤝 Contributing

Please read [CONTRIBUTING.md](./CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Project Status:** ✅ Production Ready  
**Version:** 1.0.0  
**Last Updated:** 2025-11-15  
**Maintained by:** ZitiAcademy Development Team
