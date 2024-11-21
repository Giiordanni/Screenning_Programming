from models.Statistic import Statistic
from db.bd_mysql import db_connection


def calculate_percentage(correct_answers, total_questions):
    if total_questions > 0:
        return (correct_answers / total_questions) * 100
    return 0


def create_statistc_controller(data):
    id_student = data.get('id_student')
    id_activity = data.get('id_activity')
    id_question = data.get('id_question')
    answer_correct = data.get('answer_correct')

    connection = db_connection()
    try:
        return Statistic.create_statistc_service(connection, id_student, id_activity,id_question, answer_correct)
    finally:
        connection.close()



def group_answer_by_id_student_controller(id_student,id_activity):
    connection = db_connection()
    try:
        questions = Statistic.group_answer_by_id_student_service(connection, id_student,id_activity)
    finally:
        connection.close()
    
    count_correct_answer = sum(1 for question in questions if question[1] == 1)
    total_questions = len(questions)

    if total_questions == 0:
        return { "message": "Não há respostas para essa atividade" }

    percentage = calculate_percentage(count_correct_answer, total_questions)

    return {
        "total_questions": total_questions,
        "correct_answers": count_correct_answer,
        "percentage": percentage
    }


def get_all_statistics_by_activity(id_activity):
    connection = db_connection()
    try:
        questions = Statistic.get_all_statistics_service_from_activity(connection, id_activity)
    finally:
        connection.close()
    
    grouped_statistics = {}

    for question in questions:
        id_student = question['id_student']
        id_question = question['id_question']
        answer_correct = question['answer_correct']
        
        if id_student not in grouped_statistics:
            grouped_statistics[id_student] = {
                'id_activity': id_activity,
                'total_questions': 0,
                'correct_answers': 0,
                'questions': []
            }
        
        grouped_statistics[id_student]['total_questions'] += 1
        
        if answer_correct == 1:
            grouped_statistics[id_student]['correct_answers'] += 1
        
        grouped_statistics[id_student]['questions'].append({
            'id_question': id_question,
            'answer_correct': answer_correct
        })
    
    for student_id, stats in grouped_statistics.items():
        total_questions = stats['total_questions']
        correct_answers = stats['correct_answers']
        
        if total_questions > 0:
            percentage = calculate_percentage(correct_answers, total_questions)
        else:
            percentage = 0
        
        grouped_statistics[student_id]['percentage'] = percentage
    
    return grouped_statistics



