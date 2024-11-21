from models.Users import User


class Teacher(User):
    def __init__(self, name, email, password, birth, gender=None, institution=None, certificate=None, state=None, city=None, registration = None, image = None):
        super().__init__(name, email, password, birth, gender, institution, certificate, state, city, registration, image)
        
    def to_db_format(self):
        return {
            'nameTeacher': self.name,
            'emailTeacher': self.email,
            'passwordTeacher': self.password,
            'birthTeacher': self.birth,
            'genderTeacher': self.gender,
            'institutionTeacher': self.institution,
            'stateTeacher': self.state,
            'cityTeacher': self.city,
            'formationTeacher': self.formation,
            'registrationTeacher': self.registration,
            'photoTeacher': self.image
        }

    def create_teacher_service(self, connection):
        teacher_data = self.to_db_format()
        return self.create_user_service(connection, 'professor', teacher_data)

    def update_teacher_service(connection, user_id, field, value):
        User.update_user_service(connection, 'professor', user_id, field, value)

    @staticmethod
    def get_all_teacher_service(connection):
        return User.get_all_user_service(connection, 'professor')
    
    @staticmethod
    def delete_teacher_service(connection, user_id):
        return User.delete_user_service(connection, user_id, 'professor')
    
    @staticmethod
    def get_teacher_by_email_service(connection, email):
        return User.get_user_by_email_service(connection, email, 'professor', 'emailTeacher')
    
    @staticmethod
    def get_teacher_by_id_service(connection, user_id):
        return User.get_user_by_id_service(connection, user_id, 'professor')

    @staticmethod
    def get_email_by_id(connection, user_id):
        return User.get_email_by_id(connection, user_id, 'professor')
    
    def upload_image_service(connection, user_id, imagePath):
        return User.upload_image_service(connection, user_id, 'professor', 'photoTeacher', imagePath)

    def get_groups_from_teacher_service(connection, user_id):
        return User.get_groups_from_user_service(connection, user_id, 'professor')
    
    def update_password_field_teacher(connection, email, email_name_teacher, table_name, password_name_teacher, password):
        return User.update_password_field(connection, email, email_name_teacher, table_name, password_name_teacher, password)
