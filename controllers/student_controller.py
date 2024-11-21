from models.Student import Student
from db.bd_mysql import db_connection
from werkzeug.utils import secure_filename
from middleware.global_middleware import (
    verify_id_exists,
    verify_email_student_registered,
    create_token)



def add_student_controller(data):
    try:
        connection = db_connection()

        if not isinstance(data, dict):
            return {"message": "Dados não são json"}, 500

        name = data.get('nameStudent').lower()
        email = data.get('emailStudent').lower()
        birth = data.get('birthStudent')
        password = data.get('passwordStudent')
        
        if connection:
            student = Student(
                name=name,
                email=email,
                birth=birth,
                password=password
            )

            inserted_id = student.create_student_service(connection)

            if inserted_id is not None:
                try:
                    user = Student.get_student_by_id_service(connection, inserted_id)
                    access_token = create_token(user, 'student')
                except Exception as e:
                    print(f"Erro ao criar token ou buscar usuário: {e}")
                    return {"message": "Erro ao criar usuário, mas usuário foi salvo"}, 500

                connection.close()
                return {"message": "Usuário criado com sucesso!", "user_id": inserted_id, "access_token": access_token}, 201
            else:
                return {"message": "Erro ao criar usuário"}, 500
        else:
            return {"message": "Falha ao conectar com o banco de dados!"}, 500

    except Exception as e:
        print(f"Erro no controlador de aluno: {e}")
        return {"message": "Internal Server Error"}, 500


def get_students_controller():
    connection = db_connection()
    if connection:
        users = Student.get_all_student_service(connection)
        connection.close()
        return users
    else:
        return {"message": "Falha ao conectar com o banco de dados!"}, 500

def update_student_controller(user_id, data):
    connection = db_connection()
    if connection:
        verify_id_exists(connection, user_id, 'student')
        if 'emailStudent' in data:
            verify_email_student_registered(connection, data.get('emailStudent').lower())
            
        try:
            for field, value in data.items():
                Student.update_student_service(connection, user_id, field, value)
            connection.close()
            return {"message": 'Atualização feita com sucesso!'}, 200
        except Exception as e:
            return {"error": str(e)}, 500
    else:
        return {"error": "Falha ao conectar com o banco de dados!"}, 500


def delete_student_controller(current_user_id, user_id):
    connection = db_connection()
    if not connection:
        return {"message": "Falha ao conectar com o banco de dados!"}, 500
    verify_id_exists(connection,user_id,'student')
    try:
        if current_user_id != user_id:
            return {"message": "Sem permissão para deletar"}, 400

        Student.delete_student_service(connection, user_id)
        return {"message": "User deletado"}, 200

    except Exception as e:
        return {"message": f"Erro ao deletar o usuário: {e}"}, 500

    finally:
        connection.close()

def get_student_by_id_controller(user_id):
    connection = db_connection()
    if connection:
        verify_id_exists(connection,user_id,'student')
        user = Student.get_student_by_id_service(connection, user_id)
        connection.close()
        return user
    else:
        return {"message": "Falha ao conectar com o banco de dados!"}, 500
    
def get_student_by_email_controller(email):
    connection = db_connection()
    if connection:
        user = Student.get_student_by_email_service(connection, email)
        connection.close()
        return user
    else:
        return {"message": "Falha ao conectar com o banco de dados!"}, 500
    
def upload_image_student_controller(image_url, student_id):
    connection = db_connection()
    if connection:
        try:
            sanitized_student_id = secure_filename(student_id)
            Student.upload_image_service(connection, sanitized_student_id, image_url)
            return image_url
        except Exception as e:
            raise Exception(f"Error uploading student's image: {str(e)}")
    else:
        raise Exception("Database connection failed.")

def get_groups_from_student_controller(user_id):
    connection = db_connection()
    if connection:
        verify_id_exists(connection,user_id,'student')
        groups = Student.get_groups_from_student_service(connection, user_id)
        connection.close()
        return groups
    else:
        return {"message": "Falha ao conectar com o banco de dados!"}, 500
    
def get_id_by_email_controller(email):
    connection = db_connection()
    if connection:
        user = Student.get_student_by_email_service(connection, email)
        connection.close()
        return user['id']
    else:
        return {"message": "Falha ao conectar com o banco de dados!"}, 500
    
def update_password_field_student_controller(email, password):
    connection = db_connection()
    if connection:
        try:
            Student.update_password_field_student(connection, email, 'emailStudent', 'aluno', 'passwordStudent', password)
            return {"message": "Senha atualizada com sucesso!"}, 200
        except Exception as e:
            return {"message": f"Erro ao atualizar senha: {e}"}, 500
    else:
        return {"message": "Falha ao conectar com o banco de dados!"},

def update_levelStudent_controller(user_id, level):
    connection = db_connection()
    if connection:
        verify_id_exists(connection, user_id, 'student')
        try:
            Student.update_levelStudent_service(connection, user_id, level)
            return {"message": "Nível do aluno atualizado com sucesso!"}, 200
        except Exception as e:
            return {"message": f"Erro ao atualizar nível do aluno: {e}"}, 500
    else:
        return {"message": "Falha ao conectar com o banco de dados!"}, 500