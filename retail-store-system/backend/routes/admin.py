from flask import request, jsonify
from routes import admin_bp
from supabase_client import get_supabase
from datetime import datetime

supabase = get_supabase()

# ============================================
# GET ALL STAFF
# ============================================
@admin_bp.route('/staff', methods=['GET'])
def get_staff():
    """Get all staff members"""
    try:
        response = supabase.table('users').select('*').execute()
        staff = response.data if response.data else []
        
        return jsonify({
            'status': 'success',
            'data': staff,
            'count': len(staff)
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================
# CREATE NEW STAFF
# ============================================
@admin_bp.route('/staff', methods=['POST'])
def create_staff():
    """Create new staff member"""
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
        
        # Check if email exists
        existing = supabase.table('users').select('*').eq('email', email).execute()
        if existing.data:
            return jsonify({
                'status': 'error',
                'message': 'Email already exists'
            }), 400
        
        # Create auth user
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
            user_id = str(auth_response.user.id)
            
            # Store in users table
            supabase.table('users').insert({
                'id': user_id,
                'email': email,
                'full_name': full_name,
                'role': role,
                'created_at': datetime.utcnow().isoformat()
            }).execute()
            
            return jsonify({
                'status': 'success',
                'message': 'Staff member created',
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
                'message': 'Failed to create user'
            }), 400
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================
# UPDATE STAFF ROLE
# ============================================
@admin_bp.route('/staff/<staff_id>', methods=['PUT'])
def update_staff(staff_id):
    """Update staff role"""
    try:
        data = request.get_json()
        
        if 'role' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Role is required'
            }), 400
        
        role = data['role'].lower()
        if role not in ['admin', 'staff']:
            return jsonify({
                'status': 'error',
                'message': 'Invalid role'
            }), 400
        
        supabase.table('users').update({'role': role}).eq('id', staff_id).execute()
        
        return jsonify({
            'status': 'success',
            'message': 'Staff role updated'
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================
# DELETE STAFF
# ============================================
@admin_bp.route('/staff/<staff_id>', methods=['DELETE'])
def delete_staff(staff_id):
    """Delete staff member"""
    try:
        # Delete from users table
        supabase.table('users').delete().eq('id', staff_id).execute()
        
        # Delete from auth (if possible)
        try:
            supabase.auth.admin.delete_user(staff_id)
        except:
            pass
        
        return jsonify({
            'status': 'success',
            'message': 'Staff member deleted'
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500