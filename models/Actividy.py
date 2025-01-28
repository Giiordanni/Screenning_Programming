from mysql.connector import Error

class Activity:
    
    def create_activity_service(self, connection, id_group,id_content, description, deadline, amount_questions):
        try:
            cursor = connection.cursor()
 
            if amount_questions is None:
                query = "INSERT INTO activity (id_group, id_content, description, deadline) VALUES (%s, %s, %s, %s"
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
    def create_student_table(connection, id_student, id_activity, questions_answered_count):
        try:
            cursor = connection.cursor()
            query = "INSERT INTO activity_student (id_student, id_activity, questions_answered_count) VALUES (%s, %s, %s)"
            cursor.execute(query, (id_student, id_activity, questions_answered_count))
            connection.commit()
            return True
        except Error as e:
            print(f"Error creating student table in database: {e}")
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def check_activity_status_student(connection, id_student, id_activity):
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT status_activity FROM activity_student WHERE id_student = %s AND id_activity = %s", (id_student, id_activity))
            result = cursor.fetchone()
            
            if result and result[0]== 'Aberta':
                return True
            elif result and result[0] == 'Concluída':
                return False
            else:
                return None
            
        except Error as e:
            print(f"Error checking activity status: {e}")
            return None
        finally:
            cursor.close()
            