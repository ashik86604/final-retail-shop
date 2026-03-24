from flask import request, jsonify
from routes import customers_bp
from supabase_client import get_supabase
from datetime import datetime
from datetime import datetime, timezone

supabase = get_supabase()

# ============================================
# GET ALL CUSTOMERS
# ============================================
@customers_bp.route('/', methods=['GET'])
def get_customers():
    """Fetch all customers"""
    try:
        response = supabase.table('customers').select('*').execute()
        return jsonify({
            'status': 'success',
            'data': response.data,
            'count': len(response.data)
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================
# ADD NEW CUSTOMER
# ============================================
@customers_bp.route('/', methods=['POST'])
def add_customer():
    """Add a new customer"""
    try:
        data = request.get_json()
        
        # Validation
        required = ['name']
        if not all(field in data for field in required):
            return jsonify({
                'status': 'error',
                'message': 'Customer name is required'
            }), 400
        
        customer_data = {
            'name': data['name'].strip(),
            'email': data.get('email', '').strip() or None,
            'phone': data.get('phone', '').strip() or None,
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        response = supabase.table('customers').insert(customer_data).execute()
        
        return jsonify({
            'status': 'success',
            'message': 'Customer added successfully',
            'data': response.data[0] if response.data else customer_data
        }), 201
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================
# GET CUSTOMER BY ID
# ============================================
@customers_bp.route('/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    """Fetch a single customer"""
    try:
        response = supabase.table('customers').select('*').eq('id', customer_id).execute()
        
        if not response.data:
            return jsonify({
                'status': 'error',
                'message': 'Customer not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': response.data[0]
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================
# UPDATE CUSTOMER
# ============================================
@customers_bp.route('/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    """Update customer details"""
    try:
        data = request.get_json()
        
        # Check if exists
        existing = supabase.table('customers').select('*').eq('id', customer_id).execute()
        if not existing.data:
            return jsonify({
                'status': 'error',
                'message': 'Customer not found'
            }), 404
        
        # Prepare update
        update_data = {}
        if 'name' in data:
            update_data['name'] = data['name'].strip()
        if 'email' in data:
            update_data['email'] = data['email'].strip() or None
        if 'phone' in data:
            update_data['phone'] = data['phone'].strip() or None
        
        response = supabase.table('customers').update(update_data).eq('id', customer_id).execute()
        
        return jsonify({
            'status': 'success',
            'message': 'Customer updated successfully',
            'data': response.data[0] if response.data else update_data
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================
# DELETE CUSTOMER
# ============================================
@customers_bp.route('/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    """Delete a customer"""
    try:
        # Check if exists
        existing = supabase.table('customers').select('*').eq('id', customer_id).execute()
        if not existing.data:
            return jsonify({
                'status': 'error',
                'message': 'Customer not found'
            }), 404
        
        supabase.table('customers').delete().eq('id', customer_id).execute()
        
        return jsonify({
            'status': 'success',
            'message': 'Customer deleted successfully'
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500