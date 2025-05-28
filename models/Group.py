from mysql.connector import Error

class Group:
    def __init__(self, id_teacher, title, period, code_group):
        self.id_teacher = id_teacher
        self.title = title
        self.period = period
        self.code_group = code_group
        #self.students = students if students is not None else []

    def create_group_service(self, connection):
        try:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO group_table (id_teacher, title, period, code) VALUES (%s, %s, %s, %s)",
                (self.id_teacher, self.title, self.period, self.code_group))
            connection.commit()
            inserted_id = cursor.lastrowid 
            return inserted_id
            
        except Error as e:
            print(f"Error saving group to database: {e}")
        
        finally:
            cursor.close()


    @staticmethod
    def get_students_from_group_service(connection, id_group):
        with connection.cursor() as cursor:
            query = """
                SELECT p.nameTeacher, e.nameStudent, g.title, g.period, e.id, e.registrationStudent, g.code
                FROM 
                    group_table g
                JOIN 
                    professor p ON g.id_teacher = p.id
                LEFT JOIN 
                    student_group sg ON g.id_grupo = sg.id_grupo
                LEFT JOIN 
                    aluno e ON sg.id_aluno = e.id
                WHERE 
                    g.id_grupo = %s
                ORDER BY e.nameStudent, e.id
            """
            cursor.execute(query, (id_group,))
            results = cursor.fetchall()

        if not results:
            teacher = {
                "nameTeacher": "Professor não encontrado",
                "title": "Grupo não encontrado",
                "period": "Desconhecido"
            }
            students = []
        else:
            teacher = {
                "nameTeacher": results[0][0],
                "title": results[0][2],
                "period": results[0][3],
                "code": results[0][6]
            }

            students = [
                {
                    "nameStudent": row[1],
                    "idStudent": row[4],
                    "registrationStudent": row[5] or "N/A"
                }
                for row in results
                if row[1] is not None  
            ]

        return teacher, students

    @staticmethod
    def delete_student_from_group_service(connection, groupID, studentID):
        try:
            cursor = connection.cursor()
            connection.start_transaction()

            cursor.execute("DELETE FROM student_group WHERE id_grupo = %s AND id_aluno = %s", (groupID, studentID))

            cursor.execute("DELETE FROM activity_student WHERE id_student = %s AND id_activity IN (SELECT id_activity FROM activity WHERE id_group = %s)",(studentID, groupID))

            connection.commit()
            return True, "Usuário deletado do grupo com sucesso!"

        except Error as e:
            if connection:
                connection.rollback()
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def get_teacher_id_from_group_service(connection, id_group):
        cursor = connection.cursor()
        cursor.execute(f"SELECT id_teacher FROM group_table WHERE id_grupo = {id_group}")
        teacherID = cursor.fetchone()
        cursor.close()
        return teacherID[0]
    
    @staticmethod
    def get_group_code(connection, code_group):
        cursor = connection.cursor()
        cursor.execute("SELECT id_grupo FROM group_table WHERE code = %s", (code_group, ))
        id_group = cursor.fetchone()
        cursor.close()
        return id_group[0]

    @staticmethod
    def add_student_to_group_service(connection, group_id, student_id):
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO student_group (id_aluno, id_grupo) VALUES (%s, %s)",
                    (student_id, group_id)
                )
                connection.commit()
                inserted_id = cursor.lastrowid
                return inserted_id
        except Exception as e:
            print(f"Error adding student to group: {e}")
            return None
        
    @staticmethod
    def delete_group_service(connection, group_id):
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM group_table WHERE id_grupo = %s", (group_id,))
                connection.commit()

            return {"message": "Grupo excluído com sucesso"}, 200

        except Exception as e:
            print(f"Erro ao excluir o grupo: {e}")
            return {"message": "Erro ao excluir o grupo"}, 500
        
    @staticmethod
    def get_group_by_teacher_id_service(connection, teacher_id):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM group_table WHERE id_teacher = %s", (teacher_id,))
                results = cursor.fetchall()

                dados = [
                        {
                            "group_id": row[0],
                            "title": row[2],
                            "period": row[3],
                            "code": row[4]
                        }
                        for row in results
                ]

                return dados

        except Exception as e:
            print(f"Error getting group by teacher ID: {e}")
            return None
        

    def update_group_service(connection,field,value,group_id):
        try:
            with connection.cursor() as cursor:
                sql = f"UPDATE group_table SET {field} = %s WHERE id_grupo = %s" 
                cursor.execute(sql, (value,group_id,))
                connection.commit()
                return {"message": "Grupo atualizado com sucesso"}, 200

        except Exception as e:
            print(f"Error updating group: {e}")
            return {"message": "Erro ao atualizar o grupo"}, 500

    def upload_image_service(connection, group_id, image_url):
        try:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE group_table SET photoGroup = %s WHERE id_grupo = %s", (image_url, group_id))
                connection.commit()
                return {"message": "Imagem enviada com sucesso"}, 200

        except Exception as e:
            print(f"Error uploading image: {e}")
            return {"message": "Erro ao enviar a imagem"}, 500

    def get_student_group_by_id_service(connection, student_id, group_id):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM student_group WHERE id_aluno = %s AND group_id = %s", (student_id, group_id))
                group = cursor.fetchone()
                return group

        except Exception as e:
            print(f"Error getting student group by ID: {e}")
            return None



        