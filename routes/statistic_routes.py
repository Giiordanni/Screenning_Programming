from flask import Blueprint, request, jsonify
from controllers.statisc_controller import *

statistic_app = Blueprint("statistic_app", __name__)


@statistic_app.route('/api/statistic', methods=['POST'])
def create_statistic_routes():
    try:
        data = request.json
        response = create_statistc_controller(data)
        return jsonify(response), 201
    except Exception as e:
        return jsonify({"error": f"Erro ao criar estatística: {str(e)}"}), 500


@statistic_app.route('/api/activity/<id_student>', methods=['GET'])
def get_activity_statistics_routes(id_student):
    try:
        id_activity = request.args.get('id_activity')
        response = group_answer_by_id_student_controller(id_student,id_activity)
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao buscar estatísticas: {str(e)}"}), 500


@statistic_app.route('/api/activity/all', methods=['GET'])
def get_all_statistics_routes():
    try:
        id_activity = request.args.get('id_activity')
        response = get_all_statistics_by_activity(id_activity)
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao buscar estatísticas: {str(e)}"}), 500