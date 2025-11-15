from flask import Blueprint, request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, create_access_token
from datetime import datetime, timedelta
import qrcode
from io import BytesIO
from ..models import db, Course, User, Enrollment
from ..utils.helpers import success_response, error_response, paginate
from ..utils.decorators import teacher_or_admin_required, admin_required

bp = Blueprint('courses', __name__)

@bp.route('', methods=['GET'])
@jwt_required()
def get_courses():
    """Get courses based on user role"""
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role')
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    semester = request.args.get('semester')
    year = request.args.get('year', type=int)
    search = request.args.get('search')
    
    query = Course.query
    
    # Filter based on role
    if role == 'student':
        # Students see only enrolled courses
        query = query.join(Enrollment).filter(Enrollment.student_id == user_id)
    elif role == 'teacher':
        # Teachers see their own courses
        query = query.filter_by(teacher_id=user_id)
    # Admins see all courses
    
    if semester:
        query = query.filter_by(semester=semester)
    if year:
        query = query.filter_by(year=year)
    if search:
        query = query.filter(
            (Course.name.ilike(f'%{search}%')) |
            (Course.code.ilike(f'%{search}%'))
        )
    
    result = paginate(query.order_by(Course.created_at.desc()), page, per_page)
    return success_response(result)

@bp.route('', methods=['POST'])
@jwt_required()
@teacher_or_admin_required
def create_course():
    """Create a new course"""
    data = request.get_json()
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role')
    
    # Validate required fields
    required_fields = ['name', 'code', 'semester', 'year']
    for field in required_fields:
        if not data.get(field):
            return error_response(f'{field} is required', 400)
    
    # Check uniqueness
    existing = Course.query.filter_by(
        code=data['code'],
        semester=data['semester'],
        year=data['year']
    ).first()
    
    if existing:
        return error_response('Course with this code already exists for this semester', 409)
    
    # Create course
    teacher_id = data.get('teacher_id', user_id) if role == 'admin' else user_id
    
    course = Course(
        name=data['name'],
        code=data['code'],
        description=data.get('description', ''),
        teacher_id=teacher_id,
        semester=data['semester'],
        year=data['year']
    )
    
    try:
        db.session.add(course)
        db.session.commit()
        return success_response(course.to_dict(), 'Course created successfully', 201)
    except Exception as e:
        db.session.rollback()
        return error_response('Course creation failed', 500)
@bp.route('/<int:course_id>', methods=['GET'])
@jwt_required()
def get_course(course_id):
    """Get course details"""
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role')
    
    course = Course.query.get_or_404(course_id)
    
    # Check access
    if role == 'student':
        enrollment = Enrollment.query.filter_by(student_id=user_id, course_id=course_id).first()
        if not enrollment:
            return error_response('Access denied', 403)
    elif role == 'teacher' and course.teacher_id != user_id:
        return error_response('Access denied', 403)
    
    return success_response(course.to_dict(include_students=True))

@bp.route('/<int:course_id>', methods=['PUT'])
@jwt_required()
@teacher_or_admin_required
def update_course(course_id):
    """Update course"""
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role')
    
    course = Course.query.get_or_404(course_id)
    
    # Check permissions
    if role == 'teacher' and course.teacher_id != user_id:
        return error_response('Access denied', 403)
    
    data = request.get_json()
    
    # Update fields
    if 'name' in data:
        course.name = data['name']
    if 'description' in data:
        course.description = data['description']
    if 'semester' in data:
        course.semester = data['semester']
    if 'year' in data:
        course.year = data['year']
    
    try:
        db.session.commit()
        return success_response(course.to_dict(), 'Course updated successfully')
    except Exception as e:
        db.session.rollback()
        return error_response('Update failed', 500)

@bp.route('/<int:course_id>', methods=['DELETE'])
@jwt_required()
@teacher_or_admin_required
def delete_course(course_id):
    """Delete course"""
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role')
    
    course = Course.query.get_or_404(course_id)
    
    # Check permissions
    if role == 'teacher' and course.teacher_id != user_id:
        return error_response('Access denied', 403)
    
    try:
        db.session.delete(course)
        db.session.commit()
        return success_response(message='Course deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response('Delete failed', 500)

@bp.route('/<int:course_id>/enroll', methods=['POST'])
@jwt_required()
@teacher_or_admin_required
def enroll_student(course_id):
    """Enroll student(s) in course"""
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role')
    
    course = Course.query.get_or_404(course_id)
    
    # Check permissions
    if role == 'teacher' and course.teacher_id != user_id:
        return error_response('Access denied', 403)
    
    data = request.get_json()
    student_ids = data.get('student_ids', [])
    
    if not student_ids:
        return error_response('student_ids is required', 400)
    
    enrolled = []
    for student_id in student_ids:
        # Check if already enrolled
        existing = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
        if not existing:
            enrollment = Enrollment(student_id=student_id, course_id=course_id)
            db.session.add(enrollment)
            enrolled.append(student_id)
    
    try:
        db.session.commit()
        return success_response(
            {'enrolled_count': len(enrolled), 'student_ids': enrolled},
            f'{len(enrolled)} student(s) enrolled successfully'
        )
    except Exception as e:
        db.session.rollback()
        return error_response('Enrollment failed', 500)

@bp.route('/<int:course_id>/enroll/<int:student_id>', methods=['DELETE'])
@jwt_required()
@teacher_or_admin_required
def unenroll_student(course_id, student_id):
    """Remove student from course"""
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role')
    course = Course.query.get_or_404(course_id)
    
    # Check permissions
    if role == 'teacher' and course.teacher_id != user_id:
        return error_response('Access denied', 403)
    
    enrollment = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
    if not enrollment:
        return error_response('Student not enrolled in this course', 404)
    
    try:
        db.session.delete(enrollment)
        db.session.commit()
        return success_response(message='Student removed from course')
    except Exception as e:
        db.session.rollback()
        return error_response('Unenrollment failed', 500)

@bp.route('/<int:course_id>/students', methods=['GET'])
@jwt_required()
def get_course_students(course_id):
    """Get enrolled students for a course"""
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role')
    
    course = Course.query.get_or_404(course_id)
    
    # Check access
    if role == 'teacher' and course.teacher_id != user_id:
        return error_response('Access denied', 403)
    elif role == 'student':
        enrollment = Enrollment.query.filter_by(student_id=user_id, course_id=course_id).first()
        if not enrollment:
            return error_response('Access denied', 403)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    search = request.args.get('search')
    
    query = User.query.join(Enrollment).filter(Enrollment.course_id == course_id)
    
    if search:
        query = query.filter(
            (User.username.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )
    
    result = paginate(query.order_by(User.username), page, per_page)
    return success_response(result)

@bp.route('/<int:course_id>/qrcode', methods=['GET'])
@jwt_required()
@teacher_or_admin_required
def generate_qr_code(course_id):
    """Generate QR code for course check-in"""
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role')
    
    course = Course.query.get_or_404(course_id)
    
    # Check permissions
    if role == 'teacher' and course.teacher_id != user_id:        return error_response('Access denied', 403)
    
    # Generate short-lived JWT token for check-in
    token = create_access_token(
        identity=user_id,
        additional_claims={
            'scope': 'checkin',
            'course_id': course_id
        },
        expires_delta=timedelta(minutes=10)
    )
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(token)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png')