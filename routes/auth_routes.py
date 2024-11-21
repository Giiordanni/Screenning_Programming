from flask import request, jsonify, Blueprint
from controllers.auth_controller import *
from flask_jwt_extended import jwt_required
from controllers.auth_controller import get_user_data
auth_app = Blueprint("auth_app", __name__)


@auth_app.route("/api/login", methods=["POST"])
def login_route():
    data = request.get_json()

    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Email or password is missing"}), 400

    response, status_code = login_controller(data)

    return jsonify(response), status_code


@auth_app.route('/api/data_user', methods=['GET'])
@jwt_required()
def get_user_data_route():
    return get_user_data()