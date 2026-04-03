from flask import Blueprint, jsonify, request
from models import User, db
from werkzeug.security import generate_password_hash, check_password_hash

user_blueprint = Blueprint('user_api_routes', __name__, url_prefix='/api/user')

# HomePage
@user_blueprint.route('/')
def index():
    return 'Welcome to the User API'

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
