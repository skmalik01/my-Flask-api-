from flask import Flask 
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

with app.app_context():
    db.create_all()


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(300), nullable=True)
    
    profile = db.relationship('Profile', backref = 'user', uselist=False)
    
    def __repr__(self) -> str:
        return f"<User : {self.name}>"
    
class Profile(db.Model):
    __tablename__ = 'profile'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(300), nullable=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self) -> str:
        return f"<Profile : {self.username}>"


@app.route('/add_user')
def add_user():
    new_user = User(name = "Shaikh Malik!")
    db.session.add(new_user)
    db.session.commit()
    
    new_profile = Profile(username = "SkMalik0112",user_id=new_user.id)
    db.session.add(new_profile)
    db.session.commit()
    
    return f"{new_user.name} Created Successfully"

@app.route('/get_user_profile/<int:user_id>')
def get_user_profile(user_id):
    user = User.query.get(user_id)
    if user:
        profile = user.profile
        return f"User : {user.name}, Profile : {profile.username}"
    else:
        return f"User not found"
    
if __name__ == "__main__":
    app.run(debug=True)
    
    

