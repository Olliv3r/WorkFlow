from flask import jsonify
from app.stage import bp
from app.stage.services.stage_service import StageService as ss
from app.core.exceptions import NotFoundError

@bp.route("/options", methods=["GET"])
def get_options():
    try:
        stages = ss.get_stages()
        return jsonify(status="success", message="Dados de etapa encontrados", stages=stages)
      
    except NotFoundError as error:
        return jsonify(status="error", message=str(error.message))