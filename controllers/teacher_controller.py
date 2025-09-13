from models.Teacher import Teacher
from db.bd_postgres import db_connection
from db.firebase import *

from middleware.global_middleware import (
    verify_email_teacher_registered,
    verify_id_exists
    ,verify_email_registered,
    create_token)

def add_teacher_controller(data):
    connection = db_connection()

    name = data.get('nameTeacher').lower()
    email = data.get('emailTeacher').lower()
    birth = data.get('birthTeacher')
    password = data.get('passwordTeacher')

    if connection:
        teacher = Teacher(
            name=name,
            email=email,
            birth=birth,
            password=password
        )
        inserted_id = teacher.create_teacher_service(connection)

        if inserted_id is not None:
            try:
                user = Teacher.get_teacher_by_id_service(connection, inserted_id)
                if user is None:
                    print("Usuário professor não encontrado após inserção")
                    return {"message": "Erro: usuário não encontrado após criação"}, 500
                access_token = create_token(user, 'teacher')
                print(access_token)
            except Exception as e:
                print(f"Erro ao criar token ou buscar usuário: {e}")
                return {"message": "Erro ao criar usuário, mas usuário foi salvo"}, 500

            connection.close()
            return {"message": "Usuário criado com sucesso!", "user_id": inserted_id, "access_token": access_token}, 201
        else:
            return {"message": "Erro ao criar usuário"}, 500
        
    else:
        return {"message": "Falha ao conectar com o banco de dados!"}, 500

def get_teacher_controller():
    connection = db_connection()
    if connection:
        users = Teacher.get_all_teacher_service(connection)
        connection.close()
        return users
    else:
        return {"message": "Falha ao conectar com o banco de dados!"}, 500

def update_teacher_controller(user_id, data):
    connection = db_connection()
    if connection:
        verify_id_exists(connection, user_id, 'teacher')
        if 'emailTeacher' in data:
            verify_email_teacher_registered(connection, data.get('emailTeacher').lower())
        try:
            for field, value in data.items():
                Teacher.update_teacher_service(connection, user_id, field, value)
            connection.close()
            return {"message": 'Atualização feita com sucesso!'}, 200
        except Exception as e:
            return {"error": str(e)}, 500
    else:
        return {"error": "Falha ao conectar com o banco de dados!"}, 500


def delete_teacher_controller(current_user_id, user_id):
    connection = db_connection()
    if not connection:
        return {"message": "Falha ao conectar com o banco de dados!"}, 500
    
    verify_id_exists(connection,user_id,'teacher')
    try:
        if current_user_id != user_id:
            return {"message": "Sem permissão para deletar"}, 400

        
        Teacher.delete_teacher_service(connection, user_id)
        return {"message": "User deletado"}, 200

    except Exception as e:
        return {"message": f"Erro ao deletar o usuário: {e}"}, 500

    finally:
        connection.close()

    
def get_teacher_by_email_controller(email):
    connection = db_connection()
    if connection:
        user = Teacher.get_teacher_by_email_service(connection, email)
        connection.close()
        return user
    else:
        return {"message": "Falha ao conectar com o banco de dados!"}, 500
    
def get_teacher_by_id_controller(user_id):
    connection = db_connection()
    if connection:
        verify_id_exists(connection,user_id,'teacher')
        user = Teacher.get_teacher_by_id_service(connection, user_id)
        connection.close()
        return user
    else:
        return {"message": "Falha ao conectar com o banco de dados!"}, 500

def upload_image_teacher_controller(image_url, teacher_id):
    connection = db_connection()
    if connection:
        try:
            sanitized_teacher_id = secure_filename(teacher_id)
                        
            Teacher.upload_image_service(connection, sanitized_teacher_id, image_url)
            return image_url
        except Exception as e:
            raise Exception(f"Error uploading student's image: {str(e)}")
    else:
        raise Exception("Database connection failed.")
    
def get_groups_from_teacher_controller(user_id):
    connection = db_connection()
    if connection:
        verify_id_exists(connection,user_id,'teacher')
        groups = Teacher.get_groups_from_teacher_service(connection, user_id)
        connection.close()
        return groups
    else:
        return {"message": "Falha ao conectar com o banco de dados!"}, 500

def update_password_field_teacher_controller(email, password):
    connection = db_connection()
    if connection:
        try:
            Teacher.update_password_field_teacher(connection, email, 'emailTeacher', 'professor', 'passwordTeacher', password)
            return {"message": "Senha atualizada com sucesso!"}, 200
        except Exception as e:
            return {"message": f"Erro ao atualizar senha: {e}"}, 500
        finally:
            connection.close()
    else:
        return {"message": "Falha ao conectar com o banco de dados!"}, 500