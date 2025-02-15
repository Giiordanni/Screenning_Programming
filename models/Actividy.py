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
            connection.close()


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


    def get_all_activity_model(connection, id_group):
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM activity WHERE id_group = %s" ,(id_group,))

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

            values.append(id_activity)
            sql_query = f"UPDATE activity SET {', '.join(fields)} WHERE id_activity = %s"
            cursor.execute(sql_query, tuple(values))
            connection.commit()

            return True
        except Error as e:
            print(f"Error updating activity in database: {e}")
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
    def create_student_table(connection, id_student, id_activity):
        try:
            cursor = connection.cursor()
            query = "INSERT INTO activity_student (id_student, id_activity) VALUES (%s, %s)"
            cursor.execute(query, (id_student, id_activity))
            connection.commit()
            return True
        except Error as e:
            print(f"Error creating student table in database: {e}")
        finally:
            cursor.close()
            

    @staticmethod
    def check_student_activity(connection, id_student, id_activity):
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM activity_student WHERE id_student = %s AND id_activity = %s", (id_student, id_activity))
            id = cursor.fetchone()
            if id:
                return id
            else:
                return None
        except Error as e:
            print(f"Error getting student activity from database: {e}")
        finally:
            cursor.close()

    @staticmethod
    def check_activity_status_student(connection, id_student, id_activity):
        try:
            cursor = connection.cursor()
            query = """SELECT ac.status_activity, a.amount_questions, ac.questions_answered_count, a.deadline, a.status_activity 
                        FROM activity_student ac 
                        JOIN activity a ON ac.id_activity = a.id_activity
                        WHERE ac.id_student = %s AND ac.id_activity = %s"""
            cursor.execute(query, (id_student, id_activity))
            result = cursor.fetchone()

            if result[1] == result[2] and result[0] == 'Aberta':
                query = "UPDATE activity_student SET status_activity = 'concluída' WHERE id_student = %s AND id_activity = %s"
                cursor.execute(query, (id_student, id_activity))
                connection.commit()
                return False
            elif result[0].lower() == 'concluída' or result[4].lower() == 'concluída':
                return False
            elif result[2] != result[1] and result[0] == 'Aberta':
                return True
            elif result[3]:
                deadline_date = datetime.strptime(result[3], '%d/%m/%Y')
                if deadline_date.date() <= datetime.today().date():
                    query = "UPDATE activity SET status_activity = 'concluída' WHERE id_activity = %s"
                    cursor.execute(query, (id_activity, ))
                    connection.commit()
                    return False
            else:
                return None
        except Exception as e:
            print(f"Erro: {e}")
            connection.rollback()
            return None
        finally:
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
        finally:
            cursor.close()
            
    @staticmethod
    def get_status_activity(connection, id_activity):
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT ac.status_activity, a.status_activity FROM activity a JOIN  activity_student ac ON a.id_activity = ac.id_activity WHERE a.id_activity = %s", (id_activity, ))
            result = cursor.fetchone()
            return result
        except Error as e:
            print(f"Error getting status activity from database: {e}")
        finally:
            cursor.close()
            
    
    def get_status_activity_all(connection, id_group):
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT id_activity, description, status_activity, deadline, amount_questions FROM activity WHERE id_group = %s", (id_group,))
            result = cursor.fetchall()
            if result:
                activities = []
                for row in result:
                    activities.append({
                        "id_activity": row[0],
                        "description": row[1],
                        "status_activity": row[2],
                        "deadline": row[3],
                        "amount_questions": row[4]
                    })
                return activities
            else:
                return None
        except Error as e:
            print(f"Error getting status activity from database: {e}")
        finally:
            cursor.close()