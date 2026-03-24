from flask import Blueprint

# Create blueprints
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
inventory_bp = Blueprint('inventory', __name__, url_prefix='/api/inventory')
billing_bp = Blueprint('billing', __name__, url_prefix='/api/billing')
customers_bp = Blueprint('customers', __name__, url_prefix='/api/customers')
chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/api/chatbot')
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')
reports_bp = Blueprint('reports', __name__, url_prefix='/api/reports')
payments_bp = Blueprint('payments', __name__, url_prefix='/api/payments')
email_bp = Blueprint('email', __name__, url_prefix='/api/email')

# Import routes
from . import auth
from . import inventory
from . import billing
from . import customers
from . import chatbot
from . import dashboard
from . import admin
from . import reports
from . import payments
from . import email