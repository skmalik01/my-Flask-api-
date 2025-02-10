from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    return "Auth login page"
@auth_bp.route('/signup')
def signup():
    return "Auth signup page" 