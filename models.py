from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import time

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
    api_key = db.Column(db.String(120), unique=True, nullable=True)
    last_activity = db.Column(db.Float, default=time.time())
    session_created_at = db.Column(db.Float, nullable=True)
    
    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f'<User {self.id}, {self.username}>'  
    
    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'is_authenticated': self.is_authenticated,
            'api_key': self.api_key
        }
    
    def is_session_expired(self, timeout_minutes=30):
        """Check if session has exceeded timeout"""
        if not self.session_created_at:
            return False
        elapsed = (time.time() - self.session_created_at).total_seconds()
        return elapsed > (timeout_minutes * 60)
    
    def update_last_activity(self):
        """Update when user last made a request"""
        self.last_activity = time.time()
        db.session.commit()

    def update_api_key(self):
        self.api_key = generate_password_hash(f"{self.username}{self.email}" + "{str(time.time())}", method='pbkdf2:sha1', salt_length=8)