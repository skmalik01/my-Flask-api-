from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import jwt
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///api'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
app.config['SECRET_KEY'] = 'thisisasecretkey'

db = SQLAlchemy(app)
ma = Marshmallow(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique = True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(300))
    admin = db.Column(db.Boolean)

with app.app_context():
    db.create_all()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'messsage' : 'Token is missing!'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(user_id=data['user_id'])
        except:
            return jsonify({'message' : 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated
class Userschema(ma.Schema):
    class meta:
        fields = ("user_id", "username", "admin")

user_schema = Userschema()
users_schema = Userschema(many=True)

@app.route("/user", methods=["GET"])
@token_required
def get_all_users(current_user):
    if not current_user.admin:
        return jsonify({"message" : "cannot perform that function"})
    users = User.query.all()
    result = users_schema.dump(users)
    return jsonify(result)

@app.route('/signup', methods=["POST"])
def create_user():
    data=request.get_json()
    hashed_password=generate_password_hash(data['password'])
    new_user = User(user_id=data['user_id'], username=data['username'], password=hashed_password, admin=False)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message' : 'New user created!'})

@app.route("/user/<user_id>", methods=["PUT"])
def make_admin(user_id):
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({'message' : 'No user Found!'})
    user.admin=True
    db.session.commit()
    return jsonify({'message' : "you are now admin..."})
@app.route("/user/<user_id>", methods=['DELETE'])
def delete_user(user_id):
    user = User.query.filter_by(user_id=user_id).first()

    if not user:
        return jsonify({'message' : "user not found!"})
    db.session.delete(user)
    db.session.commit()
    result = user_schema.dump(user)
    return jsonify({'message' : "The user has been deleted!"})
@app.route('/login',methods=['GET'])
def login():
    auth=request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    user=User.query.filter_by(username=auth.username).first()

    if not user:
        return make_response('Incorrect username',404,{'WWW-Authenticate' : 'Basic realm="username required!"'})

    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'user_id' : user.user_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=10)}, app.config['SECRET_KEY'])
        return jsonify({'token' : token})

    return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

if __name__=='__main__':
    app.run(debug=True)