from asyncio.log import logger
from datetime import timedelta
import time
from flask import Flask, g
import os
from dotenv import load_dotenv
from flask.sessions import SecureCookieSessionInterface
from models import db, init_app, User
from routes import user_blueprint
from flask_migrate import Migrate
from flask_login import LoginManager
from apscheduler.schedulers.background import BackgroundScheduler

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

# ============== HEARTBEAT FUNCTIONALITY ==============

# def app_heartbeat():
#     """
#     Periodic heartbeat task that:
#     1. Checks database connectivity
#     2. Logs app status with timestamp
#     """
#     with app.app_context():
#         try:
#             # Check database connectivity
#             db.session.execute('SELECT 1')
#             db_status = "✓ Connected"
            
#             # Get active sessions count
#             active_sessions = User.query.filter(
#                 User.is_authenticated == True
#             ).count()
            
#             # Get total users count
#             total_users = User.query.count()
            
#             # Log heartbeat status with timestamp
#             logger.info(
#                 f"[HEARTBEAT] Timestamp: {time.time()} | "
#                 f"Database: {db_status} | "
#                 f"Total Users: {total_users} | "
#                 f"Active Sessions: {active_sessions}"
#             )
            
#         except Exception as e:
#             logger.error(f"[HEARTBEAT ERROR] Timestamp: {time.time()} | Error: {str(e)}")

def app_heartbeat():
    """Periodic task to log app status"""
    print(f"[HEARTBEAT] User service is running - {time.time()}")

# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=app_heartbeat,
    trigger="interval",
    seconds=30,  # Run every 30 seconds
    id='app_heartbeat',
    name='App Heartbeat with DB Check',
    replace_existing=True
)

try:
    scheduler.start()
    logger.info(f"[SCHEDULER] Heartbeat scheduler started at {time.time()}")
except Exception as e:
    logger.error(f"[SCHEDULER ERROR] Failed to start scheduler: {str(e)}")


# ============== END HEARTBEAT ==============

#import the routes
app.register_blueprint(user_blueprint)

#run the application
if __name__ == '__main__':
    app.run(debug=True, port=5003)