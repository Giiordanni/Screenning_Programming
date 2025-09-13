from email.headerregistry import Group
import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
import jwt
from controllers.student_controller import get_id_by_email_controller
from db.bd_postgres import db_connection
from middleware.global_middleware import verify_student_is_in_group
from models.Student import Student
from models.Teacher import Teacher
from models.Group import Group
from models.Email import sendEmail, verify_code, user_data, delete_data
from passlib.hash import pbkdf2_sha256 as sha256
from controllers.token_controller import create_token_controller
from controllers.student_controller import add_student_controller
from controllers.teacher_controller import add_teacher_controller
import json

from db.redis import redis_client
from models.Token import Token
from models.Users import User
from models.Email import send_verification_code


email_app = Blueprint("email_app", __name__)

@email_app.route('/api/send_verification_code/<email>', methods=['POST'])
def verification_code(email):
    try:
        data = request.get_json()
        code = data.get('code')
        email = email.lower().strip()
        resendCode = data.get('resendCode', False)

        if resendCode == True:
            send_verification_code(email)
            return jsonify({'message': 'Código de verificação reenviado com sucesso.'}), 200

        if not code:
            return jsonify({'error': 'Código não fornecido'}), 400
        
        if not verify_code(email, code):
            return ({'message': 'Código inválido'}), 400
        
        dataUser = user_data(email)

        if not dataUser:
            return jsonify({"message": "Os dados do usuário expiraram ou são inválidos."}), 400
        
        delete_data(f"verification_code:{email}")
        delete_data(f"user_data:{email}")
        
        if email.split("@")[-1] == "aluno.uepb.edu.br":
            result = add_student_controller(dataUser)
        else: 
            result = add_teacher_controller(dataUser)

        if len(result) == 2:
            response,status_code = result
            return jsonify(response), status_code

        response, access_token, status_code = result
        return jsonify(response), status_code, access_token
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@email_app.route('/api/send_email', methods=['POST'])
def sendEmail_route():
    try:
        data = request.json
        subject = data['subject']
        recipient = data['recipient']
        body = data['body']
        html_body = data.get('html_body')
        sendEmail(subject, recipient, body,html_body)

        return jsonify({'message': 'E-mail enviado com sucesso'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@email_app.route('/api/forgetPassword', methods=['POST'])
def forgetPassword():
    try:
        data = request.get_json()
        recipient = data.get('email')
        if not recipient or not isinstance(recipient, str):
            return jsonify({'error': 'Email inválido'}), 400

        connection = db_connection()
        if not connection:
            return jsonify({'error': 'Erro ao conectar com o banco de dados'}), 500
        
        if "servidor" in recipient:
            user_type = "teacher"
        elif "aluno" in recipient:
            user_type = "student"
        else:
            return jsonify({'error': "Domínio não permitido"}), 500 
        token, error_message, status_code = create_token_controller(recipient, user_type, "", 'password')

        if not token:
            return {"error": error_message}, status_code


        link = f'screenning-programming2024.vercel.app/html/nova-senha.html?token={token}'
        subject = 'Recuperação de senha'
        
        with open('templates/forget_password.html', 'r', encoding='utf-8') as file:
            body = file.read()
        
        body = body.replace('{link}', link)

        sendEmail(subject, recipient, body)

        return jsonify({'message': 'E-mail enviado com sucesso'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@email_app.route('/api/groupInvite', methods=['POST'])
@jwt_required()
def group_invite():
    connection = db_connection()
    if not connection:
        return jsonify({'error': 'Erro ao conectar com o banco de dados'}), 500
    try:
        data = request.get_json()
        teacherId = get_jwt_identity()
        groupName = data['groupName']
        groupId = data['groupId']
        recipient = data['recipient']
                
        token, token_id, status_code = create_token_controller(recipient, 'student', int(groupId), 'invite')
        if status_code != 201:
            return jsonify({'error': token_id}), status_code
        
        link = f"http://screenning-programming2024.vercel.app/html/pagina-redirecionamento.html?token={token}"
        subject = 'Convite para grupo'

        if not isinstance(recipient, str):
            raise ValueError("Email inválido")
        
        teacher = Teacher.get_teacher_by_id_service(connection, teacherId)
        teacherName = teacher['name'] if teacher else 'Professor Desconhecido'
        
        with open('templates/group_invite.html', 'r', encoding='utf-8') as file:
            html = file.read()
            body = html.format(group=groupName, teacher=teacherName, link=link)
        
        sendEmail(subject, recipient, body)
        
        return jsonify({
            'message': 'E-mail enviado com sucesso',
            'token': token,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    
@email_app.route('/api/verifyInvite', methods=['GET'])
@jwt_required()
def verify_invite():
    try:
        connection = db_connection()
        redis = redis_client()
        user = get_jwt()
        userEmail = User.get_email_by_id(connection, user["id"], user["type"])
        userEmail = str(userEmail[0])
        userEmail = userEmail.lower().strip()
        
        token = Token.get_token_by_user_email_service(redis, userEmail)
        if token["email"] != userEmail:
            return jsonify({"Emails incompativeis"})
        
        delete_data(f"Token invite:{userEmail}")
        return jsonify({token})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# # # ATALHO PARA COMENTAR == CTRL + K -> CTRL + C