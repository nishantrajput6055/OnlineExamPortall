"""
Authentication routes for login, registration, and logout
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils.database import execute_query, execute_insert
from utils.decorators import logout_required


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
@logout_required
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please provide both email and password.', 'danger')
            return render_template('login.html')

        query = "SELECT * FROM users WHERE username = %s"
        user = execute_query(query, (email,), fetch='one')

        if user and user['password'] == password:

            session['user_id'] = str(user['id'])
            session['username'] = user['username']
            session['role'] = user['role']

            flash('Login successful!', 'success')

            if user['role'] == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('student.dashboard'))

        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
@logout_required
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not username or not password or not confirm_password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

    
        check_query = "SELECT * FROM users WHERE username = %s"
        existing_user = execute_query(check_query, (username,), fetch='one')

        if existing_user:
            flash('User already exists.', 'danger')
            return render_template('register.html')

        insert_query = "INSERT INTO users (username, password, role) VALUES (%s, %s, 'student')"
        user_id = execute_insert(insert_query, (username, password))

        if user_id:
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Registration failed.', 'danger')

    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('auth.login'))