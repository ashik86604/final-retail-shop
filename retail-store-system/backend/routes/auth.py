from flask import request, jsonify
from routes import auth_bp
from supabase_client import get_supabase
from datetime import datetime
import json

supabase = get_supabase()

# ============================================
# SIGN UP
# ============================================
@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Create new user account"""
    try:
        data = request.get_json()
        
        required = ['email', 'password', 'full_name']
        if not all(field in data for field in required):
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields'
            }), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        full_name = data['full_name'].strip()
        role = data.get('role', 'staff').lower()
        
        if role not in ['admin', 'staff']:
            role = 'staff'
        
        if len(password) < 6:
            return jsonify({
                'status': 'error',
                'message': 'Password must be at least 6 characters'
            }), 400
        
        # Register with Supabase Auth
        auth_response = supabase.auth.sign_up({
            'email': email,
            'password': password,
            'options': {
                'data': {
                    'full_name': full_name,
                    'role': role
                }
            }
        })
        
        if auth_response.user:
            # Store user profile in users table
            user_id = str(auth_response.user.id)
            supabase.table('users').insert({
                'id': user_id,
                'email': email,
                'full_name': full_name,
                'role': role
            }).execute()
            
            return jsonify({
                'status': 'success',
                'message': 'Account created successfully',
                'user': {
                    'id': user_id,
                    'email': email,
                    'full_name': full_name,
                    'role': role
                }
            }), 201
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to create account'
            }), 400
    
    except Exception as e:
        print(f"Signup error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================
# LOGIN
# ============================================
@auth_bp.route('/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({
                'status': 'error',
                'message': 'Email and password required'
            }), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        
        # Authenticate with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            'email': email,
            'password': password
        })
        
        if auth_response.user:
            user_id = str(auth_response.user.id)
            
            # Get user profile from users table
            user_profile = supabase.table('users').select('*').eq('id', user_id).execute()
            
            if user_profile.data:
                user_data = user_profile.data[0]
                return jsonify({
                    'status': 'success',
                    'message': 'Login successful',
                    'session': {
                        'access_token': auth_response.session.access_token,
                        'refresh_token': auth_response.session.refresh_token,
                        'user': {
                            'id': user_id,
                            'email': user_data['email'],
                            'full_name': user_data['full_name'],
                            'role': user_data['role']
                        }
                    }
                }), 200
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'User profile not found'
                }), 404
        else:
            return jsonify({
                'status': 'error',
                'message': 'Invalid email or password'
            }), 401
    
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================
# GET CURRENT USER
# ============================================
@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current logged-in user"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({
                'status': 'error',
                'message': 'No token provided'
            }), 401
        
        user = supabase.auth.get_user(token)
        
        if user:
            user_id = str(user.id)
            user_profile = supabase.table('users').select('*').eq('id', user_id).execute()
            
            if user_profile.data:
                user_data = user_profile.data[0]
                return jsonify({
                    'status': 'success',
                    'user': {
                        'id': user_id,
                        'email': user_data['email'],
                        'full_name': user_data['full_name'],
                        'role': user_data['role']
                    }
                }), 200
        
        return jsonify({
            'status': 'error',
            'message': 'Invalid token'
        }), 401
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================
# LOGOUT
# ============================================
@auth_bp.route('/logout', methods=['POST'])
def logout():
    """User logout"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if token:
            supabase.auth.sign_out(token)
        
        return jsonify({
            'status': 'success',
            'message': 'Logged out successfully'
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500