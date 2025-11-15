from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, decode_token
from datetime import datetime, date
from ..models import db, Attendance, Course, Enrollment, User
from ..utils.helpers import success_response, error_response, paginate, parse_date
from ..utils.decorators import teacher_or_admin_required

bp = Blueprint('attendance', __name__)

@bp.route('', methods=['POST'])
@jwt_required()
@teacher_or_admin_required
def mark_attendance():
    """Mark attendance for a student"""
    data = request.get_json()
    user_id = get_jwt_identity()
    
    # Validate required fields
    required_fields = ['course_id', 'student_id', 'date', 'status']
    for field in required_fields:
        if field not in data:
            return error_response(f'{field} is required', 400)
    
    # Validate status
    valid_statuses = ['present', 'absent', 'late', 'excused']
    if data['status'] not in valid_statuses:
        return error_response(f'Invalid status. Must be one of: {", ".join(valid_statuses)}', 400)
    
    # Parse date
    attendance_date = parse_date(data['date'])
    if not attendance_date:        return error_response('Invalid date format', 400)
    
    # Check if student is enrolled
    enrollment = Enrollment.query.filter_by(
        student_id=data['student_id'],
        course_id=data['course_id']
    ).first()
    
    if not enrollment:
        return error_response('Student not enrolled in this course', 400)
    
    # Check for existing attendance
    existing = Attendance.query.filter_by(
        student_id=data['student_id'],
        course_id=data['course_id'],
        date=attendance_date
    ).first()
    
    if existing:
        # Update existing
        existing.status = data['status']
        existing.notes = data.get('notes')
        existing.marked_by = user_id
        if data['status'] in ['present', 'late'] and not existing.check_in_time:
            existing.check_in_time = datetime.utcnow()
    else:
        # Create new
        attendance = Attendance(
            student_id=data['student_id'],
            course_id=data['course_id'],
            date=attendance_date,
            status=data['status'],            notes=data.get('notes'),
            marked_by=user_id,
            check_in_time=datetime.utcnow() if data['status'] in ['present', 'late'] else None
        )
        db.session.add(attendance)
    
    try:
        db.session.commit()
        return success_response(
            existing.to_dict() if existing else attendance.to_dict(),
            'Attendance marked successfully',
            201 if not existing else 200
        )
    except Exception as e:
        db.session.rollback()
        return error_response('Failed to mark attendance', 500)

@bp.route('/bulk', methods=['POST'])
@jwt_required()
@teacher_or_admin_required
def bulk_mark_attendance():
    """Mark attendance for multiple students"""
    data = request.get_json()
    user_id = get_jwt_identity()
    
    records = data.get('records', [])
    if not records:
        return error_response('records array is required', 400)
    
    created = 0
    updated = 0
    errors = []    
    for record in records:
        try:
            attendance_date = parse_date(record.get('date'))
            if not attendance_date:
                errors.append({'record': record, 'error': 'Invalid date'})
                continue
            
            existing = Attendance.query.filter_by(
                student_id=record['student_id'],
                course_id=record['course_id'],
                date=attendance_date
            ).first()
            
            if existing:
                existing.status = record['status']
                existing.notes = record.get('notes')
                existing.marked_by = user_id
                if record['status'] in ['present', 'late'] and not existing.check_in_time:
                    existing.check_in_time = datetime.utcnow()
                updated += 1
            else:
                attendance = Attendance(
                    student_id=record['student_id'],
                    course_id=record['course_id'],
                    date=attendance_date,
                    status=record['status'],
                    notes=record.get('notes'),
                    marked_by=user_id,
                    check_in_time=datetime.utcnow() if record['status'] in ['present', 'late'] else None
                )
                db.session.add(attendance)
                created += 1
        except Exception as e:
            errors.append({'record': record, 'error': str(e)})
    
    try:
        db.session.commit()
        return success_response({
            'created': created,
            'updated': updated,
            'errors': errors
        }, f'Processed {created + updated} attendance records')
    except Exception as e:
        db.session.rollback()
        return error_response('Bulk operation failed', 500)

