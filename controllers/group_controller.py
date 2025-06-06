import base64
import bcrypt
from flask import request
from db.firebase import *
from models.Group import Group
from db.bd_mysql import db_connection
import random
import string
from models.Actividy import Activity

def create_group_controller(teacherId, data):

    id_teacher = teacherId
    name = data.get("title").lower()
    period = data.get("period")

    period_verification = period.split(".")[1]
    if int(period_verification) > 2 and int(period_verification) < 1:
        return {"message": "Período inválido"}, 400
    
    code_group = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

    connection = db_connection()
    if connection:

        group = Group(
            id_teacher,
            name,
            period,
            code_group
            )
        inserted_id = group.create_group_service(connection)
        connection.close()
        
        if inserted_id is not None:
            return {"message": 'Grupo criado com sucesso!', "group_id": inserted_id}, 200
        else:
            return {"message": "Falha ao criar usuário"}, 500
    else:
        return {"message": "Falha ao conectar com o banco de dados!"}, 500
        

def delete_student_from_group_controller(current_user_id, group_id, student_id):
    connection = db_connection()
    if not connection:
        return {"message": "Falha ao conectar com o banco de dados!"}, 500
    
    try:
        id_teacher = Group.get_teacher_id_from_group_service(connection, group_id)
        if int(current_user_id) != id_teacher: 
            return {"message": "Sem permissão para deletar"}, 400
        
        success, message = Group.delete_student_from_group_service(connection, group_id, student_id)
        if not success:
            return {"message": message}, 500

        return {"message": "Usuário deletado do grupo com sucesso!"}, 200
    
    except Exception as e:
        return {"message": f"Erro ao deletar o usuário: {e}"}, 500
    finally:
        connection.close()

def add_student_to_group_controller(student_id, group_id = None, code = None):
    connection = db_connection()
    try:
        if group_id is None and code is not None:
            group_id = Group.get_group_code(connection, code)

        if group_id is None:
            return {"message": "Grupo não encontrado"}, 404
        
        group_id = group_id[0]
        _, students = Group.get_students_from_group_service(connection, group_id)
        if students is not None:
            for student in students:
                if str(student["idStudent"]) == str(student_id):
                    return {"message": "Estudante já está no grupo"}, 400

        inserted_id = Group.add_student_to_group_service(connection, group_id, student_id)
        
        if inserted_id is not None:
            activitys = Activity.get_status_activity_all(connection, group_id, student_id)
            ids_activitys = [activitys["id_activity"] for activitys in activitys]

            response = Activity.add_student_to_activity(connection, int(student_id), ids_activitys)
            if response:
                message = "Estudante adicionado ao grupo e atividades atualizadas"
            else:
                message = "Estudante adicionado ao grupo, mas falha ao atualizar atividades"

            return {"message": message}, 200
        else:
            return {"message": "Falha ao adicionar estudante ao grupo. "}, 500
    
    except Exception as e:
        print(f"Erro ao adicionar estudante ao grupo: {e}")
        return {"message": "Erro interno do servidor"}, 500

    finally:
        connection.close()


def get_students_from_group_controller(id_group,num_pag):
    connection = db_connection()
    start_index = (int(num_pag) - 1) * 5
    end_index = start_index + 5

    teacher, students = Group.get_students_from_group_service(connection, id_group)
    
    students = students[start_index:end_index]

    return {"Group": teacher,"Students":students}, 200

def get_all_students_controller(id_group):
    connection = db_connection()
    teacher,students = Group.get_students_from_group_service(connection, id_group)
    return {"Group":teacher,"Students": students}, 200

def delete_group_controller(current_user_id, group_id):
    connection = db_connection()
    if not connection:
        return {"message": "Falha ao conectar com o banco de dados!"}, 500
    try:
        
        if int(current_user_id) != Group.get_teacher_id_from_group_service(connection, group_id):
            return {"message": "Sem permissão para deletar"}, 400
        Group.delete_group_service(connection, group_id)
        return {"message": "Grupo deletado com sucesso!"}, 200
    except Exception as e:
        return {"message": f"Erro ao deletar o grupo: {e}"}, 500
    finally:
        connection.close()

def get_group_by_teacher_id_controller(teacher_id):
    connection = db_connection()
    if not connection:
        return {"message": "Falha ao conectar com o banco de dados!"}, 500
    try:
        groups = Group.get_group_by_teacher_id_service(connection, teacher_id)
        return {"groups": groups}, 200
    except Exception as e:
        return {"message": f"Erro ao buscar grupos: {e}"}, 500
    finally:
        connection.close()

def update_group_controller(teacher_id, group_id, data):
    connection = db_connection()
    if not connection:
        return {"message": "Falha ao conectar com o banco de dados!"}, 500
    
    teacherId_group = Group.get_teacher_id_from_group_service(connection, group_id)
    if int(teacher_id) != teacherId_group:
        return {"message": "Sem permissão para atualizar"}, 400
    
    try:
        for field, value in data.items():
            Group.update_group_service(connection, field, value, group_id)
        return {"message": 'Atualização feita com sucesso!'}, 200
    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        connection.close()

def upload_image_group_controller(image_url, group_id):
    connection = db_connection()
    if connection:
        try:
            sanitized_group_id = secure_filename(group_id)
                        
            Group.upload_image_service(connection, sanitized_group_id, image_url)
            return image_url
        except Exception as e:
            raise Exception(f"Error uploading student's image: {str(e)}")
    else:
        raise Exception("Database connection failed.")
    

