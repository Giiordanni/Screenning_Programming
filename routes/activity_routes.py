from flask import request, jsonify, Blueprint

from controllers.activity_controller import *

from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity, get_jwt

activity_app = Blueprint("activity_app", __name__)

@activity_app.route("/api/activity", methods=["POST"])
@jwt_required()
def create_activity_route():

    type_user = get_jwt()["type"]
    if(type_user != "teacher"):
        return jsonify({"error": "Invalid user type"}), 400
    
    data = request.get_json()
    response, status_code = create_activity_controller(data)
    return jsonify(response), status_code


@activity_app.route("/api/activity", methods=["GET"])
@jwt_required()
def get_activity_route():

    id_content = request.args.get('id_content')
    id_group = request.args.get('id_group')
    
    data = {
        "id_content": id_content,
        "id_group": id_group
    }

    response, status_code = get_activity_controller(data)
    return jsonify(response), status_code


@activity_app.route("/api/activity/<id_activity>", methods=["DELETE"])
@jwt_required()
def delete_activity_route(id_activity):

    type_user = get_jwt()["type"]
    if(type_user != "teacher"):
        return jsonify({"error": "Invalid user type"}), 400
    
    id_teacher = get_jwt_identity()
    if not verify_permission_user(id_teacher, id_activity):
        return jsonify({"error": "Permission denied"}), 403

    try:
        response, status_code = delete_activity_controller(id_activity)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@activity_app.route("/api/activity/<id_activity>", methods=["PATCH"])
@jwt_required()
def update_activity_route(id_activity):

    type_user = get_jwt()["type"]
    if(type_user != "teacher"):
        return jsonify({"error": "Invalid user type"}), 400
    
    id_teacher = get_jwt_identity()
    if not verify_permission_user(id_teacher, id_activity):
        return jsonify({"error": "Permission denied"}), 403
    
    try:
        data = request.get_json()
        response, status_code = update_activity_controller(data, id_activity)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@activity_app.route('/api/activity/complete', methods=['GET'])
@jwt_required()
def complete_activity():
    
    type_user = get_jwt()["type"]
    if(type_user != "teacher"):
        return jsonify({"error": "Invalid user type"}), 400
    
    id_group = request.args.get('id_group')
    if not id_group:
        return jsonify({"error": "Parâmetro 'id_group' é obrigatório."}), 400

    result, status_code = status_activity_all(id_group)
    return jsonify(result), status_code


@activity_app.route('/api/activity/student/all', methods=['GET'])
@jwt_required()
def complete_activity_student():
    
    type_user = get_jwt()["type"]
    if(type_user != "student"):
        return jsonify({"error": "Invalid user type"}), 400

    id_student = get_jwt_identity()
    id_group = request.args.get('id_group')
    if not id_group:
        return jsonify({"error": "Parâmetro 'id_group' é obrigatório."}), 400

    result = student_activity_status(id_student, id_group)
    return jsonify(result), 200