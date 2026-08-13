from flask import jsonify
from app.hole import bp
from app.hole.services.hole_service import HoleService as hs
from app.core.exceptions import NotFoundError

@bp.route("/options", methods=["GET"])
def get_options():
    try:
        holes = hs.get_holes()
        return jsonify(status="success", message="Dados de furos encontrados", holes=holes)
      
    except NotFoundError as error:
        return jsonify(status="error", message=str(error.message))