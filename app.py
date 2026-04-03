from flask import Flask
import os
from dotenv import load_dotenv
from models import db, init_app, User
from routes import user_blueprint
from flask_migrate import Migrate

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

#initialize the database and migration
init_app(app)
migrate = Migrate(app, db)

#import the routes
app.register_blueprint(user_blueprint)

#run the application
if __name__ == '__main__':
    app.run(debug=True, port=5003)