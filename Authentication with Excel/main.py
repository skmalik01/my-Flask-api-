from operator import ipow
from os import name
from flask import Flask, jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import csv
import io
import openpyxl
import jwt
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///excelcrud.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
app.config['SECRET_KEY'] = "thisisasecretkey"

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Students(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20))
    rollno = db.Column(db.Integer, unique = True)
    std = db.Column(db.String(10))
    contact = db.Column(db.String(10))
    
    def __init__(self, name, rollno, std, contact):
        self.name = name 
        self.rollno = rollno
        self.std = std
        self.contact = contact
        
class Users(db.Model):
    user_id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50))
    contact = db.Column(db.String(20))
    email = db.Column(db.String(20))
    password = db.Column(db.String(200))
    admin = db.Column(db.Boolean)
    

class PostSchema(ma.Schema):
    class Meta:
        fields = ("name", "rollno", "std", "contact")
post_schema = PostSchema()
posts_schema = PostSchema(many=True)

class UserSchema(ma.Schema):
    class Meta:
        fields = ("user_id", "name", "contact", "email", "admin")
user_schema = UserSchema()
users_schema = UserSchema(many=True)

with app.app_context():
    db.create_all()
    
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message' : 'Token is Missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
            current_user = Users.query.filter_by(user_id=data['user_id']).first()
        except:
            return jsonify({'message' : 'Token is Invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/user', methods = ["GET"])
@token_required
def get_all_user(current_user):
    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function!'})
    user = Users.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({'message' : 'No user Found!'})
    return user_schema.jsonify(user)
@app.route('/user/<user_id>', methods=["PUT"])
@token_required
def make_admin(current_user, user_id):
    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function!'})
    user = Users.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({'message' : 'user not found!'})
    user.admin=True
    db.session.commit()
    return jsonify({'message' : 'Now you are admin..'})

@app.route('/user/user_id', methods = ["DELETE"])
@token_required
def delete_user(current_user, user_id):
    if not current_user.admin:
        return jsonify({'message' : 'cannot perform that function'})
    user=Users.query.filter_by(user_id=user_id).first()
    
    if not user:
        return jsonify({'message' : 'user not found'})
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message' : 'The user has been deleted'})

@app.route('/registration', methods = ["POST"])
def create_user():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'])
    new_user = Users(name=data['name'], contact=data['contact'], email=data['email'], password=hashed_password, admin=False)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message' : 'New user created!'})

@app.route('/login', methods = ["POST"])
def login():
    auth=request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
    user=Users.query.filter_by(name=auth.username).first()
    if not user:
        return make_response('Incorrect username', 404, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'user_id' : user.user_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=10)}, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'token' : token})
    return make_response('could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

with app.app_context():
    
    dbRollno= Students.query.with_entities(Students.rollno).all()
    existing=[]
    for x in dbRollno:
        lst=list(x)
        existing+=lst
    
@app.route('/csvUpload', methods=['POST'])
@token_required
def csvUpload(current_user):
    if request.method == 'POST':
        if request.files:
            uploaded_file = request.files['filename']
            data = uploaded_file.stream.read() # This line uses the same variable and worked fine
            #Convert the FileStorage to list of lists here.
            stream = io.StringIO(data.decode("UTF8"), newline=None)
            reader = csv.reader(stream)
            i=0
            for row in reader:
                i+=1
                if i==1:
                    continue
                else:
                    if int(row[1]) in existing:
                        name = row[0]
                        std = row[2]
                        contact = row[3]
                        col = Students.query.filter_by(rollno=row[1]).first()
                        if col.name!=name or col.std!=std or col.contact!=contact:
                            col.name=name
                            col.std=std
                            col.contact=contact
                            db.session.add(col) 
                        else:
                            continue
                    else:
                        my_posts=Students(*row)
                        db.session.add(my_posts)
                    db.session.commit()

            return jsonify({'message' : 'csv file successfully uploaded'})

@app.route('/excelUpload',methods=['POST'])
@token_required
def excelUpload(current_user):
    if request.method=='POST':
        if request.files:
            uploaded_file = request.files['filename']
            wb_obj=openpyxl.load_workbook(uploaded_file)
            sheet=wb_obj.active
            l=0
            for row in sheet.values:
                l+=1
                if l==1:
                    continue
                else:
                    if row[1] in existing:
                        name = row[0]
                        std = row[2]
                        contact = row[3]
                        col = Students.query.filter_by(rollno=row[1]).first()
                        if col.name!=name or col.std!=std or col.contact!=contact:    
                            col.name=name
                            col.std=std
                            col.contact=contact
                            db.session.add(col)
                    else:
                        my_posts=Students(*row)
                        db.session.add(my_posts)
                    db.session.commit()
            return jsonify({'message' : 'Excel File successfully uploaded'})
if __name__ == '__main__':
    app.run(debug=True)        
