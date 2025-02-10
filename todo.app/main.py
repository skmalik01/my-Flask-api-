from flask import Flask, request, Response, Blueprint, session, make_response
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(30), nullable=False)

@app.route('/', methods=["POST"])
def show():
    name = request.form['name']
    return f"Hello {name}"

@app.route('/submit', methods=["Post"])
def data():
    return Response("Some data", status=200)

user_bp = Blueprint('user', __name__)

@app.route('/home')
def home():
    return 'Home Page'

@app.route("/page")
def show():
    user = request.cookies.get('name')
    return f"hello {user}" 

@app.route("/pages")
def showed():
    resp = make_response('Cookie set')
    resp.set_cookie('name', name)
    return resp   
