from flask import Blueprint, request, jsonify
from functools import wraps
import jwt
import os
from datetime import datetime, timedelta
import hashlib
from models.database import User, Patient, AnalysisResult, ensure_db

auth_bp = Blueprint('auth', __name__)

# Secret key for JWT tokens
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

def generate_token(user_id):
    """Generate JWT token"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=30)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def token_required(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        request.user_id = payload['user_id']
        return f(*args, **kwargs)
    
    return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        ensure_db()
        data = request.get_json()
        
        # Validate input
        if not data.get('email') or not data.get('password') or not data.get('full_name'):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if user exists
        existing_user = User.find_by_email(data['email'])
        if existing_user:
            return jsonify({'error': 'User already exists'}), 400
        
        # Create user
        hashed_password = hash_password(data['password'])
        user = User.create(
            email=data['email'],
            password=hashed_password,
            full_name=data['full_name']
        )
        
        if not user:
            return jsonify({'error': 'Failed to create user'}), 500
        
        # Generate token
        token = generate_token(user['id'])
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user': {
                'id': user['id'],
                'email': user['email'],
                'full_name': user['full_name']
            },
            'token': token
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        ensure_db()
        data = request.get_json()
        
        # Validate input
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Missing email or password'}), 400
        
        # Find user
        user = User.find_by_email(data['email'])
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check password
        hashed_password = hash_password(data['password'])
        if user['password'] != hashed_password:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate token
        token = generate_token(user['id'])
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': user['id'],
                'email': user['email'],
                'full_name': user['full_name']
            },
            'token': token
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile():
    """Get user profile"""
    try:
        user = User.find_by_id(request.user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get patients for this user
        patients = Patient.get_by_user(request.user_id)
        
        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'full_name': user['full_name'],
                'created_at': user['created_at']
            },
            'patients_count': len(patients)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/verify', methods=['POST'])
def verify():
    """Verify token"""
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 400
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        user = User.find_by_id(payload['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'full_name': user['full_name']
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
