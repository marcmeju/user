from flask import Blueprint, jsonify, request
from models import User, db

user_blueprint = Blueprint('user_api_routes', __name__, url_prefix='/api/user')

# HomePage
@user_blueprint.route('/')
def index():
    return 'Welcome to the User API'

# Get all users
@user_blueprint.route('/all', methods=['GET'])
def get_users():
    return 'TO BE IMPLEMENTED - Retrieve all users'

#Create a User   
@user_blueprint.route('/create', methods=['POST'])
def create_user():
    return 'Create a new user'

# Retrieve a User by ID
@user_blueprint.route('/<int:id>', methods=['GET'])
def get_user(id):
    return f'TO BE IMPLEMENTED - Retrieve user with ID: {id}'

# Retrieve a User by username
@user_blueprint.route('/<string:username>', methods=['GET'])
def get_user_by_username(username):
    return f'TO BE IMPLEMENTED - Retrieve user with username: {username}'
