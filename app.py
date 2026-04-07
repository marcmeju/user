from flask import Flask, g
import os
from dotenv import load_dotenv
from flask.sessions import SecureCookieSessionInterface
from models import db, init_app, User
from routes import user_blueprint
from flask_migrate import Migrate
from flask_login import LoginManager

# Load the environment variables from the .env file
load_dotenv()

#initialize the application
app = Flask(__name__, instance_relative_config=True)

# Ensure instance folder exists
try:
    os.makedirs(app.instance_path, exist_ok=True)
except OSError:
    pass

#database configuration
app.config['SECRET_KEY'] = os.getenv('USER_DB_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(app.instance_path, 'user.db')}"
app.config['SQL_ALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager(app)

#initialize the database and migration
init_app(app)
migrate = Migrate(app, db)

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()

@login_manager.request_loader
def load_user_from_request(request):
    api_key = request.headers.get('Authorization')
    if api_key:
        user = User.query.filter_by(api_key=api_key).first()
        if user:
            return user
    return None

class CustomSessionInterface(SecureCookieSessionInterface):
    def save_session(self, *args, **kwargs):
        if g.get('login_via_header'):
            return
        return super(CustomSessionInterface, self).save_session(*args, **kwargs)

#import the routes
app.register_blueprint(user_blueprint)

#run the application
if __name__ == '__main__':
    app.run(debug=True, port=5003)