from flask import request, jsonify
from routes import reports_bp
from supabase_client import get_supabase
from datetime import datetime, timedelta

supabase = get_supabase()

# ============================================
# GET DAILY PROFITS
# ============================================
@reports_bp.route('/daily-profits', methods=['GET'])
def get_daily_profits():
    """Get daily profit breakdown"""
    try:
        # Get last 30 days
        bills_res = supabase.table('bills').select('*').execute()
        bills = bills_res.data if bills_res.data else []
        
        # Group by date
        daily_profits = {}
        for bill in bills:
            bill_date = str(bill['bill_date'])[:10]
            if bill_date not in daily_profits:
                daily_profits[bill_date] = {
                    'date': bill_date,
                    'sales': 0,
                    'gst': 0,
                    'net_profit': 0,
                    'transactions': 0
                }
            
            daily_profits[bill_date]['sales'] += float(bill['total_amount'])
            daily_profits[bill_date]['gst'] += float(bill['gst_amount'])
            daily_profits[bill_date]['net_profit'] += float(bill['final_amount'])
            daily_profits[bill_date]['transactions'] += 1
        
        # Convert to list and sort by date
        result = sorted(daily_profits.values(), key=lambda x: x['date'])
        
        return jsonify({
            'status': 'success',
            'data': result
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================
# GET MONTHLY PROFITS
# ============================================
@reports_bp.route('/monthly-profits', methods=['GET'])
def get_monthly_profits():
    """Get monthly profit breakdown"""
    try:
        bills_res = supabase.table('bills').select('*').execute()
        bills = bills_res.data if bills_res.data else []
        
        monthly_profits = {}
        for bill in bills:
            bill_month = str(bill['bill_date'])[:7]  # YYYY-MM
            if bill_month not in monthly_profits:
                monthly_profits[bill_month] = {
                    'month': bill_month,
                    'sales': 0,
                    'gst': 0,
                    'net_profit': 0,
                    'transactions': 0
                }
            
            monthly_profits[bill_month]['sales'] += float(bill['total_amount'])
            monthly_profits[bill_month]['gst'] += float(bill['gst_amount'])
            monthly_profits[bill_month]['net_profit'] += float(bill['final_amount'])
            monthly_profits[bill_month]['transactions'] += 1
        
        result = sorted(monthly_profits.values(), key=lambda x: x['month'])
        
        return jsonify({
            'status': 'success',
            'data': result
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================
# GET TOP PRODUCTS
# ============================================
@reports_bp.route('/top-products', methods=['GET'])
def get_top_products():
    """Get top selling products"""
    try:
        products_res = supabase.table('products').select('*').execute()
        products = products_res.data if products_res.data else []
        
        # Sort by quantity sold (descending)
        top_products = sorted(products, key=lambda x: x['quantity'], reverse=True)[:10]
        
        return jsonify({
            'status': 'success',
            'data': top_products
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================
# GET INVENTORY HEALTH
# ============================================
@reports_bp.route('/inventory-health', methods=['GET'])
def get_inventory_health():
    """Get inventory health report"""
    try:
        products_res = supabase.table('products').select('*').execute()
        products = products_res.data if products_res.data else []
        
        total_products = len(products)
        low_stock = len([p for p in products if p['quantity'] < 5])
        out_of_stock = len([p for p in products if p['quantity'] == 0])
        total_value = sum(p['price'] * p['quantity'] for p in products)
        
        return jsonify({
            'status': 'success',
            'data': {
                'total_products': total_products,
                'low_stock_items': low_stock,
                'out_of_stock_items': out_of_stock,
                'total_inventory_value': round(total_value, 2),
                'healthy_stock': total_products - low_stock - out_of_stock
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================
# GET CUSTOMER METRICS
# ============================================
@reports_bp.route('/customer-metrics', methods=['GET'])
def get_customer_metrics():
    """Get customer analytics"""
    try:
        customers_res = supabase.table('customers').select('*').execute()
        bills_res = supabase.table('bills').select('*').execute()
        
        total_customers = len(customers_res.data) if customers_res.data else 0
        bills = bills_res.data if bills_res.data else []
        
        # Calculate customer spending
        customer_spending = {}
        for bill in bills:
            cust_id = bill['customer_id']
            if cust_id not in customer_spending:
                customer_spending[cust_id] = 0
            customer_spending[cust_id] += float(bill['final_amount'])
        
        avg_spending = sum(customer_spending.values()) / len(customer_spending) if customer_spending else 0
        top_customer_value = max(customer_spending.values()) if customer_spending else 0
        
        return jsonify({
            'status': 'success',
            'data': {
                'total_customers': total_customers,
                'average_spending': round(avg_spending, 2),
                'total_transactions': len(bills),
                'top_customer_value': round(top_customer_value, 2)
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500