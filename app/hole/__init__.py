from flask import Blueprint

bp = Blueprint("hole", __name__)

from app.hole import views