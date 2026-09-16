from flask import Blueprint
bp = Blueprint("advance", __name__)
from app.advance import views
