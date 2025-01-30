import mysql.connector


class Statistic:

    def create_statistc_service(connection, id_student, id_activity, id_question, answer_correct):
        try:
            if connection.is_connected():
                query = "INSERT INTO statistic(id_student, id_activity, id_question, answer_correct) VALUES (%s, %s, %s, %s)"
                cursor = connection.cursor()
                cursor.execute(query, (id_student, id_activity , id_question, answer_correct,))
                connection.commit()
                return {"message": "Estatística criada com sucesso."}, 201
            else:
                return {"error": "Conexão com o banco de dados não está ativa."}, 500

        except mysql.connector.Error as err:
            return {"error": f"Erro ao acessar o banco de dados: {str(err)}"}, 500
        
        finally:
            cursor.close()


    def group_answer_by_id_student_service(connection, id_student, id_activity):
        try:
            if connection.is_connected():
                query = """SELECT s.id_question, s.         
                            answer_correct, q.skill_question, a.nameStudent
                            FROM statistic s
                            JOIN questions q ON s.id_question = q.id_questions
                            JOIN aluno a ON s.id_student = a.id
                            WHERE s.id_student = %s AND s.id_activity = %s
                            """
                cursor = connection.cursor()
                cursor.execute(query, (id_student, id_activity,))
                result = cursor.fetchall()
                return result
            else:
                return {"error": "Conexão com o banco de dados não está ativa."}, 500

        except mysql.connector.Error as err:
            return {"error": f"Erro ao acessar o banco de dados: {str(err)}"}, 500
        
        finally:
            cursor.close()

        
    def get_all_statistics_service_from_activity(connection, id_activity):
        try:
            if connection.is_connected():
                query = """
                SELECT id_student, id_activity, id_question, answer_correct 
                FROM statistic 
                WHERE id_activity = %s
                """
                cursor = connection.cursor(dictionary=True) 
                cursor.execute(query, (id_activity,)) 
                
                result = cursor.fetchall() 
                return result

            else:
                return {"error": "Conexão com o banco de dados não está ativa."}, 500

        except mysql.connector.Error as err:
            return {"error": f"Erro ao acessar o banco de dados: {str(err)}"}, 500
        

        finally:
            cursor.close()


    