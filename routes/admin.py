"""
Admin routes for dashboard, exam management, and result viewing
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from utils.database import execute_query, execute_insert, execute_update, execute_many
from utils.decorators import admin_required
from datetime import datetime

# Create Blueprint
# Blueprint
admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard showing overview statistics"""
    
    total_students = execute_query(
        "SELECT COUNT(*) as count FROM users WHERE role = 'student'",
        fetch='one'
    )['count']
    
    total_exams = execute_query(
        "SELECT COUNT(*) as count FROM exams",
        fetch='one'
    )['count']
    
    total_attempts = execute_query(
        "SELECT COUNT(*) as count FROM results",
        fetch='one'
    )['count']
    
    total_questions = execute_query(
        "SELECT COUNT(*) as count FROM questions",
        fetch='one'
    )['count']
    
    recent_exams = execute_query("""
        SELECT e.exam_id, e.exam_title, e.duration_minutes, e.total_marks,
               e.created_at, COUNT(r.result_id) as attempts
        FROM exams e
        LEFT JOIN results r ON e.exam_id = r.exam_id
        GROUP BY e.exam_id
        ORDER BY e.created_at DESC
        LIMIT 5
    """, fetch='all')
    
    recent_results = execute_query("""
        SELECT r.result_id, u.full_name, e.exam_title, r.score, 
               r.total_marks, r.percentage, r.status, r.submitted_at
        FROM results r
        JOIN users u ON r.user_id = u.user_id
        JOIN exams e ON r.exam_id = e.exam_id
        ORDER BY r.submitted_at DESC
        LIMIT 5
    """, fetch='all')
    
    return render_template('admin/dashboard.html',
                         total_students=total_students,
                         total_exams=total_exams,
                         total_attempts=total_attempts,
                         total_questions=total_questions,
                         recent_exams=recent_exams,
                         recent_results=recent_results)


@admin_bp.route('/exams')
@admin_required
def manage_exams():
    """Display all exams"""
    exams = execute_query("""
        SELECT e.exam_id, e.exam_title, e.exam_description, e.duration_minutes,
               e.total_marks, e.passing_marks, e.is_active, e.created_at,
               COUNT(DISTINCT q.question_id) as question_count,
               COUNT(DISTINCT r.result_id) as attempt_count
        FROM exams e
        LEFT JOIN questions q ON e.exam_id = q.exam_id
        LEFT JOIN results r ON e.exam_id = r.exam_id
        GROUP BY e.exam_id
        ORDER BY e.created_at DESC
    """, fetch='all')
    
    return render_template('admin/manage_exams.html', exams=exams)


@admin_bp.route('/exams/create', methods=['GET', 'POST'])
@admin_required
def create_exam():
    """Create a new exam"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        duration = request.form.get('duration', type=int)
        total_marks = request.form.get('total_marks', type=int)
        passing_marks = request.form.get('passing_marks', type=int)
        
        # Validate input
        if not all([title, duration, total_marks, passing_marks]):
            flash('Please fill all required fields.', 'danger')
            return redirect(url_for('admin.create_exam'))
        
        if duration < 1 or duration > 180:
            flash('Duration must be between 1 and 180 minutes.', 'danger')
            return redirect(url_for('admin.create_exam'))
        
        if passing_marks > total_marks:
            flash('Passing marks cannot exceed total marks.', 'danger')
            return redirect(url_for('admin.create_exam'))
        
    
        query = """
            INSERT INTO exams (exam_title, exam_description, duration_minutes, 
                             total_marks, passing_marks, created_by)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        exam_id = execute_insert(query, (title, description, duration, 
                                        total_marks, passing_marks, session['user_id']))
        
        if exam_id:
            flash('Exam created successfully!', 'success')
            return redirect(url_for('admin.manage_questions', exam_id=exam_id))
        else:
            flash('Failed to create exam.', 'danger')
    
    return render_template('admin/create_exam.html')


