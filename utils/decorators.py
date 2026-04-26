"""
Custom decorators for authentication and authorization
"""

from functools import wraps
from flask import session, redirect, url_for, flash


def login_required(f):
    """
    Decorator to ensure user is logged in
    Redirects to login page if not authenticated
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Decorator to ensure user is an admin
    Redirects to student dashboard if not admin
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if session.get('role') != 'admin':
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('student.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function


def student_required(f):
    """
    Decorator to ensure user is a student
    Redirects to admin dashboard if not student
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if session.get('role') != 'student':
            flash('Access denied. Student privileges required.', 'danger')
            return redirect(url_for('admin.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function


def logout_required(f):
    """
    Decorator to ensure user is NOT logged in
    Redirects to appropriate dashboard if already logged in
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' in session:
            if session.get('role') == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('student.dashboard'))
        return f(*args, **kwargs)
    return decorated_function