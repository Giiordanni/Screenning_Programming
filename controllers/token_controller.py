import os
from flask import abort, jsonify
from models.Token import Token
from db.redis import redis_client
import jwt

def create_token_controller(user_email, user_type, group_id, type_token):

    redis = redis_client()

    secretKey = os.getenv('SECRET_KEY')
    if not secretKey:
        return None, "Chave secreta não encontrada", 500

    try:
        token_exists = Token.get_token_by_user_email_and_type_service(redis, user_email, type_token)
        if type_token == "password" and token_exists:
            return None, "Token já existe para este usuário nesta função", 400
        
        if token_exists and int(token_exists.get("group_id")) == group_id and token_exists.get("email") == user_email:
            return None, "Token já existe para este usuário nesta função", 400

        payload = {
            'email': user_email,
            'user_type': user_type,
            'group_id': group_id
        }
        
        token = jwt.encode(payload, secretKey, algorithm='HS256')
        
        token_id = Token.create_token_service(redis, user_email, user_type, group_id, token, type_token)

        if token_id:
            return token, None, 201
        else:
            return None, "Falha ao criar token", 500
    except Exception as e:
        error_message = f"Erro ao criar token: {str(e)}"
        return None, error_message, 500
    

def get_groupId_by_token_controller(email):
    try:
        redis = redis_client()
        group_id = Token.get_group_id_by_token(redis, 'invite', email)
        if not group_id:
            return jsonify({"message": "Token não existe"}), 404  
        return jsonify(group_id), 200 
    
    except:
        return jsonify({"message": "Falha ao conectar com o banco de dados!"}), 500
