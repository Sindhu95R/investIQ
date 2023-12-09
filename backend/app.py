from  flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///intellIQ.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION']=False

db = SQLAlchemy(app)
ma =Marshmallow(app)

migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email=db.Column(db.Column())
    
    def __init__(self, username, email):
        self.username = username
        self.email = email
        
class UserSchema(ma.Schema):       
    class Meta:
        fields =('id','username','email')

user_schema = UserSchema()
users_schema = UserSchema(many=True)

@app.route("/intellIQ")
def hello_world():
    return "Hello, world!"

@app.route("/signup")
def createUser():
    return "Hello, world!"

@app.route("/login")
def getUser():
    return "Hello, world!"

@app.route("/updateUser")
def updateUser():
    return "Hello, world!"

@app.route("/deleteUser")
def deleteUser():
    return "Hello, world!"

if __name__ == "__main__":
    app.run(debug=True)