from flask import Blueprint, request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from sqlalchemy import func
from datetime import datetime
import csv
import openpyxl
from io import BytesIO, StringIO
from ..models import db, Attendance, Course, User, Enrollment
from ..utils.helpers import success_response, error_response, parse_date

bp = Blueprint('reports', __name__)

@bp.route('/course/<int:course_id>', methods=['GET'])
@jwt_required()
def get_course_report(course_id):
    """Get attendance summary report for a course"""
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role')
    
    course = Course.query.get_or_404(course_id)
    
    # Check permissions
    if role == 'teacher' and course.teacher_id != user_id:
        return error_response('Access denied', 403)
    elif role == 'student':
        return error_response('Access denied', 403)
    
    # Date filters
    start_date = parse_date(request.args.get('start_date')) if request.args.get('start_date') else None
    end_date = parse_date(request.args.get('end_date')) if request.args.get('end_date') else None    
    query = Attendance.query.filter_by(course_id=course_id)
    if start_date:
        query = query.filter(Attendance.date >= start_date)
    if end_date:
        query = query.filter(Attendance.date <= end_date)
    
    # Status distribution
    status_counts = db.session.query(
        Attendance.status,
        func.count(Attendance.id)
    ).filter_by(course_id=course_id).group_by(Attendance.status).all()
    
    # Per-student summary
    students = User.query.join(Enrollment).filter(Enrollment.course_id == course_id).all()
    student_summaries = []
    
    for student in students:
        student_query = query.filter_by(student_id=student.id)
        total = student_query.count()
        present = student_query.filter_by(status='present').count()
        late = student_query.filter_by(status='late').count()
        absent = student_query.filter_by(status='absent').count()
        excused = student_query.filter_by(status='excused').count()
        
        attendance_rate = ((present + late) / total * 100) if total > 0 else 0
        
        student_summaries.append({
            'student': student.to_dict(),
            'total_sessions': total,
            'present': present,
            'late': late,            'absent': absent,
            'excused': excused,
            'attendance_rate': round(attendance_rate, 2)
        })
    
    return success_response({
        'course': course.to_dict(),
        'status_distribution': dict(status_counts),
        'students': student_summaries,
        'total_students': len(students)
    })

@bp.route('/student/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student_report(student_id):
    """Get attendance report for a student"""
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role')
    
    # Students can only view their own reports
    if role == 'student' and user_id != student_id:
        return error_response('Access denied', 403)
    
    student = User.query.get_or_404(student_id)
    
    # Get courses
    enrollments = Enrollment.query.filter_by(student_id=student_id).all()
    course_reports = []
    
    for enrollment in enrollments:
        course = enrollment.course
        query = Attendance.query.filter_by(student_id=student_id, course_id=course.id)
        
        total = query.count()
        present = query.filter_by(status='present').count()
        late = query.filter_by(status='late').count()
        absent = query.filter_by(status='absent').count()
        excused = query.filter_by(status='excused').count()
        
        attendance_rate = ((present + late) / total * 100) if total > 0 else 0
        
        course_reports.append({
            'course': course.to_dict(),
            'total_sessions': total,
            'present': present,
            'late': late,
            'absent': absent,
            'excused': excused,
            'attendance_rate': round(attendance_rate, 2)
        })
    
    return success_response({
        'student': student.to_dict(),
        'courses': course_reports
    })

@bp.route('/export/<int:course_id>', methods=['GET'])
@jwt_required()
def export_course_attendance(course_id):
    """Export course attendance to CSV or XLSX"""
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role')    
    course = Course.query.get_or_404(course_id)
    
    # Check permissions
    if role == 'teacher' and course.teacher_id != user_id:
        return error_response('Access denied', 403)
    elif role == 'student':
        return error_response('Access denied', 403)
    
    format_type = request.args.get('format', 'csv').lower()
    
    # Get attendance records
    records = Attendance.query.filter_by(course_id=course_id).order_by(Attendance.date.desc()).all()
    
    if format_type == 'csv':
        # Generate CSV
        si = StringIO()
        writer = csv.writer(si)
        writer.writerow(['Student Name', 'Student Email', 'Date', 'Status', 'Check-in Time', 'Notes'])
        
        for record in records:
            writer.writerow([
                record.student.username,
                record.student.email,
                record.date.isoformat(),
                record.status,
                record.check_in_time.isoformat() if record.check_in_time else '',
                record.notes or ''
            ])
        
        output = BytesIO()
        output.write(si.getvalue().encode('utf-8'))
        output.seek(0)
        
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'attendance_{course.code}_{datetime.now().strftime("%Y%m%d")}.csv'
        )
    
    elif format_type == 'xlsx':
        # Generate Excel
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'Attendance'
        
        # Headers
        headers = ['Student Name', 'Student Email', 'Date', 'Status', 'Check-in Time', 'Notes']
        ws.append(headers)
        
        for record in records:
            ws.append([
                record.student.username,
                record.student.email,
                record.date.isoformat(),
                record.status,
                record.check_in_time.isoformat() if record.check_in_time else '',
                record.notes or ''
            ])
        
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'attendance_{course.code}_{datetime.now().strftime("%Y%m%d")}.xlsx'
        )
    
    else:
        return error_response('Invalid format. Use csv or xlsx', 400)