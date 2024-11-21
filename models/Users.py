from aifc import Error

class User:
    def __init__(self, name, email, password, birth, gender=None, institution=None, formation=None, state=None, city=None, registration=None, image = None):
        self.id = None
        self.name = name
        self.email = email
        self.password = password
        self.birth = birth
        self.gender = gender
        self.institution = institution
        self.state = state
        self.city = city
        self.formation = formation
        self.registration = registration
        self.image = image


    def create_user_service(self, connection, user_type, user_data):
        cursor = connection.cursor()
        try:
            if user_type == 'aluno':
                cursor.execute("""
                    INSERT INTO aluno (nameStudent, emailStudent, birthStudent, passwordStudent) 
                    VALUES (%s, %s, %s, %s)
                """, (
                    user_data['nameStudent'], 
                    user_data['emailStudent'], 
                    user_data['birthStudent'], 
                    user_data['passwordStudent']
                ))
                connection.commit()
                inserted_id = cursor.lastrowid 
                return inserted_id

            elif user_type == 'professor':
                cursor.execute("""
                    INSERT INTO professor (nameTeacher, emailTeacher, birthTeacher, passwordTeacher)
                    VALUES (%s, %s, %s, %s)
                """, (
                    user_data['nameTeacher'], 
                    user_data['emailTeacher'], 
                    user_data['birthTeacher'], 
                    user_data['passwordTeacher']
                ))
                connection.commit()
                inserted_id = cursor.lastrowid 
                return inserted_id

        except Exception as e:
            print(f"Erro ao criar usuário: {e}")
            connection.rollback()
            return None

        finally:
            cursor.close()

    

    def update_user_service(connection, table_name, user_id, field, value):
        cursor = connection.cursor()

        sql = f"UPDATE {table_name} SET {field} = %s WHERE id = %s"

        cursor.execute(sql, (value, user_id))
        connection.commit()
        cursor.close()
    

    @staticmethod
    def get_user_by_id_service(connection, user_id, table_name):
        cursor = connection.cursor()
        try:
            cursor.execute(f"SELECT * FROM {table_name} WHERE id = %s", (user_id,))
            user = cursor.fetchone()

            if table_name == 'professor':
                if user:
                    return {
                        "id": user[0],
                        "name": user[1],
                        "email": user[2],
                        "password": user[3],
                        "birth": user[4],
                        "gender": user[5],
                        "institution": user[6],
                        "state": user[7],
                        "city": user[8],
                        "formation": user[9],
                        "registration": user[10],
                        "photo": user[11]
                        
                    }
                else:
                    return None
                
            elif table_name == 'aluno':
                if user:
                    return {
                        "id": user[0],
                        "name": user[1],
                        "email": user[2],
                        "password": user[3],
                        "birth": user[4],
                        "gender": user[5],
                        "institution": user[6],
                        "period": user[7],
                        "state": user[8],
                        "city": user[9],
                        "registration": user[10],
                        "photo": user[11],
                        "levelStudent"  : user[12]
                        
                    }
                else:
                    return None

        finally:
            cursor.close()


    @staticmethod
    def get_all_user_service(connection, table_name):
        cursor = connection.cursor()
        try:
            if table_name == 'aluno':
                cursor.execute(f"SELECT  id, nameStudent AS name, emailStudent AS email FROM {table_name}")
            elif table_name == 'professor':
                cursor.execute(f"SELECT id, nameTeacher AS name, emailTeacher AS email FROM {table_name}")
            else:
                raise ValueError("Invalid table name")

            users = cursor.fetchall()
            return users

        except Exception as e:
            print(f"Erro ao buscar usuários: {e}")
            return []

        finally:
            cursor.close()

    
    @staticmethod
    def delete_user_service(connection, user_id, table_name):
        cursor = connection.cursor()
        cursor.execute(f"DELETE FROM {table_name} WHERE id = %s", (user_id,))
        connection.commit()
        cursor.close()


    @staticmethod
    def get_user_by_email_service(connection, email, table_name, email_column):
        cursor = connection.cursor()
        try:
            cursor.execute(f"SELECT * FROM {table_name} WHERE {email_column} = %s", (email,))
            user = cursor.fetchone()  

            if table_name == 'professor':
                if user:
                    return {
                        "id": user[0],
                        "name": user[1],
                        "email": user[2],
                        "password": user[3],
                        "birth": user[4],
                        "gender": user[5],
                        "institution": user[6],
                        "state": user[7],
                        "city": user[8],
                        "formation": user[9],
                        "registration": user[10],
                        "photo": user[11]
                        
                    }
                else:
                    return None
                
            elif table_name == 'aluno':
                if user:
                    return {
                        "id": user[0],
                        "name": user[1],
                        "email": user[2],
                        "password": user[3],
                        "birth": user[4],
                        "gender": user[5],
                        "institution": user[6],
                        "period": user[7],
                        "state": user[8],
                        "city": user[9],
                        "registration": user[10],
                        "photo": user[11]
                        
                    }
                else:
                    return None

        finally:
            cursor.close()


    @staticmethod
    def get_all_emails_service(connection):
        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT emailStudent AS email FROM aluno
                UNION
                SELECT emailTeacher AS email FROM professor
            """)
            emails = cursor.fetchall()
        finally:
            cursor.close()
        return emails



    @classmethod
    def rename_table(cls, connection, current_name, new_name):
        try:
            cursor = connection.cursor()
            cursor.execute(f"ALTER TABLE {current_name} RENAME TO {new_name}")
            connection.commit()
            cursor.close()
            print(f"Tabela '{current_name}' renomeada para '{new_name}' com sucesso.")
            return True
        except Error as e:
            print(f"Erro ao tentar renomear a tabela: {e}")
            return False

    def get_email_by_id(connection, user_id, type):
        cursor = connection.cursor()
        try:
            if type == 'student':
                cursor.execute(f"SELECT emailStudent AS email FROM aluno WHERE id = %s", (user_id,))
                email = cursor.fetchone()
                if email:
                    return email
            cursor.execute(f"SELECT emailTeacher AS email FROM teacher WHERE id = %s", (user_id,))
            email = cursor.fetchone()
            if email:
                return email
            else:
                return None
        finally:
            cursor.close()

    def upload_image_service(connection, user_id, table_name, fieldName,imagePath):
        cursor = connection.cursor()
        try:
            cursor.execute(f"UPDATE {table_name} SET {fieldName} = %s WHERE id = %s", (imagePath, user_id))
            connection.commit()
            return True
        except Exception as e:
            print(f"Erro ao atualizar foto: {e}")
            return False
        finally:
            cursor.close()

    def get_groups_from_user_service(connection, user_id, user_type):
        cursor = connection.cursor()
        try:
            if user_type == 'aluno':
                cursor.execute("""
                    SELECT s.id_grupo, g.id_teacher, g.title,g.period, t.nameTeacher
                    FROM 
                        student_group s
                    JOIN 
                        group_table g ON g.id_grupo = s.id_grupo
                    JOIN 
                        professor t ON t.id = g.id_teacher
                    WHERE 
                        s.id_aluno = %s
                    """, (user_id,))
                results = cursor.fetchall()
                return [{"id_group": result[0], "id_teacher":result[1], "title":result[2],"period":result[3], "teacher":result[4]} for result in results]
            else:
                cursor.execute("SELECT id_grupo, id_teacher, title, period, photoGroup FROM group_table WHERE id_teacher = %s", (user_id,))
                results = cursor.fetchall()
                return [
                    {
                        "id_group": result[0],
                        "id_teacher": result[1],
                        "title": result[2],
                        "period": result[3],
                        "photoGroup": result[4]
                    } for result in results
                ]
        except Exception as e:
            print(f"Erro ao buscar grupos: {e}")
            return None  
        finally:
            cursor.close()

    def get_id_by_email_service(connection, email, table_name, email_column):
        cursor = connection.cursor()
        try:
            cursor.execute(f"SELECT id FROM {table_name} WHERE {email_column} = %s", (email,))
            user_id = cursor.fetchone()
            if user_id:
                return user_id
            else:
                return None
        finally:
            cursor.close()

    def update_password_field(connection, email, email_name, table_name, passord_name, password):
        cursor = connection.cursor()
        try:
            cursor.execute(f"UPDATE {table_name} SET {passord_name} = %s WHERE {email_name} = %s", (password, email,))
            connection.commit()
            return True
        except Exception as e:
            print(f"Erro ao atualizar senha: {e}")
            return False
        finally:
            cursor.close()