@admin_bp.route('/exams/<int:exam_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_exam(exam_id):
    """Edit an existing exam"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        duration = request.form.get('duration', type=int)
        total_marks = request.form.get('total_marks', type=int)
        passing_marks = request.form.get('passing_marks', type=int)
        is_active = request.form.get('is_active') == 'on'
        
        query = """
            UPDATE exams 
            SET exam_title = %s, exam_description = %s, duration_minutes = %s,
                total_marks = %s, passing_marks = %s, is_active = %s
            WHERE exam_id = %s
        """
        execute_update(query, (title, description, duration, total_marks, 
                              passing_marks, is_active, exam_id))
        
        flash('Exam updated successfully!', 'success')
        return redirect(url_for('admin.manage_exams'))
    
    exam = execute_query("SELECT * FROM exams WHERE exam_id = %s", (exam_id,), fetch='one')
    return render_template('admin/edit_exam.html', exam=exam)


@admin_bp.route('/exams/<int:exam_id>/delete', methods=['POST'])
@admin_required
def delete_exam(exam_id):
    """Delete an exam"""
    execute_update("DELETE FROM exams WHERE exam_id = %s", (exam_id,))
    flash('Exam deleted successfully!', 'success')
    return redirect(url_for('admin.manage_exams'))


@admin_bp.route('/exams/<int:exam_id>/questions')
@admin_required
def manage_questions(exam_id):
    """Display and manage questions for an exam"""
    exam = execute_query("SELECT * FROM exams WHERE exam_id = %s", (exam_id,), fetch='one')
    
    if not exam:
        flash('Exam not found.', 'danger')
        return redirect(url_for('admin.manage_exams'))
    
    questions = execute_query("""
        SELECT * FROM questions 
        WHERE exam_id = %s 
        ORDER BY question_id
    """, (exam_id,), fetch='all')
    
    return render_template('admin/manage_questions.html', exam=exam, questions=questions)


@admin_bp.route('/exams/<int:exam_id>/questions/add', methods=['GET', 'POST'])
@admin_required
def add_question(exam_id):
    """Add a new question to an exam"""
    exam = execute_query("SELECT * FROM exams WHERE exam_id = %s", (exam_id,), fetch='one')
    
    if not exam:
        flash('Exam not found.', 'danger')
        return redirect(url_for('admin.manage_exams'))
    
    if request.method == 'POST':
        question_text = request.form.get('question_text', '').strip()
        option_a = request.form.get('option_a', '').strip()
        option_b = request.form.get('option_b', '').strip()
        option_c = request.form.get('option_c', '').strip()
        option_d = request.form.get('option_d', '').strip()
        correct_answer = request.form.get('correct_answer', '').strip()
        marks = request.form.get('marks', type=int, default=1)
        
        
        if not all([question_text, option_a, option_b, option_c, option_d, correct_answer]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('admin.add_question', exam_id=exam_id))
        
        if correct_answer not in ['A', 'B', 'C', 'D']:
            flash('Invalid correct answer option.', 'danger')
            return redirect(url_for('admin.add_question', exam_id=exam_id))
        
     
        query = """
            INSERT INTO questions (exam_id, question_text, option_a, option_b, 
                                 option_c, option_d, correct_answer, marks)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        question_id = execute_insert(query, (exam_id, question_text, option_a, 
                                            option_b, option_c, option_d, 
                                            correct_answer, marks))
        
        if question_id:
            flash('Question added successfully!', 'success')
            return redirect(url_for('admin.manage_questions', exam_id=exam_id))
        else:
            flash('Failed to add question.', 'danger')
    
    return render_template('admin/add_question.html', exam=exam)


@admin_bp.route('/questions/<int:question_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_question(question_id):
    """Edit an existing question"""
    question = execute_query("SELECT * FROM questions WHERE question_id = %s", 
                           (question_id,), fetch='one')
    
    if not question:
        flash('Question not found.', 'danger')
        return redirect(url_for('admin.manage_exams'))
    
    if request.method == 'POST':
        question_text = request.form.get('question_text', '').strip()
        option_a = request.form.get('option_a', '').strip()
        option_b = request.form.get('option_b', '').strip()
        option_c = request.form.get('option_c', '').strip()
        option_d = request.form.get('option_d', '').strip()
        correct_answer = request.form.get('correct_answer', '').strip()
        marks = request.form.get('marks', type=int, default=1)
        
     
        query = """
            UPDATE questions 
            SET question_text = %s, option_a = %s, option_b = %s, 
                option_c = %s, option_d = %s, correct_answer = %s, marks = %s
            WHERE question_id = %s
        """
        execute_update(query, (question_text, option_a, option_b, option_c, 
                              option_d, correct_answer, marks, question_id))
        
        flash('Question updated successfully!', 'success')
        return redirect(url_for('admin.manage_questions', exam_id=question['exam_id']))
    
    exam = execute_query("SELECT * FROM exams WHERE exam_id = %s", 
                        (question['exam_id'],), fetch='one')
    return render_template('admin/edit_question.html', question=question, exam=exam)


@admin_bp.route('/questions/<int:question_id>/delete', methods=['POST'])
@admin_required
def delete_question(question_id):
    """Delete a question"""
    question = execute_query("SELECT exam_id FROM questions WHERE question_id = %s", 
                           (question_id,), fetch='one')
    
    if question:
        execute_update("DELETE FROM questions WHERE question_id = %s", (question_id,))
        flash('Question deleted successfully!', 'success')
        return redirect(url_for('admin.manage_questions', exam_id=question['exam_id']))
    
    flash('Question not found.', 'danger')
    return redirect(url_for('admin.manage_exams'))


@admin_bp.route('/results')
@admin_required
def view_results():
    """View all exam results"""
    results = execute_query("""
        SELECT r.result_id, u.full_name, u.email, e.exam_title, 
               r.score, r.total_marks, r.percentage, r.status, 
               r.time_taken, r.submitted_at
        FROM results r
        JOIN users u ON r.user_id = u.user_id
        JOIN exams e ON r.exam_id = e.exam_id
        ORDER BY r.submitted_at DESC
    """, fetch='all')
    
    return render_template('admin/view_results.html', results=results)


@admin_bp.route('/results/<int:result_id>')
@admin_required
def view_result_detail(result_id):
    """View detailed result with answers"""
    result = execute_query("""
        SELECT r.*, u.full_name, u.email, e.exam_title, e.duration_minutes
        FROM results r
        JOIN users u ON r.user_id = u.user_id
        JOIN exams e ON r.exam_id = e.exam_id
        WHERE r.result_id = %s
    """, (result_id,), fetch='one')
    
    if not result:
        flash('Result not found.', 'danger')
        return redirect(url_for('admin.view_results'))
    
    # Get detailed answers
    answers = execute_query("""
        SELECT q.question_text, q.option_a, q.option_b, q.option_c, q.option_d,
               q.correct_answer, q.marks, sa.selected_answer, sa.is_correct
        FROM student_answers sa
        JOIN questions q ON sa.question_id = q.question_id
        WHERE sa.result_id = %s
        ORDER BY q.question_id
    """, (result_id,), fetch='all')
    
    return render_template('admin/result_detail.html', result=result, answers=answers)


@admin_bp.route('/students')
@admin_required
def manage_students():
    """View and manage students"""
    students = execute_query("""
        SELECT u.user_id, u.username, u.email, u.full_name, u.created_at,
               u.last_login, u.is_active,
               COUNT(DISTINCT r.exam_id) as exams_taken,
               AVG(r.percentage) as avg_percentage
        FROM users u
        LEFT JOIN results r ON u.user_id = r.user_id
        WHERE u.role = 'student'
        GROUP BY u.user_id
        ORDER BY u.created_at DESC
    """, fetch='all')
    
    return render_template('admin/manage_students.html', students=students)


@admin_bp.route('/students/<int:user_id>/toggle', methods=['POST'])
@admin_required
def toggle_student_status(user_id):
    """Activate or deactivate a student account"""
    student = execute_query("""
        SELECT is_active FROM users WHERE user_id = %s AND role = 'student'
    """, (user_id,), fetch='one')
    
    if student:
        new_status = not student['is_active']
        execute_update("UPDATE users SET is_active = %s WHERE user_id = %s", 
                      (new_status, user_id))
        
        status_text = 'activated' if new_status else 'deactivated'
        flash(f'Student account {status_text} successfully!', 'success')
    else:
        flash('Student not found.', 'danger')
    
    return redirect(url_for('admin.manage_students'))