import os
from flask import abort, jsonify
from models.Token import Token
from db.bd_mysql import db_connection
import jwt
import datetime

def create_token_controller(user_email, user_type, group_id, type_token):
    connection = db_connection()
    
    if not connection:
        return None, "Falha ao conectar com o banco de dados!", 500

    secretKey = os.getenv('SECRET_KEY')
    if not secretKey:
        return None, "Chave secreta não encontrada", 500

    try:
        token_exists = Token.get_token_by_user_email_and_type_service(connection, user_email, type_token)
        print(token_exists)
        if type_token == "password" and token_exists:
            return None, "Token já existe para este usuário nesta função", 400
        
        if token_exists and token_exists.get("groupId") == group_id and token_exists.get("email") == user_email:
            return None, "Token já existe para este usuário nesta função", 400

        payload = {
            'email': user_email,
            'user_type': user_type,
            'group_id': group_id,
            'exp': datetime.datetime.now() + datetime.timedelta(hours=72)
        }
        
        token = jwt.encode(payload, secretKey, algorithm='HS256')
        
        token_id = Token.create_token_service(connection, user_email, user_type, group_id, token, type_token)

        if token_id:
            return token, None, 201
        else:
            return None, "Falha ao criar token", 500
    except Exception as e:
        error_message = f"Erro ao criar token: {str(e)}"
        return None, error_message, 500
    finally:
        if connection:
            connection.close()



def delete_token_controller(user_email, token_type):
    connection = db_connection()
    
    if not connection:
        return jsonify({"message": "Falha ao conectar com o banco de dados!"}), 500
    
    try:
        token = Token.get_token_by_user_email_and_type_service(connection, user_email, token_type)
        
        if not token:
            return jsonify({"message": "Token não encontrado para o tipo especificado"}), 404
        
        if token_type not in ["password", "invite"]:
            return jsonify({"message": "Tipo de token inválido"}), 400
        
        deleted = Token.delete_token_service(connection, user_email, token_type)
        
        if deleted:
            return jsonify({"message": "Token deletado com sucesso"}), 200
        else:
            return jsonify({"message": "Falha ao deletar token"}), 500
    
    except Exception as e:
        return jsonify({"message": f"Erro interno no servidor: {str(e)}"}), 500
    
    finally:
        if connection:
            connection.close()


    
def get_groupId_by_token_controller(token):
    connection = db_connection()

    if connection:
        try:
            group_id = Token.get_group_id_by_token(connection, token)
        finally:
            connection.close()

        if not group_id:
            return jsonify({"message": "Token não existe"}), 404  
        return jsonify(group_id), 200 
    else:
        return jsonify({"message": "Falha ao conectar com o banco de dados!"}), 500
