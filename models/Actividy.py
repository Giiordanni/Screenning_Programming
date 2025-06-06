from mysql.connector import Error
from datetime import datetime

class Activity:
    
    def create_activity_service(connection, id_group, id_content, description, deadline, amount_questions):
        cursor = connection.cursor()
        try:
            if amount_questions is None:
                query = "INSERT INTO activity (id_group, id_content, description, deadline) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (id_group, id_content, description, deadline))
            else:
                query = "INSERT INTO activity (id_group, id_content, description, deadline, amount_questions) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(query, (id_group, id_content, description, deadline, amount_questions))
        
            connection.commit()
            print("Activity saved successfully")
            inserted_id = cursor.lastrowid 
            return inserted_id
            
        except Error as e:
            print(f"Error saving activity to database: {e}")
        
        finally:
            cursor.close()


    def get_activity_model(connection, id_content, id_group):
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM activity WHERE id_content = %s AND id_group = %s" , (id_content,id_group,))

            result = cursor.fetchall()
            
            return result
        except Error as e:
            print(f"Error getting activity from database: {e}")
        finally:
            cursor.close()
            connection.close()


    def delete_activity_model(connection, id_activity):
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM activity WHERE id_activity = %s", (id_activity,))
            connection.commit()
            return True
        except Error as e:
            print(f"Error deleting activity from database: {e}")
        finally:
            cursor.close()
            connection.close()


    def update_activity_model(connection, id_activity, data):
        try:
            cursor = connection.cursor()

            fields = []
            values = []

            if 'description' in data:
                fields.append('description = %s')
                values.append(data['description'])
            
            if 'deadline' in data:
                fields.append('deadline = %s')
                values.append(data['deadline'])

                new_deadline_date = datetime.strptime(data['deadline'], '%d/%m/%Y')
                if new_deadline_date.date() >= datetime.today().date():
                    fields.append('status_activity = %s')
                    values.append('Aberta')
                else:
                    fields.append('status_activity = %s')
                    values.append('concluída')

            values.append(id_activity)
            sql_query = "UPDATE activity SET " + ', '.join(fields) + " WHERE id_activity = %s"
            cursor.execute(sql_query, tuple(values))
            connection.commit()

            return True
        except Error as e:
            print(f"Error updating activity in database: {e}")
            cursor.rollback()
        finally:
            cursor.close()
            connection.close()
    
    @staticmethod
    def verify_permission_user_model(connection, id_teacher, id_activity):
        try:
            cursor = connection.cursor()
            cursor.execute("""SELECT * FROM activity a 
                           JOIN group_table gp ON a.id_group = gp.id_grupo
                           WHERE a.id_activity = %s AND gp.id_teacher = %s""", (id_activity, id_teacher))
            result = cursor.fetchone()
            return result
        except Error as e:
            print(f"Error verifying permission in database: {e}")
        finally:
            cursor.close()
            connection.close()


    @staticmethod
    def add_student_to_activity(connection, student_ids, id_activitys):
        cursor = connection.cursor()
        try:
            if isinstance(student_ids, list) and isinstance(id_activitys, int):
                values = [(id_student, id_activitys) for id_student in student_ids]
                query = "INSERT INTO activity_student (id_student, id_activity) VALUES (%s, %s)"
                cursor.executemany(query, values)
            
            elif isinstance(student_ids, int) and isinstance(id_activitys, list):
                values = [(student_ids, id_activity) for id_activity in id_activitys]
                query = "INSERT INTO activity_student (id_student, id_activity) VALUES (%s, %s)"
                cursor.executemany(query, values)

            else:
                query = "INSERT INTO activity_student (id_student, id_activity) VALUES (%s, %s)"
                cursor.execute(query, (student_ids, id_activitys))
            
            connection.commit()
            return True
        except Error as e:
            print(f"Error creating student table in database: {e}")
            connection.rollback()
            return False
        finally:
            cursor.close()
            

    @staticmethod
    def check_activity_status_student(connection, id_student, id_activity):
        try:
            result = Activity.get_activity_student_status(connection, id_student, id_activity)
            
            if result is None:
                Activity.add_student_to_activity(connection, id_student=id_student, id_activity=id_activity)
                result = Activity.get_activity_student_status(connection, id_student, id_activity)

            if result[3]:
                deadline_date = datetime.strptime(result[3], '%d/%m/%Y')
                if deadline_date.date() < datetime.today().date():
                    Activity._mark_activity_as_completed(connection, id_activity=id_activity)
                    return False
            
            if result[0].lower() == 'concluída' or result[4].lower() == 'concluída':
                return False
            
            if result[2] != result[1] and result[0].lower() == 'aberta':
                return True
                
            return None
        except Exception as e:
            print(f"Erro: {e}")
            connection.rollback()
            return None
        

    #Verifica o status da atividade do aluno
    @staticmethod
    def get_activity_student_status(connection, id_student, id_activity):
        cursor = connection.cursor()
        query = """
            SELECT ac.status_activity AS student_status_activity, 
            a.amount_questions, ac.questions_answered_count, a.deadline, 
            a.status_activity AS activity_status_activity, ac.id
            FROM activity_student ac 
            JOIN activity a ON ac.id_activity = a.id_activity
            WHERE ac.id_student = %s AND ac.id_activity = %s
        """
        cursor.execute(query, (id_student, id_activity))
        return cursor.fetchone()
    
    #Marca a atividade como concluída
    @staticmethod
    def _mark_activity_as_completed(connection, id_student=None, id_activity=None):
        try:
            cursor = connection.cursor()

            if id_student and id_activity:
                query = "UPDATE activity_student SET status_activity = 'concluída' WHERE id_student = %s AND id_activity = %s"
                cursor.execute(query, (id_student, id_activity))
            else:
                cursor.execute("UPDATE activity SET status_activity = 'concluída' WHERE id_activity = %s", (id_activity,))
                
            connection.commit()  # Confirma as alterações no banco de dados
        except Exception as e:
            print(f"Erro ao marcar atividade como concluída: {e}")
            connection.rollback()  # Reverte as alterações em caso de erro
            raise
        finally:
            if cursor:
                cursor.close()
            
    @staticmethod
    def update_aswered_count_student(connection, id_student, id_activity):
        try:
            cursor = connection.cursor()
            cursor.execute("UPDATE activity_student SET questions_answered_count = questions_answered_count + 1 WHERE id_student = %s AND id_activity = %s", (id_student, id_activity))
            connection.commit()
            return True
        except Error as e:
            print(f"Error updating answered count in database: {e}")
            connection.rollback()
            return False
        finally:
            cursor.close()
            
    @staticmethod
    def get_status_activity(connection, id_activity):
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT ac.status_activity, a.status_activity FROM activity a JOIN  activity_student ac ON a.id_activity = ac.id_activity WHERE a.id_activity = %s", (id_activity, ))
            result = cursor.fetchall()
            if result:
                response = [status for row in result for status in row]
                return response
            else:
                return None
        except Error as e:
            print(f"Error getting status activity from database: {e}")
        finally:
            cursor.close()
    
    
    def get_status_activity_all(connection, id_group, id_student=None):
        cursor = connection.cursor()
        activities = []
        try:
            if id_student:
                query =  """SELECT a.id_activity, a.id_content, a.description, 
                            ac.status_activity AS student_activity_status,
                            a.deadline, a.amount_questions
                            FROM activity a 
                            LEFT JOIN activity_student ac 
                            ON a.id_activity = ac.id_activity AND ac.id_student = %s
                            WHERE a.id_group = %s"""
                
                cursor.execute(query, (id_student, id_group))
            
            else: 
                query = "SELECT id_activity, id_content, description, status_activity, deadline, amount_questions FROM activity WHERE id_group = %s"
                cursor.execute(query, (id_group,))
            
            result = cursor.fetchall()

            if result:
                for row in result:
                    deadline_date = datetime.strptime(row[4], '%d/%m/%Y')
                    if deadline_date.date() < datetime.today().date():
                        Activity._mark_activity_as_completed(connection, id_activity=row[0])
                        if id_student:
                            status_activity = "student_activity_status"
                            cursor.execute(query, (id_student, id_group))
                        else:
                            status_activity = "status_activity"
                            cursor.execute(query, (id_group,))
                        result = cursor.fetchall()

                    activities.append({
                        "id_activity": row[0],
                        "id_content": row[1],
                        "description": row[2],
                        "status_activity": row[3] if row[3] != None else "Não iniciada",
                        "deadline": row[4],
                        "amount_questions": row[5]
                    })
                return activities
            else:
                return None
        except Error as e:
            print(f"Error getting status activity from database: {e}")
        finally:
            cursor.close()

    @staticmethod
    def get_id_student_by_group(connection, id_group):
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT id_aluno FROM student_group where id_grupo = %s", (id_group,))
            result = cursor.fetchall()

            students = []
            for row in result:
                students.append(row[0])
            return students
        except Error as e:
            print(f"Error getting student id from database: {e}")
        finally:
            cursor.close()
