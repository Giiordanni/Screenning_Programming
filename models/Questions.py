from multiprocessing import connection
import random
import numpy as np
from decimal import Decimal
import mysql.connector

class Questions:
    @staticmethod
    def get_questions_by_level_service(connection, student_level, id_activity):
        try:
            # Verifica se a conexão está ativa
            if connection.is_connected():
                with connection.cursor() as cursor:
                    # Consulta para obter questões e seus parâmetros
                    query = """
                    SELECT q.id_questions, q.skill_question, q.question, q.answer, q.slope, q.threshold, q.asymptote
                    FROM questions q
                    JOIN activity a ON q.id_content = a.id_content
                    WHERE a.id_activity = %s
                    """
                    cursor.execute(query, (id_activity,))
                    results = cursor.fetchall()

                    if not results:
                        return {"error": "Nenhuma questão encontrada."}, 200

                    # Iterar sobre as questões e os parâmetros TRI
                    suitable_questions = []  # Lista para armazenar questões adequadas

                    for row in results:
                        question_id = row[0]
                        skill = row[1]
                        question_image = row[2]
                        answer = row[3]
                        slope = row[4]  # Discrimination
                        threshold = row[5]  # Difficulty
                        asymptote = row[6]  # Guessing

                        # Calcular a probabilidade de acerto com base nos parâmetros TRI
                        prob_correct = calculate_question_prob(student_level, slope, threshold, asymptote)

                        if is_question_suitable(prob_correct, student_level):
                            suitable_questions.append({
                                "ID": question_id,
                                "Skill": skill,
                                "Question Image": question_image,
                                "Answer": answer,
                                "Question Value": prob_correct
                            })

                    if suitable_questions:
                        # Retornar uma questão adequada aleatória
                        return random.choice(suitable_questions), 200

                    # Se nenhuma questão for adequada, retorna uma mensagem de erro
                    return {"error": "Nenhuma questão adequada encontrada."}, 200

            else:
                return {"error": "Conexão com o banco de dados não está ativa."}, 500

        except mysql.connector.Error as err:
            return {"error": f"Erro ao acessar o banco de dados: {str(err)}"}, 500
        
    @staticmethod
    def get_correct_answer(connection, question_id):
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT answer FROM questions WHERE id_questions = %s", (question_id,))
            return cursor.fetchone()
        finally:
            cursor.close()

    def get_level_questions_by_id_service(connection, id):
        query = "SELECT level_questions FROM questions WHERE id_questions = %s"
        cursor = connection.cursor()
        cursor.execute(query, (id,))
        result = cursor.fetchone()
        return result

    def get_params_by_question_id(connection, question_id):
        query = "SELECT slope, threshold, asymptote FROM questions WHERE id_questions = %s"
        cursor = connection.cursor()
        cursor.execute(query, (question_id,))
        params = cursor.fetchone()
        return params
    
    def get_question_params(connection):
        query = "SELECT id_questions, slope, threshold, asymptote FROM questions"
        cursor = connection.cursor()
        cursor.execute(query)
        params = cursor.fetchall()
        return [(param[0], param[1], param[2], param[3]) for param in params]

def calculate_question_prob(student_level, slope, threshold, asymptote):

    student_level = float(student_level) if isinstance(student_level, Decimal) else student_level
    slope = float(slope) if isinstance(slope, Decimal) else slope
    threshold = float(threshold) if isinstance(threshold, Decimal) else threshold
    asymptote = float(asymptote) if isinstance(asymptote, Decimal) else asymptote

    return asymptote + (1 - asymptote) / (1 + np.exp(-slope * (student_level - threshold)))


def is_question_suitable(prob_correct, threshold):
    return prob_correct >= threshold

    