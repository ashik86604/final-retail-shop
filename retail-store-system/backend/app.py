from flask import Flask, jsonify, render_template, redirect
from flask_cors import CORS
from config import Config

app = Flask(
    __name__, 
    template_folder='../frontend/templates', 
    static_folder='../frontend/static'
)
app.config.from_object(Config)

CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5000", "http://127.0.0.1:5000", "http://192.168.1.112:5000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

from routes import (
    auth_bp, inventory_bp, billing_bp, customers_bp, 
    chatbot_bp, dashboard_bp, admin_bp, reports_bp, 
    payments_bp, email_bp
)

app.register_blueprint(auth_bp)
app.register_blueprint(inventory_bp)
app.register_blueprint(billing_bp)
app.register_blueprint(customers_bp)
app.register_blueprint(chatbot_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(payments_bp)
app.register_blueprint(email_bp)

# Routes
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('auth.html')

@app.route('/dashboard', methods=['GET'])
def dashboard_page():
    return render_template('dashboard.html')

@app.route('/inventory', methods=['GET'])
def inventory_page():
    return render_template('inventory.html')

@app.route('/billing', methods=['GET'])
def billing_page():
    return render_template('billing.html')

@app.route('/customers', methods=['GET'])
def customers_page():
    return render_template('customers.html')

@app.route('/chatbot', methods=['GET'])
def chatbot_page():
    return render_template('chatbot.html')

@app.route('/admin', methods=['GET'])
def admin_page():
    return render_template('admin.html')

@app.route('/reports', methods=['GET'])
def reports_page():
    return render_template('reports.html')

@app.route('/api', methods=['GET'])
def api_root():
    return jsonify({
        'status': 'success',
        'message': 'RetailHub API',
        'version': '2.0.0'
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'status': 'error', 'message': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'status': 'error', 'message': 'Server error'}), 500

@app.after_request
def set_security_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)