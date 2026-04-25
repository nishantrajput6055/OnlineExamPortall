"""
Student routes for dashboard, exam listing, and exam history
"""

from flask import Blueprint, render_template, session, flash, redirect, url_for
from utils.database import execute_query
from utils.decorators import student_required
from utils.helpers import get_grade

# Create Blueprint
student_bp = Blueprint('student', __name__)


@student_bp.route('/dashboard')
@student_required
def dashboard():
    """Student dashboard showing available exams and statistics"""
    user_id = session['user_id']
    

    stats = execute_query("""
        SELECT 
            COUNT(DISTINCT exam_id) as exams_taken,
            AVG(percentage) as avg_percentage,
            SUM(CASE WHEN status = 'pass' THEN 1 ELSE 0 END) as exams_passed
        FROM results
        WHERE user_id = %s
    """, (user_id,), fetch='one')
    
    
    available_exams = execute_query("""
        SELECT e.exam_id, e.exam_title, e.exam_description, e.duration_minutes,
               e.total_marks, e.passing_marks,
               COUNT(q.question_id) as question_count,
               (SELECT COUNT(*) FROM results r 
                WHERE r.exam_id = e.exam_id AND r.user_id = %s) as attempt_count
        FROM exams e
        LEFT JOIN questions q ON e.exam_id = q.exam_id
        WHERE e.is_active = TRUE
        GROUP BY e.exam_id
        ORDER BY e.created_at DESC
    """, (user_id,), fetch='all')
    
    recent_results = execute_query("""
        SELECT r.result_id, e.exam_title, r.score, r.total_marks, 
               r.percentage, r.status, r.submitted_at
        FROM results r
        JOIN exams e ON r.exam_id = e.exam_id
        WHERE r.user_id = %s
        ORDER BY r.submitted_at DESC
        LIMIT 5
    """, (user_id,), fetch='all')
    
    return render_template('student/dashboard.html',
                         stats=stats,
                         available_exams=available_exams,
                         recent_results=recent_results)


@student_bp.route('/history')
@student_required
def exam_history():
    """View complete exam history"""
    user_id = session['user_id']
    
    results = execute_query("""
        SELECT r.result_id, e.exam_title, e.total_marks, r.score,
               r.percentage, r.status, r.time_taken, r.submitted_at
        FROM results r
        JOIN exams e ON r.exam_id = e.exam_id
        WHERE r.user_id = %s
        ORDER BY r.submitted_at DESC
    """, (user_id,), fetch='all')
    
    for result in results:
        result['grade'] = get_grade(result['percentage'])
    
    return render_template('student/history.html', results=results)


@student_bp.route('/results/<int:result_id>')
@student_required
def view_result(result_id):
    """View detailed result for a specific exam attempt"""
    user_id = session['user_id']
    
    result = execute_query("""
        SELECT r.*, e.exam_title, e.duration_minutes, e.passing_marks
        FROM results r
        JOIN exams e ON r.exam_id = e.exam_id
        WHERE r.result_id = %s AND r.user_id = %s
    """, (result_id, user_id), fetch='one')
    
    if not result:
        flash('Result not found.', 'danger')
        return redirect(url_for('student.exam_history'))
    
    answers = execute_query("""
        SELECT q.question_text, q.option_a, q.option_b, q.option_c, q.option_d,
               q.correct_answer, q.marks, sa.selected_answer, sa.is_correct
        FROM student_answers sa
        JOIN questions q ON sa.question_id = q.question_id
        WHERE sa.result_id = %s
        ORDER BY q.question_id
    """, (result_id,), fetch='all')
    
    total_questions = len(answers)
    correct_answers = sum(1 for ans in answers if ans['is_correct'])
    wrong_answers = total_questions - correct_answers
    
    result['grade'] = get_grade(result['percentage'])
    
    return render_template('student/result.html',
                         result=result,
                         answers=answers,
                         total_questions=total_questions,
                         correct_answers=correct_answers,
                         wrong_answers=wrong_answers)


@student_bp.route('/profile')
@student_required
def profile():
    """View student profile and statistics"""
    user_id = session['user_id']

    user = execute_query("""
        SELECT username, email, full_name, created_at, last_login
        FROM users
        WHERE user_id = %s
    """, (user_id,), fetch='one')
    
    performance = execute_query("""
        SELECT 
            COUNT(*) as total_exams,
            SUM(CASE WHEN status = 'pass' THEN 1 ELSE 0 END) as passed_exams,
            AVG(percentage) as avg_percentage,
            MAX(percentage) as best_percentage,
            MIN(percentage) as worst_percentage
        FROM results
        WHERE user_id = %s
    """, (user_id,), fetch='one')
    
    exam_performance = execute_query("""
        SELECT e.exam_title, r.percentage, r.status, r.submitted_at
        FROM results r
        JOIN exams e ON r.exam_id = e.exam_id
        WHERE r.user_id = %s
        ORDER BY r.submitted_at DESC
        LIMIT 10
    """, (user_id,), fetch='all')
    
    return render_template('student/profile.html',
                         user=user,
                         performance=performance,
                         exam_performance=exam_performance)