from flask import Blueprint

user_bp = Blueprint('app', __name__)

@user_bp.route('/login')
def login():
    return f"login Page"

