from flask import Flask
from app import user_bp
from auth import auth_bp

app = Flask(__name__)
app.register_blueprint(user_bp, url_prefix='/app')
app.register_blueprint(auth_bp, url_prefix='/auth')

if __name__ == '__main__':
    app.run(debug=True)