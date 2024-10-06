# This file handles user authentication, including register and login functionality.
from flask import Blueprint, jsonify, request, current_app
import jwt
import datetime
from models import User, db

# Define a Blueprint for authentication routes
auth_blueprint = Blueprint('auth', __name__)

# Register a new user
@auth_blueprint.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password required'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 400

    new_user = User(username=username)
    new_user.set_password(password)
    
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

# Login and generate a JWT token
@auth_blueprint.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username == None or password == None:
        return jsonify({'message': 'Username or password missing'}), 412

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid credentials'}), 401

    # Generate JWT token
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    token = jwt.encode({'username': user.username, 'exp': expiration_time}, current_app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({'token': token}), 200

# Endpoint to validate JWT token
@auth_blueprint.route('/validate-token', methods=['GET'])
def validate_token():
    token = request.headers.get('Authorization')
    
    if not token:
        return jsonify({"message": "Token is missing"}), 400
    
    try:
        token = token.split(" ")[1]
    except IndexError:
        return jsonify({"message": "Invalid token format"}), 400

    try:
        decoded = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return jsonify({"message": "Token is valid", "user": decoded['username']}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid token"}), 401
