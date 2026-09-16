from flask import Blueprint
bp = Blueprint("daily_work", __name__)
from app.daily_work import views
