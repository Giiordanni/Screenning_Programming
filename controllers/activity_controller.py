from flask import request
from db.firebase import *
from models.Actividy import Activity
from db.bd_mysql import db_connection
from datetime import datetime

def create_activity_controller(data):
    
    id_group = data.get("id_group")
    id_content = data.get("id_content")
    description = data.get("description")
    deadline = data.get("deadline")

    date_now = datetime.now()
    deadline = datetime.strptime(deadline, '%d/%m/%Y')
    date_now = datetime.strptime(date_now.strftime('%d/%m/%Y'))
    if deadline < date_now:
        return {"message": "Data limite inválida"}, 400

    connection = db_connection()

    activity = Activity()
    inserted_id = activity.create_activity_service(connection, id_group, id_content, description, deadline)
    if inserted_id is not None:
        return {"message": 'Atividade criada com sucesso!', "activity_id": inserted_id}, 200
    else:
        return {"message": "Falha ao criar atividade"}, 500

def get_activity_controller(data):
    id_group = data.get("id_group")
    id_content = data.get("id_content")

    connection = db_connection()

    result =  Activity.get_activity_model(connection, id_content, id_group)
    if result is not None:
        return {"activity": result}, 200
    else:
        return {"message": "Atividade não encontrada"}, 404
    

    
def get_all_activity_controller(data):
    id_group = data.get("id_group")

    connection = db_connection()

    result = Activity.get_all_activity_model(connection, id_group)
    if result is not None:
        return {"activity": result}, 200
    else:
        return {"message": "Atividade não encontrada"}, 404
    

def delete_activity_controller(id_activity):
    connection = db_connection()
    result = Activity.delete_activity_model(connection, id_activity)
    if result is not None:
        return {"message": "Atividade deletada com sucesso!"}, 200
    else:
        return {"message": "Atividade não encontrada"}, 404
    

def update_activity_controller(data, id_activity):

    if 'description' not in data and 'deadline' not in data and 'status_activity' not in data:
        return {"message": "Nenhum campo enviado para atualização"}, 400
    

    connection = db_connection()
    result = Activity.update_activity_model(connection, id_activity, data)
    if result:
        return {"message": "Atividade atualizada com sucesso!"}, 200
    else:
        return {"message": "Atividade não encontrada"}, 404


def verify_permission_user(id_teacher, id_activity):
    connection = db_connection()
    result = Activity.verify_permission_user_model(connection, id_teacher, id_activity)
    if result is not None:
        return True
    else:
        return False