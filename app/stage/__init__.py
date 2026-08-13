from flask import Blueprint

bp = Blueprint("stage", __name__)

from app.stage import views