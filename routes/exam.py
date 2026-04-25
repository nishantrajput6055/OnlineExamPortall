"""
Exam taking routes for starting exams, submitting answers, and calculating results
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from utils.database import execute_query, execute_insert, execute_many
from utils.decorators import student_required
from datetime import datetime, timedelta

# Create Blueprint
exam_bp = Blueprint('exam', __name__)


@exam_bp.route('/<int:exam_id>/start')
@student_required
def start_exam(exam_id):
    """Start an exam"""
    user_id = session['user_id']
    
    # Get exam details
    exam = execute_query("""
        SELECT * FROM exams WHERE exam_id = %s AND is_active = TRUE
    """, (exam_id,), fetch='one')
    
    if not exam:
        flash('Exam not found or not available.', 'danger')
        return redirect(url_for('student.dashboard'))
    
    # Get questions for the exam
    questions = execute_query("""
        SELECT question_id, question_text, option_a, option_b, option_c, option_d, marks
        FROM questions
        WHERE exam_id = %s
        ORDER BY question_id
    """, (exam_id,), fetch='all')
    
    if not questions:
        flash('This exam has no questions yet.', 'danger')
        return redirect(url_for('student.dashboard'))
    
    # Store exam start time in session
    session['exam_start_time'] = datetime.now().isoformat()
    session['current_exam_id'] = exam_id
    
    return render_template('student/exam.html', exam=exam, questions=questions)


@exam_bp.route('/<int:exam_id>/submit', methods=['POST'])
@student_required
def submit_exam(exam_id):
    """Submit exam answers and calculate results"""
    user_id = session['user_id']
    
    # Verify exam session
    if session.get('current_exam_id') != exam_id:
        flash('Invalid exam session.', 'danger')
        return redirect(url_for('student.dashboard'))
    
    # Calculate time taken
    start_time_str = session.get('exam_start_time')
    if not start_time_str:
        flash('Invalid exam session.', 'danger')
        return redirect(url_for('student.dashboard'))
    
    start_time = datetime.fromisoformat(start_time_str)
    end_time = datetime.now()
    time_taken = int((end_time - start_time).total_seconds())
    
    # Get exam details
    exam = execute_query("""
        SELECT exam_id, total_marks, passing_marks, duration_minutes
        FROM exams WHERE exam_id = %s
    """, (exam_id,), fetch='one')
    
    if not exam:
        flash('Exam not found.', 'danger')
        return redirect(url_for('student.dashboard'))
    
    # Check if time exceeded (with 5 second buffer)
    max_time = exam['duration_minutes'] * 60 + 5
    if time_taken > max_time:
        time_taken = exam['duration_minutes'] * 60
    
    # Get all questions with correct answers
    questions = execute_query("""
        SELECT question_id, correct_answer, marks
        FROM questions
        WHERE exam_id = %s
    """, (exam_id,), fetch='all')
    
    # Create a dictionary for quick lookup
    question_dict = {q['question_id']: q for q in questions}
    
    # Get submitted answers
    submitted_answers = {}
    for key, value in request.form.items():
        if key.startswith('question_'):
            question_id = int(key.split('_')[1])
            submitted_answers[question_id] = value.upper()
    
    # Calculate score
    score = 0
    student_answers = []
    
    for question_id, question_data in question_dict.items():
        selected_answer = submitted_answers.get(question_id, '')
        is_correct = selected_answer == question_data['correct_answer']
        
        if is_correct:
            score += question_data['marks']
        
        student_answers.append({
            'question_id': question_id,
            'selected_answer': selected_answer if selected_answer else 'A',  # Default to A if not answered
            'is_correct': is_correct
        })
    
    # Calculate percentage and status
    total_marks = exam['total_marks']
    percentage = round((score / total_marks) * 100, 2) if total_marks > 0 else 0
    status = 'pass' if score >= exam['passing_marks'] else 'fail'
    
    # Insert result
    result_query = """
        INSERT INTO results (user_id, exam_id, score, total_marks, percentage, status, time_taken)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    result_id = execute_insert(result_query, (user_id, exam_id, score, total_marks, 
                                              percentage, status, time_taken))
    
    if not result_id:
        flash('Failed to save exam results.', 'danger')
        return redirect(url_for('student.dashboard'))
    
    # Insert student answers
    answer_query = """
        INSERT INTO student_answers (result_id, question_id, selected_answer, is_correct)
        VALUES (%s, %s, %s, %s)
    """
    answer_data = [(result_id, ans['question_id'], ans['selected_answer'], ans['is_correct']) 
                   for ans in student_answers]
    execute_many(answer_query, answer_data)
    
    # Clear exam session data
    session.pop('exam_start_time', None)
    session.pop('current_exam_id', None)
    
    flash('Exam submitted successfully!', 'success')
    return redirect(url_for('student.view_result', result_id=result_id))


@exam_bp.route('/<int:exam_id>/check_time', methods=['GET'])
@student_required
def check_exam_time(exam_id):
    """API endpoint to check remaining exam time"""
    if session.get('current_exam_id') != exam_id:
        return jsonify({'error': 'Invalid exam session'}), 400
    
    start_time_str = session.get('exam_start_time')
    if not start_time_str:
        return jsonify({'error': 'No start time found'}), 400
    
    # Get exam duration
    exam = execute_query("""
        SELECT duration_minutes FROM exams WHERE exam_id = %s
    """, (exam_id,), fetch='one')
    
    if not exam:
        return jsonify({'error': 'Exam not found'}), 404
    
    # Calculate remaining time
    start_time = datetime.fromisoformat(start_time_str)
    elapsed_seconds = int((datetime.now() - start_time).total_seconds())
    total_seconds = exam['duration_minutes'] * 60
    remaining_seconds = max(0, total_seconds - elapsed_seconds)
    
    return jsonify({
        'remaining_seconds': remaining_seconds,
        'elapsed_seconds': elapsed_seconds,
        'total_seconds': total_seconds
    })


@exam_bp.route('/<int:exam_id>/auto_submit', methods=['POST'])
@student_required
def auto_submit_exam(exam_id):
    """Auto-submit exam when time expires"""
    # This endpoint is called by JavaScript when timer reaches 0
    # It performs the same submission logic as submit_exam
    return submit_exam(exam_id)