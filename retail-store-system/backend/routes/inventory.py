from flask import request, jsonify
from routes import inventory_bp
from supabase_client import get_supabase
from datetime import datetime

supabase = get_supabase()

# ============================================
# GET ALL PRODUCTS
# ============================================
@inventory_bp.route('/', methods=['GET'])
def get_products():
    """Fetch all products"""
    try:
        response = supabase.table('products').select('*').execute()
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
# GET SINGLE PRODUCT BY ID
# ============================================
@inventory_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Fetch a single product by ID"""
    try:
        response = supabase.table('products').select('*').eq('id', product_id).execute()
        
        if not response.data:
            return jsonify({
                'status': 'error',
                'message': 'Product not found'
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
# ADD NEW PRODUCT (ADMIN ONLY)
# ============================================
@inventory_bp.route('/', methods=['POST'])
def add_product():
    """Add a new product"""
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['name', 'price', 'quantity']
        if not all(field in data for field in required_fields):
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields: name, price, quantity'
            }), 400
        
        # Validate data types
        try:
            price = float(data['price'])
            quantity = int(data['quantity'])
        except (ValueError, TypeError):
            return jsonify({
                'status': 'error',
                'message': 'Price must be a number and quantity must be an integer'
            }), 400
        
        if price < 0 or quantity < 0:
            return jsonify({
                'status': 'error',
                'message': 'Price and quantity cannot be negative'
            }), 400
        
        # Prepare product data
        product_data = {
            'name': data['name'].strip(),
            'price': price,
            'quantity': quantity,
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Insert into database
        response = supabase.table('products').insert(product_data).execute()
        
        return jsonify({
            'status': 'success',
            'message': 'Product added successfully',
            'data': response.data[0] if response.data else product_data
        }), 201
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================
# UPDATE PRODUCT (ADMIN ONLY)
# ============================================
@inventory_bp.route('/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update product details or stock"""
    try:
        data = request.get_json()
        
        # Check if product exists
        existing = supabase.table('products').select('*').eq('id', product_id).execute()
        if not existing.data:
            return jsonify({
                'status': 'error',
                'message': 'Product not found'
            }), 404
        
        # Prepare update data
        update_data = {}
        
        if 'name' in data:
            update_data['name'] = data['name'].strip()
        
        if 'price' in data:
            try:
                update_data['price'] = float(data['price'])
                if update_data['price'] < 0:
                    return jsonify({
                        'status': 'error',
                        'message': 'Price cannot be negative'
                    }), 400
            except (ValueError, TypeError):
                return jsonify({
                    'status': 'error',
                    'message': 'Price must be a valid number'
                }), 400
        
        if 'quantity' in data:
            try:
                update_data['quantity'] = int(data['quantity'])
                if update_data['quantity'] < 0:
                    return jsonify({
                        'status': 'error',
                        'message': 'Quantity cannot be negative'
                    }), 400
            except (ValueError, TypeError):
                return jsonify({
                    'status': 'error',
                    'message': 'Quantity must be a valid integer'
                }), 400
        
        if not update_data:
            return jsonify({
                'status': 'error',
                'message': 'No fields to update'
            }), 400
        
        # Update database
        response = supabase.table('products').update(update_data).eq('id', product_id).execute()
        
        return jsonify({
            'status': 'success',
            'message': 'Product updated successfully',
            'data': response.data[0] if response.data else update_data
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================
# UPDATE STOCK ONLY (QUICK UPDATE)
# ============================================
@inventory_bp.route('/<int:product_id>/stock', methods=['PUT'])
def update_stock(product_id):
    """Quick update for product stock"""
    try:
        data = request.get_json()
        
        if 'quantity' not in data:
            return jsonify({
                'status': 'error',
                'message': 'quantity field is required'
            }), 400
        
        try:
            quantity = int(data['quantity'])
        except (ValueError, TypeError):
            return jsonify({
                'status': 'error',
                'message': 'Quantity must be an integer'
            }), 400
        
        if quantity < 0:
            return jsonify({
                'status': 'error',
                'message': 'Quantity cannot be negative'
            }), 400
        
        # Check if product exists
        existing = supabase.table('products').select('*').eq('id', product_id).execute()
        if not existing.data:
            return jsonify({
                'status': 'error',
                'message': 'Product not found'
            }), 404
        
        # Update stock
        response = supabase.table('products').update({'quantity': quantity}).eq('id', product_id).execute()
        
        return jsonify({
            'status': 'success',
            'message': 'Stock updated successfully',
            'data': response.data[0] if response.data else {'id': product_id, 'quantity': quantity}
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================
# DELETE PRODUCT (ADMIN ONLY)
# ============================================
@inventory_bp.route('/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete a product"""
    try:
        # Check if product exists
        existing = supabase.table('products').select('*').eq('id', product_id).execute()
        if not existing.data:
            return jsonify({
                'status': 'error',
                'message': 'Product not found'
            }), 404
        
        # Delete product
        supabase.table('products').delete().eq('id', product_id).execute()
        
        return jsonify({
            'status': 'success',
            'message': 'Product deleted successfully'
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================
# GET LOW STOCK PRODUCTS
# ============================================
@inventory_bp.route('/low-stock', methods=['GET'])
def get_low_stock():
    """Get products with low stock (quantity < 5)"""
    try:
        threshold = request.args.get('threshold', 5, type=int)
        response = supabase.table('products').select('*').lt('quantity', threshold).execute()
        
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