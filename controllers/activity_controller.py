from flask import request
from db.firebase import *
from models.Actividy import Activity
from db.bd_mysql import db_connection

def create_activity_controller(data):
    
    id_group = data.get("id_group")
    id_content = data.get("id_content")
    description = data.get("description")
    deadline = data.get("deadline")

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
    

def update_activity_controller(data):
    id_activity = data.get("id_activity")

    if 'description' not in data and 'deadline' not in data:
        return {"message": "Nenhum campo enviado para atualização"}, 400
    
    if not id_activity:
        return {"message": "ID da atividade é obrigatório"}, 400

    connection = db_connection()

    result = Activity.update_activity_model(connection, id_activity, data)
    if result:
        return {"message": "Atividade atualizada com sucesso!"}, 200
    else:
        return {"message": "Atividade não encontrada"}, 404