from flask import Blueprint, redirect, render_template, request, url_for, jsonify

from app.controllers import stats_controller as controller

stats_bp = Blueprint('stats', __name__, url_prefix='/stats')

@stats_bp.route('/single/model/report', methods=['POST'])
def single_model_report():
    try: 
        return controller.single_model_report()
    except Exception as e:
        raise e

@stats_bp.route('/all/model/reports', methods=['POST'])
def all_model_reports():
    try: 
        return controller.all_model_reports()
    except Exception as e:
        raise e