from flask import Flask, jsonify, request, session
from flask_mysqldb import MySQL, MySQLdb
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from datetime import timedelta

app = Flask(__name__)

app.config["SECRET_KEY"] = 'shaikh-malik'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)
CORS(app)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'apitest'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

@app.route('/')
def home():
    if 'username' in session:
        username = session['username']
        return jsonify({'message' : 'You are already logged in', 'username' : username})
    else:
        resp = jsonify({'message' : 'Unauthorized'})
        resp.status_code = 401
        return resp

@app.route('/signup', methods=['POST'])
def signup():
    json = request.json
    username = json.get("name")
    password = json.get('password')
    profession = json.get('profession')
    if not username or not password or not profession:
        return jsonify({"Message" : "Bad request - missing fields"})
    passhash = generate_password_hash(password)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = "INSERT INTO user (username, profession, password) VALUES (%s, %s, %s)"
    values = (username, profession, passhash)
    cursor.execute(sql, values)
    mysql.connection.commit()
    cursor.close()
    return "Successfully Signup"

@app.route('/login', methods=['POST'])
def login():
    _json = request.json
    _username = _json['username']
    _password = _json['password']
    print(_password)
    if _username and _password:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = "SELECT * FROM user WHERE username=%s"
        sql_where = (_username,)
        cursor.execute(sql, sql_where)
        row = cursor.fetchone()
        if row:
            username = row['username']
            password = row['password']
            if check_password_hash(password, _password):
                session['username'] = username
                cursor.close()
                return jsonify({'message' : 'you are logged in successfully'})
            else:
                resp = jsonify({"message" : "Bad Request - invalid password"})
                resp.status_code = 400
                return resp
        else:
            resp = jsonify({"Message" : "User not Found"})
            resp.status_code = 404
            return resp
    else:
        resp = jsonify({"message" : "Bad request - invalid credentials"})
        resp.status_code = 400
        return resp

@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username', None)
    return jsonify({'messaage' : 'You successfully logged out'})

if __name__ == '__main__':
    app.run()