from models.Statistic import Statistic
from db.bd_mysql import db_connection


def calculate_overall_percentagem(correct_answers, total_questions):
    if total_questions > 0:
        result = (correct_answers / total_questions) * 100
        return result
    return 0

def calculate_percentage_by_skill(skill_stats):
    skill_percentage = {
        skill: (stats["correct_answers"] / stats["total_questions"]) * 100
        for skill, stats in skill_stats.items()
    }
    return skill_percentage


def create_statistc_controller(id_student, id_activity, id_question, answer_correct):
    connection = db_connection()
    try:
        return Statistic.create_statistc_service(connection, id_student, id_activity,id_question, answer_correct)
    finally:
        connection.close()


def group_answer_by_id_student_controller(id_student, id_activity):
    connection = db_connection()
    try:
        questions = Statistic.group_answer_by_id_student_service(connection, id_student, id_activity)
    finally:
        connection.close()
    
    if not questions:
        return { "message": "Não há respostas para essa atividade" }
    
    level_stats = {}

    for question in questions:
        level = question[4]
        skill = question[2]
        correct = question[1] == 1

        if level not in level_stats:
            level_stats[level] = {}

        if skill not in level_stats[level]:
            level_stats[level][skill] = {
                "total_questions": 0,
                "correct_answers": 0
            }

        level_stats[level][skill]['total_questions'] += 1
        if correct:
            level_stats[level][skill]['correct_answers'] += 1
    

    total_questions = sum(
        stats["total_questions"] 
        for level in level_stats.values()
        for stats in level.values()
    )
    correct_answers = sum(
        stats["correct_answers"] 
        for level in level_stats.values()
        for stats in level.values()
    )

    percentage_overall  = calculate_overall_percentagem(correct_answers, total_questions)

    percentagem_level = {
        level: {
            "percentagem": round(
            sum(stats['correct_answers'] for stats in level_skills.values()) / 
            sum(stats['total_questions'] for stats in level_skills.values()) * 100, 2
        ),
            "Skills":{
            skill: round((stats['correct_answers'] / stats['total_questions']) * 100, 2)
            for skill, stats in level_skills.items()
        }
    }
       for level, level_skills in level_stats.items()
    }

    percentage_overall = round(percentage_overall, 2)

    return {
        "name_student": questions[0][3],
        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "percentage_overall": percentage_overall,
        "level_stats": level_stats,
        "percentagem_level": percentagem_level
        
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
            percentage = calculate_overall_percentagem(correct_answers, total_questions)
        else:
            percentage = 0
        
        grouped_statistics[student_id]['percentage'] = percentage
    
    return grouped_statistics