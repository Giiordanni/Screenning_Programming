from decimal import Decimal
from db.bd_mysql import db_connection
from models import Student
from models.Questions import Questions
from models.Student import Student
import numpy as np

def get_questions_by_level_controller(student_level, id_activity):
    connection = db_connection()
    
    question_params = Questions.get_question_params(connection)
    
    response = Questions.get_questions_by_level_service(connection, student_level, question_params, id_activity)

    return response, 200

# Função para definir o nível inicial do aluno (valor fixo)
def get_student_initial_level(user_id):
    connection = db_connection()
    return Student.get_student_lvl_service(connection,user_id)


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
    connection = db_connection()
    result = Questions.get_correct_answer(connection, question_id)
    if result:
        correct_aswer = result[0]
        return student_answer == correct_aswer
    return False

def get_question_params_controller(question_id):
    connection = db_connection()
    return Questions.get_params_by_question_id(connection, question_id)