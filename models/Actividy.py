from mysql.connector import Error

class Activity:
    
    def create_activity_service(self, connection, id_group,id_content, description, deadline):
        try:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO activity (id_group, id_content, description, deadline) VALUES (%s, %s, %s, %s)",
                           (id_group, id_content, description, deadline))
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