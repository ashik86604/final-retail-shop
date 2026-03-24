from flask import request, jsonify
from routes import payments_bp
from supabase_client import get_supabase
from datetime import datetime
import razorpay
import os
from dotenv import load_dotenv

load_dotenv()

supabase = get_supabase()

# Initialize Razorpay
RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET')

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# ============================================
# CREATE RAZORPAY ORDER
# ============================================
@payments_bp.route('/create-order', methods=['POST'])
def create_order():
    """Create Razorpay order"""
    try:
        data = request.get_json()
        
        if not data.get('amount') or not data.get('bill_id'):
            return jsonify({
                'status': 'error',
                'message': 'Amount and bill_id required'
            }), 400
        
        amount = int(float(data['amount']) * 100)  # Convert to paise
        bill_id = data['bill_id']
        
        # Create Razorpay order
        razorpay_order = client.order.create(dict(
            amount=amount,
            currency='INR',
            receipt=f'bill_{bill_id}',
            payment_capture='1'
        ))
        
        return jsonify({
            'status': 'success',
            'order_id': razorpay_order['id'],
            'amount': amount,
            'key': RAZORPAY_KEY_ID
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================
# VERIFY PAYMENT
# ============================================
@payments_bp.route('/verify-payment', methods=['POST'])
def verify_payment():
    """Verify Razorpay payment"""
    try:
        data = request.get_json()
        
        payment_id = data.get('payment_id')
        order_id = data.get('order_id')
        signature = data.get('signature')
        
        if not all([payment_id, order_id, signature]):
            return jsonify({
                'status': 'error',
                'message': 'Missing payment details'
            }), 400
        
        # Verify signature
        razorpay_order = client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        })
        
        return jsonify({
            'status': 'success',
            'message': 'Payment verified successfully'
        }), 200
    
    except razorpay.errors.SignatureVerificationError:
        return jsonify({
            'status': 'error',
            'message': 'Payment verification failed'
        }), 400
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================
# GET PAYMENT STATUS
# ============================================
@payments_bp.route('/payment-status/<payment_id>', methods=['GET'])
def get_payment_status(payment_id):
    """Get payment status"""
    try:
        payment = client.payment.fetch(payment_id)
        
        return jsonify({
            'status': 'success',
            'data': {
                'id': payment['id'],
                'amount': payment['amount'] / 100,
                'status': payment['status'],
                'method': payment.get('method', 'N/A'),
                'created_at': payment['created_at']
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500