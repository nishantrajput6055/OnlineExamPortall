"""
Helper functions for the application
Contains utility functions used across the application
"""

from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import re


def hash_password(password):
    """
    Hash a password using Werkzeug's security functions
    
    Args:
        password (str): Plain text password
    
    Returns:
        str: Hashed password
    """
    return generate_password_hash(password, method='scrypt')


def verify_password(password_hash, password):
    """
    Verify a password against its hash
    
    Args:
        password_hash (str): Hashed password
        password (str): Plain text password to verify
    
    Returns:
        bool: True if password matches, False otherwise
    """
    return check_password_hash(password_hash, password)


def validate_email(email):
    """
    Validate email format using regex
    
    Args:
        email (str): Email address to validate
    
    Returns:
        bool: True if valid email format, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """
    Validate password strength
    Requirements: At least 6 characters
    
    Args:
        password (str): Password to validate
    
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    return True, ""


def validate_username(username):
    """
    Validate username format
    Requirements: 3-20 characters, alphanumeric and underscore only
    
    Args:
        username (str): Username to validate
    
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    if len(username) < 3 or len(username) > 20:
        return False, "Username must be between 3 and 20 characters"
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    
    return True, ""


def calculate_percentage(score, total):
    """
    Calculate percentage score
    
    Args:
        score (int): Score obtained
        total (int): Total marks
    
    Returns:
        float: Percentage (rounded to 2 decimal places)
    """
    if total == 0:
        return 0.0
    return round((score / total) * 100, 2)


def format_duration(seconds):
    """
    Format duration from seconds to readable format
    
    Args:
        seconds (int): Duration in seconds
    
    Returns:
        str: Formatted duration (e.g., "1h 30m 45s")
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")
    
    return " ".join(parts)


def get_exam_status(start_time, end_time):
    """
    Determine exam status based on start and end times
    
    Args:
        start_time (datetime): Exam start time
        end_time (datetime): Exam end time
    
    Returns:
        str: 'upcoming', 'ongoing', or 'completed'
    """
    now = datetime.now()
    
    if start_time and now < start_time:
        return 'upcoming'
    elif end_time and now > end_time:
        return 'completed'
    else:
        return 'ongoing'


def sanitize_input(text):
    """
    Basic input sanitization to prevent XSS
    
    Args:
        text (str): Input text
    
    Returns:
        str: Sanitized text
    """
    if not text:
        return ""
    
    # Remove potential HTML tags
    text = re.sub(r'<[^>]*>', '', text)
    
    # Remove potential script tags
    text = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', text, flags=re.IGNORECASE)
    
    return text.strip()


def paginate_results(results, page=1, per_page=10):
    """
    Paginate a list of results
    
    Args:
        results (list): List of items to paginate
        page (int): Current page number (1-indexed)
        per_page (int): Items per page
    
    Returns:
        dict: Pagination data including items, total_pages, current_page, etc.
    """
    total_items = len(results)
    total_pages = (total_items + per_page - 1) // per_page
    
    # Ensure page is within valid range
    page = max(1, min(page, total_pages if total_pages > 0 else 1))
    
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    return {
        'items': results[start_idx:end_idx],
        'total_items': total_items,
        'total_pages': total_pages,
        'current_page': page,
        'per_page': per_page,
        'has_prev': page > 1,
        'has_next': page < total_pages
    }


def get_grade(percentage):
    """
    Convert percentage to letter grade
    
    Args:
        percentage (float): Percentage score
    
    Returns:
        str: Letter grade
    """
    if percentage >= 90:
        return 'A+'
    elif percentage >= 80:
        return 'A'
    elif percentage >= 70:
        return 'B+'
    elif percentage >= 60:
        return 'B'
    elif percentage >= 50:
        return 'C'
    elif percentage >= 40:
        return 'D'
    else:
        return 'F'