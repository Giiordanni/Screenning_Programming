from flask import request, jsonify, Blueprint
from controllers.token_controller import *
from flask_jwt_extended import jwt_required

token_app = Blueprint("token_app", __name__)

@token_app.route('/api/token/groupid', methods=['GET'])
def get_groupId_by_token_routes():
    email = request.args.get('email')
    email = str(email)
    if not email:
        return jsonify({"message": "Token não fornecido!"}), 400
    
    return get_groupId_by_token_controller(email)