@bp.route('/checkin', methods=['POST'])
@jwt_required()
def checkin():
    """Student check-in via QR code token"""
    data = request.get_json()
    token = data.get('token')
    
    if not token:
        return error_response('Token is required', 400)
    
    try:
        # Decode and verify token
        decoded = decode_token(token)
        claims = decoded.get('sub')
        scope = decoded.get('scope')
        course_id = decoded.get('course_id')
        if scope != 'checkin' or not course_id:
            return error_response('Invalid check-in token', 400)
        
        # Get current user (student)
        student_id = get_jwt_identity()
        
        # Verify enrollment
        enrollment = Enrollment.query.filter_by(
            student_id=student_id,
            course_id=course_id
        ).first()
        
        if not enrollment:
            return error_response('You are not enrolled in this course', 403)
        
        # Mark attendance
        today = date.today()
        existing = Attendance.query.filter_by(
            student_id=student_id,
            course_id=course_id,
            date=today
        ).first()
        
        if existing:
            existing.status = 'present'
            existing.check_in_time = datetime.utcnow()
        else:
            attendance = Attendance(
                student_id=student_id,
                course_id=course_id,
                date=today,
                status='present',                check_in_time=datetime.utcnow()
            )
            db.session.add(attendance)
        
        db.session.commit()
        return success_response(
            existing.to_dict() if existing else attendance.to_dict(),
            'Check-in successful'
        )
    except Exception as e:
        db.session.rollback()
        return error_response('Check-in failed', 400)

@bp.route('/course/<int:course_id>', methods=['GET'])
@jwt_required()
def get_course_attendance(course_id):
    """Get attendance records for a course"""
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role')
    
    course = Course.query.get_or_404(course_id)
    
    # Check permissions
    if role == 'teacher' and course.teacher_id != user_id:
        return error_response('Access denied', 403)
    elif role == 'student':
        return error_response('Access denied', 403)
    
    # Filters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    status = request.args.get('status')
    
    query = Attendance.query.filter_by(course_id=course_id)
    
    if start_date:
        query = query.filter(Attendance.date >= parse_date(start_date))
    if end_date:
        query = query.filter(Attendance.date <= parse_date(end_date))
    if status:
        query = query.filter_by(status=status)
    
    result = paginate(query.order_by(Attendance.date.desc()), page, per_page)
    return success_response(result)

@bp.route('/student/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student_attendance(student_id):
    """Get attendance records for a student"""
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role')
    
    # Students can only view their own attendance
    if role == 'student' and user_id != student_id:
        return error_response('Access denied', 403)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    course_id = request.args.get('course_id', type=int)
    query = Attendance.query.filter_by(student_id=student_id)
    
    if course_id:
        query = query.filter_by(course_id=course_id)
    
    result = paginate(query.order_by(Attendance.date.desc()), page, per_page)
    return success_response(result)

@bp.route('/<int:attendance_id>', methods=['PUT'])
@jwt_required()
@teacher_or_admin_required
def update_attendance(attendance_id):
    """Update attendance record"""
    attendance = Attendance.query.get_or_404(attendance_id)
    data = request.get_json()
    
    if 'status' in data:
        attendance.status = data['status']
    if 'notes' in data:
        attendance.notes = data['notes']
    
    try:
        db.session.commit()
        return success_response(attendance.to_dict(), 'Attendance updated')
    except Exception as e:
        db.session.rollback()
        return error_response('Update failed', 500)

@bp.route('/<int:attendance_id>', methods=['DELETE'])
@jwt_required()
@teacher_or_admin_required
def delete_attendance(attendance_id):
    """Delete attendance record"""
    attendance = Attendance.query.get_or_404(attendance_id)
    
    try:
        db.session.delete(attendance)
        db.session.commit()
        return success_response(message='Attendance deleted')
    except Exception as e:
        db.session.rollback()
        return error_response('Delete failed', 500)