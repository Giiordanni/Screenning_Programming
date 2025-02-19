from decimal import Decimal
from db.bd_mysql import db_connection
from models import Student
from models.Questions import Questions
from models.Student import Student
from models.Actividy import Activity
import numpy as np


def get_questions_by_level_controller(student_level, id_activity, user_id):
    try:
        connection = db_connection()
        response = Activity.check_activity_status_student(connection, user_id, id_activity)
        if response is True:
            result = Questions.get_questions_by_level_service(connection, student_level, id_activity)
            return result, 200
        elif response is False:
            return {"error": "A atividade foi concluída."}, 400
        else:
            return {"error": "Erro ao verificar status da atividade."}, 500
    finally:
        connection.close()

# Função para definir o nível inicial do aluno (valor fixo)
def get_student_initial_level(user_id):
    try:
        connection = db_connection()
        return Student.get_student_lvl_service(connection,user_id)
    finally:
        connection.close()


def calculate_student_level(student_responses, question_params, user_id):
    theta = get_student_initial_level(user_id)
    learning_rate = Decimal('0.1')  # Convert to Decimal

    for response, params in zip(student_responses, question_params):
        discrimination, difficulty, guessing = params
        
        # Calcula a probabilidade de acerto da TRI de 3 parâmetros
        prob_correct = guessing + (1 - guessing) / (1 + np.exp(-discrimination * (theta - difficulty)))

        # Atualiza o theta baseado na resposta do aluno
        theta += learning_rate * (response - prob_correct)
    theta = round(theta, 4)
    return theta


def check_answer_controller(question_id, student_answer):
    try:
        connection = db_connection()
        result = Questions.get_correct_answer(connection, question_id)
        if result:
            correct_aswer = result[0]
            if student_answer == correct_aswer:
                return True, 1
            else:
                return False, 0
    except Exception:
        return False
    finally:
        connection.close()

def get_question_params_controller(question_id):
    try:
        connection = db_connection()
        return Questions.get_params_by_question_id(connection, question_id)
    finally:
        connection.close()


def student_activity(id_student, id_activity):
    connection = db_connection()
    try:
        is_student_associated = Activity.is_student_associated_with_activity(connection, id_student, id_activity)
        if is_student_associated:
            return Activity.update_aswered_count_student(connection, id_student, id_activity)
        else:
            return Activity.add_student_to_activity(connection, id_student, id_activity)
    except Exception as e:
        print(f"Error processing student activity: {e}")
        return False
    finally:
        connection.close()
        

def get_status_activity(id_activity):
    connection = db_connection()
    try:
        result = Activity.get_status_activity(connection, id_activity)
        if result[0].lower() == 'concluída' or result[1].lower() == 'concluída':
            return False
        else:
            return True
    except Exception as e:
        print(f"Error getting activity status: {e}")
        return False
    finally:
        connection.close()