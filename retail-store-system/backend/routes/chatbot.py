from flask import request, jsonify
from routes import chatbot_bp
from supabase_client import get_supabase
from datetime import datetime, timedelta

supabase = get_supabase()

@chatbot_bp.route('/ask', methods=['POST'])
def ask_chatbot():
    """Process chatbot queries"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip().lower()
        
        if not user_message:
            return jsonify({
                'status': 'error',
                'message': 'Please ask a question'
            }), 400
        
        response = process_query(user_message)
        
        return jsonify({
            'status': 'success',
            'response': response,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        print(f"Chatbot error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error processing request: ' + str(e)
        }), 500


def process_query(user_message):
    """Process different types of queries"""
    
    try:
        # Get bills data
        bills_res = supabase.table('bills').select('*').execute()
        bills = bills_res.data if bills_res.data else []
        
        # Get products data
        products_res = supabase.table('products').select('*').execute()
        products = products_res.data if products_res.data else []
        
        # Get customers data
        customers_res = supabase.table('customers').select('*').execute()
        customers = customers_res.data if customers_res.data else []
        
        today = datetime.now().date()
        today_str = today.isoformat()
        
        # TODAY'S SALES
        if any(word in user_message for word in ['today', "today's"]):
            today_bills = [b for b in bills if str(b['bill_date'])[:10] == today_str]
            today_sales = sum(float(b['final_amount']) for b in today_bills)
            return f"📊 Today's sales (as of {today.strftime('%B %d, %Y')}): ₹{today_sales:.2f} from {len(today_bills)} transactions"
        
        # WEEKLY SALES
        if any(word in user_message for word in ['week', 'weekly', '7 days']):
            week_ago = today - timedelta(days=7)
            week_bills = [b for b in bills if datetime.fromisoformat(str(b['bill_date'])[:19]).date() >= week_ago]
            week_sales = sum(float(b['final_amount']) for b in week_bills)
            return f"📊 This week's sales: ₹{week_sales:.2f} from {len(week_bills)} transactions"
        
        # MONTHLY SALES
        if any(word in user_message for word in ['month', 'monthly']):
            month_ago = today - timedelta(days=30)
            month_bills = [b for b in bills if datetime.fromisoformat(str(b['bill_date'])[:19]).date() >= month_ago]
            month_sales = sum(float(b['final_amount']) for b in month_bills)
            return f"📊 Last 30 days sales: ₹{month_sales:.2f} from {len(month_bills)} transactions"
        
        # TOTAL SALES
        if any(word in user_message for word in ['total', 'all time', 'overall']):
            total = sum(float(b['final_amount']) for b in bills)
            return f"💰 Total all-time sales: ₹{total:.2f} from {len(bills)} transactions"
        
        # PRODUCTS
        if any(word in user_message for word in ['product', 'inventory', 'stock']):
            total_value = sum(p['price'] * p['quantity'] for p in products)
            return f"📦 Inventory: {len(products)} products worth ₹{total_value:.2f}"
        
        # CUSTOMERS
        if any(word in user_message for word in ['customer', 'clients']):
            if customers:
                return f"👥 You have {len(customers)} customers registered"
            return "👥 No customers registered yet"
        
        # LOW STOCK
        if any(word in user_message for word in ['low stock', 'restock', 'alert']):
            low = [p for p in products if p['quantity'] < 5]
            if low:
                return f"⚠️ {len(low)} products need restocking"
            return "✅ All products are well-stocked"
        
        # BILLS/TRANSACTIONS
        if any(word in user_message for word in ['bill', 'invoice', 'transaction']):
            return f"📄 Total bills created: {len(bills)}"
        
        # GST
        if any(word in user_message for word in ['gst', 'tax']):
            total_gst = sum(float(b['gst_amount']) for b in bills)
            return f"💳 Total GST collected: ₹{total_gst:.2f}"
        
        # AVG TRANSACTION
        if any(word in user_message for word in ['average', 'avg']):
            if bills:
                avg = sum(float(b['final_amount']) for b in bills) / len(bills)
                return f"📊 Average transaction value: ₹{avg:.2f}"
            return "No transactions yet"
        
        # DEFAULT RESPONSE
        return """I'm RetailHub Assistant! 🤖

I can help with:
• "Today's sales" - Check today's revenue
• "Weekly sales" - Get this week's numbers
• "Total products" - Count of products
• "Total customers" - Count of customers
• "Low stock" - Products needing restocking
• "Total bills" - All invoices created
• "Average bill" - Average transaction value

What would you like to know?"""
    
    except Exception as e:
        print(f"Query processing error: {str(e)}")
        return f"Sorry, I encountered an error: {str(e)}"