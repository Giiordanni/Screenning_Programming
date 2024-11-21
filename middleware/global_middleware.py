from flask import abort
#from models.Student import Student
from models.Teacher import Teacher
from db.bd_mysql import db_connection
from models.Student import Student
from models.Users import User
from models.Group import Group

@staticmethod
def verify_email_registered(connection, email):
    user = Student.get_student_by_email_service(connection, email)
    if not user:
        user = Teacher.get_teacher_by_email_service(connection, email)
    return user is not None

def verify_email_student_registered(connection, email):
    user = Student.get_student_by_email_service(connection, email)
    if user:
        return {"message": "Email já cadastrado!"}, 400
    
def verify_email_teacher_registered(connection, email):
    user = Teacher.get_teacher_by_email_service(connection, email)
    if user:
        return {"message": "Email já cadastrado!"}, 400
    
@staticmethod
def verify_id_exists(connection, user_id, user_type):
    if user_type == 'student':
        user = Student.get_student_by_id_service(connection, user_id)
    elif user_type == 'teacher':
        user = Teacher.get_teacher_by_id_service(connection, user_id)
    if not user:
        return abort(404, description="Usuário não encontrado")
    return user

def verify_student_is_in_group(connection, user_email, group_id):
    user = Student.get_student_by_email_service(connection, user_email)
    if not user:
        return abort(404, description="Usuário não encontrado")
    userId = Student.get_studentId_by_email_service(connection, user_email)
    group = Group.get_student_group_by_id_service(connection, userId)
    if group['group_id'] != group_id:
        return abort(404, description="Grupos diferentes")
    return user
