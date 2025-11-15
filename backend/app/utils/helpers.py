from flask import jsonify
from datetime import datetime
from dateutil import parser as date_parser

def success_response(data=None, message=None, status=200):
    """Standard success response"""
    response = {'success': True}
    if message:
        response['message'] = message
    if data is not None:
        response['data'] = data
    return jsonify(response), status

def error_response(message, status=400, errors=None):
    """Standard error response"""
    response = {
        'success': False,
        'error': message
    }
    if errors:
        response['errors'] = errors
    return jsonify(response), status

def paginate(query, page=1, per_page=20):
    """Paginate a SQLAlchemy query"""
    page = max(1, page)
    per_page = min(100, max(1, per_page))
    
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return {        'items': [item.to_dict() if hasattr(item, 'to_dict') else item for item in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'page': page,
        'per_page': per_page,
        'has_next': paginated.has_next,
        'has_prev': paginated.has_prev
    }

def parse_date(date_string):
    """Parse date string to date object"""
    try:
        if isinstance(date_string, str):
            return date_parser.parse(date_string).date()
        return date_string
    except:
        return None

def parse_datetime(datetime_string):
    """Parse datetime string to datetime object"""
    try:
        if isinstance(datetime_string, str):
            return date_parser.parse(datetime_string)
        return datetime_string
    except:
        return None