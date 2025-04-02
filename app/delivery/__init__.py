from flask import Blueprint

delivery = Blueprint('delivery', __name__)

from app.delivery import routes
