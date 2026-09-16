from flask import Blueprint

bp = Blueprint("price", __name__)

from app.price import views
