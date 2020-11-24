
from flask_sqlalchemy import SQLAlchemy
import datetime
import enum
# from flask_admin.contrib.sqla import ModelView
from passlib.hash import sha256_crypt
# from crypto import encrypt

db = SQLAlchemy()



# status ( status of the task )
class Status(enum.Enum):
    PE = 'PENDING', 'danger'  # status,css btn class
    AC = 'ACTIVE', 'info'
    CO = 'COMPLETED', 'success'



# task model
class Tasks(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.String(30), nullable=False,
                           default=datetime.datetime.now)
    created_by = db.Column(db.String(30), db.ForeignKey(
        'users.username'), nullable=False)  # one to many relation with the username
    start_date = db.Column(
        db.DateTime, default=datetime.datetime.now().date, nullable=False)
    end_date = db.Column(
        db.DateTime, default=datetime.datetime.now().date, nullable=False)
    sheet_name = db.Column(db.String(250),nullable=False)
    sheet_url = db.Column(db.String(1000), nullable=False)
    status = db.Column(db.Enum(Status), default=Status.PE)
    bot_assigned = db.Column(db.String(40), nullable=False)
    
    
    def __repr__(self):
        return "Task %d" %(self.id)


# user model

class Users(db.Model):
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer(),primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(90), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    registered_at = db.Column(
        db.String(30), nullable=False, default=datetime.datetime.now().date)
    # and i have on delete cascade if the user is deleted all his tasks will be deleted.
    tasks = db.relationship('Tasks', backref='users') # , cascade="all,delete"
   
    
    
    def __init__(self,name,username,email,password):
        self.name = name
        self.username = username
        self.email = email
        self.password = password
       
        
        
    
    def __str__(self):
        return "%s" %(self.username)

       

           
