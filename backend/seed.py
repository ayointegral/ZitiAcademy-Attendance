"""Seed database with sample data for development"""
from app import create_app
from app.models import db, User, Course, Enrollment, Attendance
from datetime import date, timedelta
import random

app = create_app()

with app.app_context():
    # Clear existing data (optional)
    print("Clearing existing data...")
    Attendance.query.delete()
    Enrollment.query.delete()
    Course.query.delete()
    User.query.delete()
    db.session.commit()
    
    # Create admin
    print("Creating admin user...")
    admin = User(username='admin', email='admin@zitiacademy.com', role='admin')
    admin.set_password('admin123')
    db.session.add(admin)
    
    # Create teacher
    print("Creating teacher...")
    teacher = User(username='teacher1', email='teacher@zitiacademy.com', role='teacher')
    teacher.set_password('teacher123')
    db.session.add(teacher)
    
    # Create students
    print("Creating students...")
    students = []
    for i in range(1, 11):
        student = User(
            username=f'student{i}',
            email=f'student{i}@zitiacademy.com',
            role='student'
        )
        student.set_password('student123')
        students.append(student)
        db.session.add(student)
    
    db.session.commit()
    
    # Create courses
    print("Creating courses...")
    course1 = Course(
        name='Introduction to Python',
        code='CS101',
        description='Learn Python programming fundamentals',
        teacher_id=teacher.id,
        semester='Fall',
        year=2024
    )
    
    course2 = Course(
        name='Web Development',
        code='CS201',
        description='Full-stack web development with Flask and React',
        teacher_id=teacher.id,
        semester='Fall',
        year=2024
    )
    
    db.session.add(course1)
    db.session.add(course2)
    db.session.commit()
    
    # Enroll students
    print("Enrolling students...")
    for student in students:
        # Enroll all in course1
        enrollment1 = Enrollment(student_id=student.id, course_id=course1.id)
        db.session.add(enrollment1)
        
        # Enroll first 5 in course2
        if students.index(student) < 5:
            enrollment2 = Enrollment(student_id=student.id, course_id=course2.id)
            db.session.add(enrollment2)
    
    db.session.commit()
    
    # Generate attendance for last 10 days
    print("Generating attendance records...")
    statuses = ['present', 'absent', 'late', 'excused']
    weights = [0.75, 0.10, 0.10, 0.05]  # Mostly present
    
    for i in range(10):
        attendance_date = date.today() - timedelta(days=i)
        
        for student in students:
            # Course 1 attendance
            status = random.choices(statuses, weights)[0]
            attendance = Attendance(
                student_id=student.id,
                course_id=course1.id,
                date=attendance_date,
                status=status,
                marked_by=teacher.id
            )
            db.session.add(attendance)
            
            # Course 2 attendance (first 5 students only)
            if students.index(student) < 5:
                status = random.choices(statuses, weights)[0]
                attendance2 = Attendance(
                    student_id=student.id,
                    course_id=course2.id,
                    date=attendance_date,
                    status=status,
                    marked_by=teacher.id
                )
                db.session.add(attendance2)
    
    db.session.commit()
    
    print("\n=== Seed data created successfully ===")
    print(f"Admin: admin@zitiacademy.com / admin123")
    print(f"Teacher: teacher@zitiacademy.com / teacher123")
    print(f"Students: student1@zitiacademy.com to student10@zitiacademy.com / student123")
    print(f"Courses: {course1.name} ({course1.code}), {course2.name} ({course2.code})")
    print(f"Total attendance records: {Attendance.query.count()}")
    print("\nYou can now start the app with: python run.py")