from flask import request, jsonify, Blueprint

from controllers.activity_controller import *

from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity

activity_app = Blueprint("activity_app", __name__)

@activity_app.route("/api/activity", methods=["POST"])
def create_activity_route():
    data = request.get_json()
    response, status_code = create_activity_controller(data)
    return jsonify(response), status_code


@activity_app.route("/api/activity", methods=["GET"])
def get_activity_route():
    id_content = request.args.get('id_content')
    id_group = request.args.get('id_group')
    
    data = {
        "id_content": id_content,
        "id_group": id_group
    }

    response, status_code = get_activity_controller(data)
    
    return jsonify(response), status_code


@activity_app.route("/api/activity/all", methods=["GET"])
def get_all_activity_route():
    id_group = request.args.get('id_group')
    
    data =  { "id_group": id_group }

    response, status_code = get_all_activity_controller(data)
    
    return jsonify(response), status_code

@activity_app.route("/api/activity/<id_activity>", methods=["DELETE"])
def delete_activity_route(id_activity):
    try:
        response, status_code = delete_activity_controller(id_activity)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@activity_app.route("/api/activity", methods=["PATCH"])
def update_activity_route():
    try:
        data = request.get_json()
        response, status_code = update_activity_controller(data)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500