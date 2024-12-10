import os
from flask import jsonify
from mysql.connector import Error

secretKey = os.getenv('SECRET_KEY')

class Token:
    def __init__(self, email,type, group_id,user_id_sha, type_token):
        self.email = email
        self.type = type
        self.group_id = group_id
        self.user_id_sha = user_id_sha
        self.type_token = type_token


    @staticmethod
    def create_token_service(redis, user_email, type, group_id, user_id_sha, type_token):
        if(type_token == "invite"):
            token_data = {
                "email": user_email,
                "type": type,
                "group_id": group_id,
                "user_id_sha": user_id_sha,
                "type_token": type_token
                }
            time =  864000
        elif(type_token == "password"):
            token_data = {
                "email": user_email,
                "type": type,
                "user_id_sha": user_id_sha,
                "type_token": type_token
            }
            time = 600
            
        try:
            redis.hset(f"Token {type_token}:{user_email}", mapping=token_data)
            redis.expire(f"Token {type_token}:{user_email}", time)
            return user_id_sha
        except Error as e:
            print(f"Erro ao criar token no redis: {e}")
            return None
        

    @staticmethod
    def get_token_by_user_email_service(redis, user_email):
        try:
            token = redis.hgetall(f"Token invite:{user_email}")
            if not token:
                return None
            
            return token
        except Error as e:
            return None
        

    def get_group_id_by_token(redis, token_type, user_email):
        try:
            result = redis.hget(f"Token {token_type}:{user_email}", "group_id")
            if result is None:
                return None
            return result
        except Error as e:
            return jsonify(f"Error getting token from database: {e}")

    @staticmethod
    def get_token_by_user_email_and_type_service(redis, user_email, token_type):
        try:
            existing_token = redis.hgetall(f"Token {token_type}:{user_email}")

            if not existing_token:
                return None
        
            return existing_token
        except Exception as e:
            return None
    