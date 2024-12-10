from flask import request, jsonify, Blueprint

from controllers.group_controller import *


from flask_jwt_extended import get_jwt_identity, get_jwt
from flask_jwt_extended import jwt_required

group_app = Blueprint("group_app", __name__)

@group_app.route("/api/group", methods=["POST"])
@jwt_required()
def create_group_route():
    data = request.get_json()
    id_teacher = get_jwt_identity()
    type_user = get_jwt()["type"]
    
    if(type_user != "teacher"):
        return jsonify({"error": "Invalid user type"}), 400

    response, status_code = create_group_controller(id_teacher, data)
    return jsonify(response), status_code

@group_app.route("/api/group/student/<groupId>", methods=["PUT"])
@jwt_required()
def add_student_to_group_route(groupId):
    data = request.get_json()
    studentId = data["studentId"]
    response, status_code = add_student_to_group_controller(groupId, studentId)
    return jsonify(response), status_code

@group_app.route("/api/group/student/<id_group>", methods=["GET"])
@jwt_required()
def get_students_from_group_route(id_group):
    num_pag = request.args.get("num_pag")
    response, status_code = get_students_from_group_controller(id_group,num_pag)
    return jsonify(response), status_code

@group_app.route("/api/group/<id_group>", methods=["GET"])
@jwt_required()
def get_all_students_group_routes(id_group):
    response, status_code = get_all_students_controller(id_group)
    return jsonify(response), status_code

@group_app.route("/api/group/student/<groupId>", methods=["DELETE"])
@jwt_required()
def delete_student_from_group_routes(groupId):
    current_user_id = get_jwt_identity()
    studentId = request.args.get("studentId")
    if studentId is None:
        return jsonify({"error": "studentId parameter is required"}), 400
    
    response, status_code = delete_student_from_group_controller(current_user_id, groupId, studentId)
    
    return jsonify(response), status_code

@group_app.route("/api/group/<groupId>", methods=["DELETE"])
@jwt_required()
def delete_group_route(groupId):
    current_user_id = get_jwt_identity()
    response, status_code = delete_group_controller(current_user_id, groupId)
    return jsonify(response), status_code

@group_app.route("/api/group/teacher", methods=["GET"])
@jwt_required()
def get_groups_from_teacher_route():
    teacherId = get_jwt_identity()
    if not teacherId:
        return {"message": "Invalid token data"}, 400
    response, status_code = get_group_by_teacher_id_controller(teacherId)
    return jsonify(response), status_code

@group_app.route("/api/group/<grupoId>", methods=["PATCH"])
@jwt_required()
def update_student_group_route(grupoId):
    data = request.get_json()
    teacher_id = get_jwt_identity()
    response, status_code = update_group_controller(teacher_id, grupoId, data)
    return jsonify(response), status_code

@group_app.route('/api/group/upload_image/<group_id>', methods=['PATCH'])
def upload_image_group(group_id):
    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        file_path = handle_image_upload(file)
        destination_blob_name = f"group/{group_id}/profile_image.jpg"
        image_url = upload_image_to_firebase(file_path,destination_blob_name)
        upload_image_group_controller(image_url, group_id)
        delete_file_from_upload(file_name=file.filename)
        return jsonify({"message": "File uploaded successfully", "file_url": image_url}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500