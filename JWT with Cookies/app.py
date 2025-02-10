import datetime
from flask import Flask, jsonify, request, abort, session, make_response, g
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import jwt
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisissecret'

db=SQLAlchemy(app)
ma=Marshmallow(app)

with app.app_context():
    db.create_all()
    
class User(db.Model):
    __tablename__ = "user"
    __table_args__ = (
        db.CheckConstraint(
            "length(name) >= 3 AND length(name) <= 64", name="user_name_check",
        ),
        db.CheckConstraint(
            "length(username) >= 3 AND length(username) <= 32", name="user_username_check"
        ),
        db.CheckConstraint(
            "length(email) >= 3 AND length(email) <= 64", name="user_email_check"
        ),
        db.UniqueConstraint("email")
        
    )
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    username = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    _password = db.Column(db.String(150))
    
    @property
    def password(self):
        raise AttributeError("cannot read password")
    @password.setter
    def password(self, password):
        self._password = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self._password, password)
    
    
# with app.app_context():
#     db.create_all()
    
class UserSchema(ma.Schema):
    class Meta:
        model = User
        fields = ("id", "name", "username", "email")
        dump_only = ("id",)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        token = request.cookies.get('currentUser')
        
        if not token:
            return jsonify({'message' : 'Token is missing'})
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"], options=None)
            current_user = User.query.filter_by(id=data['user_id']).first()
            if current_user.id != session['user_id']:
                return jsonify({'message' : 'Token is invalid!'})
        except:
            return jsonify({'message' : 'Token is invalid'})
        return f(current_user)
    return decorated

@app.route('/login', methods = ['POST'])
def login():
    credentials = request.get_json()
    user = User.query.filter_by(username=credentials["username"]).first()
    session['user_id'] = user.id
    if not user:
        abort(401)
    
    if not user.verify_password(credentials["password"]):
        abort(401)
        
    token = jwt.encode({'user_id' : user.id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=10)}, app.config['SECRET_KEY'],algorithm="HS256")
    response = make_response(token)
    response.set_cookie(
        "currentUser", token,secure=app.config.get("SECURE_COOKIE")
    )
    return response

@app.route("/signup", methods = ["POST"])
def signup():
    data = request.get_json()
    existing_username = User.query.filter_by(username=data['username']).first()
    existing_email = User.query.filter_by(email=data['email']).first()
    if existing_username:
        abort(400, description={'Username is already in use'})
    
    if existing_email:
        abort(400, description={'Email is already in use'})
    
    if  'name' not in data or len(data['name']) < 2:
        abort(400, description={'First name must be greater than 1 character'})
    
    if  'password' not in data or len(data['password']) < 7:
        abort(400, description={'Password must be at least 7 characters'})
    
    user = User(**data)
    db.session.add(user)
    db.session.commit()
    user_schema = UserSchema()
    return user_schema.dump(user), 201
    
    if existing_email:
        raise ({'Email' : 'Email is already in use'})
    
    if len(data['name']) < 2:
        raise  ({'name' : 'first name must be greater than 1 character'})
    
    if len(data['_password']) < 7:
        raise ({'password' : 'Password must be atleast 7 character'})
    
    user = User(**data)
    db.session.add(user)
    db.session.commit()
    user_schema = UserSchema()
    return user_schema.dump(user), 201

@app.route('/', methods=['GET', 'POST'])
@token_required
def home(current_user):
    userdetails = User.query.get(current_user.id)
    # user = UserSchema().dump(userdetails)
    return {'Assalamwaalaikum' : userdetails.name}
@app.route('/database')
def database():
    db.create_all()
    return {'database' : 'Databases created successfully'}

if __name__=='__main__':
    app.run(debug=True)    