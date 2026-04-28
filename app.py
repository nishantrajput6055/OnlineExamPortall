from flask import Flask, render_template, session, redirect, url_for
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)

# Use Flask's built-in session (no Flask-Session)
app.secret_key = Config.SECRET_KEY

# Import routes
from routes import auth, admin, student, exam

# Register blueprints
app.register_blueprint(auth.auth_bp)
app.register_blueprint(admin.admin_bp, url_prefix='/admin')
app.register_blueprint(student.student_bp, url_prefix='/student')
app.register_blueprint(exam.exam_bp, url_prefix='/exam')

@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('student.dashboard'))
    return render_template('index.html')


@app.context_processor
def inject_user():
    return {
        'current_user': {
            'id': session.get('user_id'),
            'username': session.get('username'),
            'role': session.get('role'),
            'full_name': session.get('full_name')
        }
    }


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)