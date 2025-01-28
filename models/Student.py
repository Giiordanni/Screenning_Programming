from models.Users import User


class Student(User):
    def __init__(self, name, email, password, levelStudent = 0.0, birth=None, gender=None, institution=None, period=None, state=None, city=None, registration=None, image=None):
        super().__init__(name, email, password, birth, gender, institution, state, city, registration,image, levelStudent)
        self.period = period

    def to_db_format(self):
        return {
            'nameStudent': self.name,
            'emailStudent': self.email,
            'passwordStudent': self.password,
            'birthStudent': self.birth,
            'genderStudent': self.gender,
            'institutionStudent': self.institution,
            'periodStudent': self.period,
            'stateStudent': self.state,
            'cityStudent': self.city,
            'registrationStudent': self.registration,
            'photoStudent': self.image
        }

        
    def create_student_service(self, connection):
        try:
            student_data = self.to_db_format()
            return self.create_user_service(connection, 'aluno', student_data)
        except Exception as e:
            return None

    def get_student_lvl_service(connection, user_id):
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT levelStudent FROM aluno WHERE id = %s", (user_id,))
            result = cursor.fetchone()
            if result:
                level = result[0]
                return level
            else:
                return None
        finally:
            cursor.close()

    def update_levelStudent_service(connection, user_id, level):
        cursor = connection.cursor()
        try:
            cursor.execute("UPDATE aluno SET levelStudent = %s WHERE id = %s", (level, user_id))
            connection.commit()
            return True
        except Exception as e:
            return False
        finally:
            cursor.close()
            connection.close()
    
    def update_student_service(connection, user_id, field, value):
        User.update_user_service(connection, 'aluno', user_id, field, value)

    def get_groups_from_student_service(connection, user_id):
        return User.get_groups_from_user_service(connection, user_id, 'aluno')

    @staticmethod
    def get_all_student_service(connection):
        return User.get_all_user_service(connection, 'aluno')
    
    @staticmethod
    def get_student_by_id_service(connection, user_id):
        return User.get_user_by_id_service(connection, user_id, 'aluno')
    
    @staticmethod
    def get_student_by_email_service(connection, email):
        return User.get_user_by_email_service(connection, email, 'aluno', 'emailStudent')

    @staticmethod
    def delete_student_service(connection, user_id):
        return User.delete_user_service(connection, user_id, 'aluno')
    
    @staticmethod
    def get_email_by_id(connection, user_id):
        return User.get_email_by_id(connection, user_id, 'aluno')
    
    def upload_image_service(connection, user_id, image_path):
        return User.upload_image_service(connection, user_id, 'aluno', 'photoStudent', image_path)
    
    def get_id_by_email_service(connection, email):
        return User.get_id_by_email_service(connection, email, 'aluno', 'emailStudent')
    
    def get_studentId_by_email_service(connection, email):
        return User.get_id_by_email_service(connection, email, 'aluno', 'emailStudent')
    
    def update_password_field_student(connection, email, email_name_student, table_name, password_name_student, password):
        return User.update_password_field(connection, email, email_name_student, table_name, password_name_student, password)
    
