from flask import request, jsonify
from routes import dashboard_bp
from supabase_client import get_supabase
from datetime import datetime, timedelta

supabase = get_supabase()

# ============================================
# GET DASHBOARD STATS
# ============================================
@dashboard_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get dashboard statistics"""
    try:
        # Get all data
        products_res = supabase.table('products').select('*').execute()
        customers_res = supabase.table('customers').select('*').execute()
        bills_res = supabase.table('bills').select('*').execute()
        
        products = products_res.data if products_res.data else []
        customers = customers_res.data if customers_res.data else []
        bills = bills_res.data if bills_res.data else []
        
        # Calculate stats
        total_products = len(products)
        total_customers = len(customers)
        total_bills = len(bills)
        
        # Sales calculations
        total_sales = sum(float(b['total_amount']) for b in bills) if bills else 0
        total_gst = sum(float(b['gst_amount']) for b in bills) if bills else 0
        total_final = sum(float(b['final_amount']) for b in bills) if bills else 0
        avg_bill = (total_final / total_bills) if total_bills > 0 else 0
        
        # Today's sales
        today = datetime.now().date().isoformat()
        today_bills = [b for b in bills if str(b['bill_date'])[:10] == today]
        today_sales = sum(float(b['final_amount']) for b in today_bills) if today_bills else 0
        
        # Inventory
        total_inventory_value = sum(p['price'] * p['quantity'] for p in products) if products else 0
        low_stock = len([p for p in products if p['quantity'] < 5])
        
        return jsonify({
            'status': 'success',
            'data': {
                'total_products': total_products,
                'total_customers': total_customers,
                'total_bills': total_bills,
                'today_sales': round(today_sales, 2),
                'total_sales': round(total_sales, 2),
                'total_gst': round(total_gst, 2),
                'avg_bill': round(avg_bill, 2),
                'inventory_value': round(total_inventory_value, 2),
                'low_stock_count': low_stock
            }
        }), 200
    
    except Exception as e:
        print(f"Dashboard stats error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================
# GET RECENT BILLS
# ============================================
@dashboard_bp.route('/recent-bills', methods=['GET'])
def get_recent_bills():
    """Get recent bills"""
    try:
        bills_res = supabase.table('bills').select('*').order('id', desc=True).limit(5).execute()
        customers_res = supabase.table('customers').select('*').execute()
        
        bills = bills_res.data if bills_res.data else []
        customers = {c['id']: c['name'] for c in (customers_res.data or [])}
        
        data = []
        for bill in bills:
            data.append({
                'id': bill['id'],
                'customer_name': customers.get(bill['customer_id'], 'N/A'),
                'amount': round(float(bill['final_amount']), 2),
                'date': str(bill['bill_date'])[:10],
                'items_count': len(bill.get('items', []))
            })
        
        return jsonify({
            'status': 'success',
            'data': data
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================
# GET TOP PRODUCTS
# ============================================
@dashboard_bp.route('/top-products', methods=['GET'])
def get_top_products():
    """Get top selling products"""
    try:
        products_res = supabase.table('products').select('*').order('quantity', desc=True).limit(5).execute()
        products = products_res.data if products_res.data else []
        
        data = []
        for product in products:
            data.append({
                'id': product['id'],
                'name': product['name'],
                'price': round(float(product['price']), 2),
                'quantity': product['quantity'],
                'value': round(float(product['price']) * product['quantity'], 2)
            })
        
        return jsonify({
            'status': 'success',
            'data': data
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500