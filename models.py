from flask_sqlalchemy import SQLAlchemy

#initialize the database
db = SQLAlchemy()

def init_app(app):
    db.app = app
    db.init_app(app)

#define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)    
    is_active = db.Column(db.Boolean, default=True) 
    is_admin = db.Column(db.Boolean, default=False)
    is_authenticated = db.Column(db.Boolean, default=False)


    def __repr__(self):
        return f'<User {self.id}, {self.username}>'  
    
    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'is_authenticated': self.is_authenticated

        }