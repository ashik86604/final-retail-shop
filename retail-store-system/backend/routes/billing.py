from flask import request, jsonify
from routes import billing_bp
from supabase_client import get_supabase
from datetime import datetime
import json

supabase = get_supabase()

# GST Rate
GST_RATE = 0.18  # 18%

# ============================================
# GET ALL BILLS
# ============================================
@billing_bp.route('/', methods=['GET'])
def get_bills():
    """Fetch all bills"""
    try:
        response = supabase.table('bills').select('*').execute()
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
# GET ALL PRODUCTS FOR BILL CREATION
# ============================================
@billing_bp.route('/products', methods=['GET'])
def get_products_for_bill():
    """Get all products for dropdown"""
    try:
        response = supabase.table('products').select('id, name, price, quantity').execute()
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
# GET ALL CUSTOMERS FOR BILL CREATION
# ============================================
@billing_bp.route('/customers', methods=['GET'])
def get_customers_for_bill():
    """Get all customers for dropdown"""
    try:
        response = supabase.table('customers').select('id, name, email, phone').execute()
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
# CREATE BILL
# ============================================
@billing_bp.route('/', methods=['POST'])
def create_bill():
    """Create a new bill"""
    try:
        data = request.get_json()
        
        print(f"Bill creation request: {data}")
        
        # Validation
        if not data.get('customer_id'):
            return jsonify({
                'status': 'error',
                'message': 'Customer ID is required'
            }), 400
        
        items = data.get('items', [])
        if not items or len(items) == 0:
            return jsonify({
                'status': 'error',
                'message': 'Bill must have at least one item'
            }), 400
        
        # Validate items
        for item in items:
            if not item.get('product_id') or not item.get('quantity') or not item.get('price'):
                return jsonify({
                    'status': 'error',
                    'message': 'Each item must have product_id, quantity, and price'
                }), 400
        
        # Calculate totals
        subtotal = 0
        for item in items:
            try:
                qty = float(item.get('quantity', 0))
                price = float(item.get('price', 0))
                subtotal += qty * price
            except (ValueError, TypeError):
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid quantity or price in items'
                }), 400
        
        gst_amount = round(subtotal * GST_RATE, 2)
        final_amount = round(subtotal + gst_amount, 2)
        
        # Validate customer exists
        cust_check = supabase.table('customers').select('id').eq('id', int(data['customer_id'])).execute()
        if not cust_check.data:
            return jsonify({
                'status': 'error',
                'message': 'Customer not found'
            }), 404
        
        # Create bill
        bill_data = {
            'customer_id': int(data['customer_id']),
            'total_amount': round(subtotal, 2),
            'gst_amount': gst_amount,
            'final_amount': final_amount,
            'bill_date': datetime.utcnow().isoformat(),
            'items': items,
            'created_at': datetime.utcnow().isoformat()
        }
        
        print(f"Creating bill: {bill_data}")
        
        response = supabase.table('bills').insert(bill_data).execute()
        
        if not response.data:
            return jsonify({
                'status': 'error',
                'message': 'Failed to create bill'
            }), 400
        
        # Update inventory (reduce stock)
        for item in items:
            try:
                product_id = int(item['product_id'])
                quantity = float(item['quantity'])
                
                # Get current stock
                prod_check = supabase.table('products').select('quantity').eq('id', product_id).execute()
                if prod_check.data:
                    current_qty = prod_check.data[0]['quantity']
                    new_qty = max(0, current_qty - quantity)
                    supabase.table('products').update({'quantity': new_qty}).eq('id', product_id).execute()
            except Exception as e:
                print(f"Error updating inventory for product {product_id}: {str(e)}")
        
        return jsonify({
            'status': 'success',
            'message': 'Bill created successfully',
            'data': response.data[0] if response.data else bill_data
        }), 201
    
    except Exception as e:
        print(f"Bill creation error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================
# GET BILL BY ID
# ============================================
@billing_bp.route('/<int:bill_id>', methods=['GET'])
def get_bill(bill_id):
    """Fetch a single bill"""
    try:
        response = supabase.table('bills').select('*').eq('id', bill_id).execute()
        
        if not response.data:
            return jsonify({
                'status': 'error',
                'message': 'Bill not found'
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
# GET SALES SUMMARY
# ============================================
@billing_bp.route('/summary', methods=['GET'])
def get_summary():
    """Get sales summary"""
    try:
        response = supabase.table('bills').select('*').execute()
        
        if not response.data:
            return jsonify({
                'status': 'success',
                'summary': {
                    'total_bills': 0,
                    'total_sales': 0,
                    'total_gst': 0,
                    'average_bill': 0
                }
            }), 200
        
        bills = response.data
        total_bills = len(bills)
        total_sales = sum(float(b['final_amount']) for b in bills)
        total_gst = sum(float(b['gst_amount']) for b in bills)
        average_bill = total_sales / total_bills if total_bills > 0 else 0
        
        return jsonify({
            'status': 'success',
            'summary': {
                'total_bills': total_bills,
                'total_sales': round(total_sales, 2),
                'total_gst': round(total_gst, 2),
                'average_bill': round(average_bill, 2)
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500