import io
from bcrypt import gensalt, hashpw
from flask import Blueprint, current_app, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from controllers.teacher_controller import *
from datetime import datetime
from dateutil.relativedelta import relativedelta
from models.Email import send_verification_code
from middleware.global_middleware import verify_email_registered
from db.bd_postgres import db_connection
from db.redis import redis_client
import json

from models.Teacher import Teacher

teacher_app = Blueprint('teacher_app', __name__)

@teacher_app.route('/api/teacher', methods=['POST'])
def add_user_router():
    connection = db_connection()
    redis = redis_client()
    data = request.get_json()

    name = data.get('nameTeacher').lower()
    email = data.get('emailTeacher').lower()
    birth = data.get('birthTeacher')
    password = data.get('passwordTeacher')
    confirm_password = data.get('confirm_password_Teacher')
    

    if not all([name, email, birth, password, confirm_password]):
        return jsonify({"message": "All fields are required"}), 400
    
    if password != confirm_password:
        return jsonify({"message": "Passwords do not match!"}), 400

    if len(password) < 6:
        return jsonify({"message": "Password must have at least 6 characters"}), 400
    
    if len(password) > 20:
        return jsonify({"message": "Password must not exceed 20 characters"})
    
    if "@" not in email:
        return jsonify({"message": "Invalid email"}), 400
    
    date_now = datetime.now()
    birth = datetime.strptime(birth, '%d/%m/%Y')
    idade = relativedelta(date_now, birth)

    if idade.years < 15:
        return jsonify({"message": "invalid date"}), 400

    domain = email.split("@")[-1]
    allowed_domains = ["servidor.uepb.edu.br"]
    if domain not in allowed_domains:
        return jsonify({"message": "Only specific email domains are allowed"}), 401

    hashed_password = hashpw(password.encode('utf-8'), gensalt())

    data['passwordTeacher'] = hashed_password.decode('utf-8')
    data.pop('confirm_password_Teacher')  

    verifyEmail = verify_email_registered(connection, email)
    if verifyEmail:
        return jsonify({"message": "Email já cadastrado!"}), 400
    

    send_verification_code(email)

    redis.hset(f"user_data:{email}", mapping=data)
    redis.expire(f"user_data:{email}", 600)

    return jsonify({"message": "Código de verificação enviado para o email"}), 200

@teacher_app.route("/api/teacher", methods=['PATCH'])
@jwt_required()
def update_user():
    data = request.get_json()
    user_id = get_jwt_identity()
    if not data or len(data) == 0:
        return jsonify({"error": "Nenhum campo enviado para atualização"}), 400

    try:
        update_teacher_controller(user_id, data)
        return jsonify({"message": "Usuário atualizado"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@teacher_app.route("/api/teacher/<user_id>", methods=["DELETE"])
@jwt_required()
def delete_users(user_id):
    current_user_id = get_jwt_identity()
    response, status_code = delete_teacher_controller(current_user_id, user_id)
    return jsonify(response), status_code

@teacher_app.route('/alterarNome', methods=['POST'])
def rename_table():
    data = request.get_json()

    current_name = data.get('current_name')
    new_name = data.get('new_name')

    if not all([current_name, new_name]):
        return jsonify({"message": "All fields are required"}), 400
    response = Teacher.rename_table(current_name, new_name)
    return jsonify(response)

@teacher_app.route('/api/teacher/email/<email>', methods=['GET'])
def get_teacher_by_id_email(email):
    user = get_teacher_by_email_controller(email)
    if user:
        return jsonify(user)
    else:
        return jsonify({"message": "Usuário não encontrado!"}), 404

@teacher_app.route('/api/teachers', methods=['GET'])
def get_all_teachers():
    teachers = get_teacher_controller()
    return jsonify(teachers)

@teacher_app.route('/api/teacher/<user_id>', methods=['GET'])
def get_teacher_route(user_id):
    response = get_teacher_by_id_controller(user_id)
    return jsonify(response)

@teacher_app.route('/api/teacher/email/<email>', methods=['GET'])
def get_teacher_by_email(email):
    user = get_teacher_by_email_controller(email)
    if user:
        return jsonify(user)
    else:
        return jsonify({"message": "Usuário não encontrado!"}), 404
    
@teacher_app.route('/api/teacher/upload_image', methods=['PATCH'])
@jwt_required()
def upload_image_teacher_route():
    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        allowed_extensions = ['jpg', 'jpeg', 'png', 'gif']
        if file_extension not in allowed_extensions:
            raise ValueError(f"Unsupported file type. Allowed types are: {', '.join(allowed_extensions)}.")

        teacher_id = get_jwt_identity()
        destination_blob_name = f"teachers/{teacher_id}/profile_image.jpg"

        file_stream = io.BytesIO(file.read())
        image_url = upload_image_to_firebase(file_stream, destination_blob_name)

        upload_image_teacher_controller(image_url, teacher_id)
        
        return jsonify({"message": "File uploaded successfully", "file_url": image_url}), 200
    except ValueError as val_error:
        return jsonify({"error": str(val_error)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@teacher_app.route('/api/teacher/groups', methods=['GET'])
@jwt_required()
def get_groups_from_teacher_route():
    user_id = get_jwt_identity()
    response = get_groups_from_teacher_controller(user_id)
    return jsonify(response)

@teacher_app.route('/api/teacher/password', methods=['PUT'])
def update_password_routes():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    
    if not all([email, password, confirm_password]):
        return jsonify({"message": "All fields are required"}), 400
    
    if password != confirm_password:
        return jsonify({"message": "Passwords do not match!"}), 400

    if len(password) < 6:
        return jsonify({"message": "Password must have at least 6 characters"}), 400
    
    if len(password) > 20:
        return jsonify({"message": "Password must not exceed 20 characters"})
    
    hashed_password = hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')
  

    response = update_password_field_teacher_controller(email, hashed_password)
    return jsonify(response)