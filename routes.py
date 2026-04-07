import time
from flask import Blueprint, jsonify, request, make_response
from models import User, db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_user, logout_user, login_required
from functools import wraps
from datetime import datetime, timedelta

user_blueprint = Blueprint('user_api_routes', __name__, url_prefix='/api/user')

# HomePage
@user_blueprint.route('/')
def index():
    return 'Welcome to the User API'

@user_blueprint.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "user-service",
        "timestamp": time.time().isoformat()
    }), 200

# Get all users
@user_blueprint.route('/all', methods=['GET'])
def get_users():
    all_users = User.query.all()
    return jsonify([user.serialize() for user in all_users])

#Create a User   
@user_blueprint.route('/create', methods=['POST'])
def create_user():
    try:
        user = User()
        user.username = request.form['username']
        user.email = request.form['email']
        user.password = generate_password_hash(request.form['password'], method='pbkdf2:sha1', salt_length=8)       

        # create a new user in the database
        db.session.add(user)
        db.session.commit()

        response = {
            "message": "User created successfully",
            "result": user.serialize()}
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        response = {
            "message": "Error creating user"}
        return jsonify(response), 400
    return jsonify(response), 201

# Retrieve a User by ID
@user_blueprint.route('/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    if user:                        
        return jsonify(user.serialize())
    else:
        return jsonify({"Message": f"User with ID {id} not found"}), 404
    
# Retrieve a User by username
@user_blueprint.route('/username/<string:username>', methods=['GET'])
def get_user_by_username(username):
    user = User.query.filter_by(username=username).first()
    if user:                        
        return jsonify(user.serialize()), 200
    else:
        return jsonify({"Message": f"User with username {username} not found"}), 404

# Handle Logging In
@user_blueprint.route('/login', methods=['POST'])
def login():
    user = User()
    username = request.form.get('username') 
    email = request.form.get('email')
    password = request.form.get('password')
    print(f"Received login request with username: {username}, email: {email}")  

    if not (username or email):
        return make_response(jsonify({"message": "Either username or email and a password must be present"}), 400)
    if not password:
        return make_response(jsonify({"message": "Missing required field: password"}), 400)
    
    if email:
        user = User.query.filter_by(email=email).first()
        print(f"Queried user by email: {email}, found: {user}")
    
    if not user and username:
        user = User.query.filter_by(username=username).first()
        print(f"Queried user by username: {username}, found: {user}")
    if not user:
        response = {"message": "Invalid username and/or password"}
        return make_response(jsonify(response), 401)
    
    user.password = str(user.password) if user.password else ""
    print(f"User password hash: {user.password} for user: {user.username}")
    password_valid = check_password_hash(user.password, password)
    print(f"Password valid: {password_valid} for user: {user.username}")
    if password_valid:
        try:
            user.session_created_at = time.time()
            user.update_api_key()
            db.session.commit()
            login_user(user)
        except Exception as e:
            print(f"Error logging in user: {str(e)}")
            response = {"message": "Error logging in user"}
            return make_response(jsonify(response), 500)
        print(f"User {user.username} logged in successfully")
        response = {"message": "Login successful", "user": user.serialize()}
        user.is_authenticated = True
        return make_response(jsonify(response), 200)
    
    response = {"message": "2nd Invalid username and/or password"}
    return make_response(jsonify(response), 401)

@user_blueprint.route('/logout', methods=['POST'])
def logout():
    if current_user.is_authenticated:
        logout_user()
        current_user.api_key = None
        current_user.is_authenticated = False
        db.session.commit()
        return make_response(jsonify({"message": "Logout successful"}), 200)
    return make_response(jsonify({"message": "User is currently logged Out"}), 400)

def check_session_expiration(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and current_user.api_key:
            if current_user.is_session_expired(timeout_minutes=30):
                logout_user()
                current_user.api_key = None
                db.session.commit()
                return jsonify({"message": "Session expired"}), 401
            current_user.last_activity = time.time()
            db.session.commit()
        return f(*args, **kwargs)
    return decorated_function

@user_blueprint.route('/protected', methods=['GET'])
@login_required
@check_session_expiration
def protected_route():
    return jsonify({"message": "Success - you are authenticated and your session is active! That's why you can see this protected route."}), 200

def user_exists(user_identifier):
    if User.query.filter_by(username=user_identifier).first() or User.query.filter_by(email=user_identifier).first():
        return True
    return False

def validate_login_data(data):
    if ('username' not in data and 'email' not in data) or 'password' not in data:
        return False, "Missing required fields: username OR email, and password are required."
    return True, "" 

