from flask import request, jsonify
from routes import email_bp
from supabase_client import get_supabase
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.units import inch
import io

load_dotenv()

supabase = get_supabase()

SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')

# ============================================
# GENERATE PDF INVOICE
# ============================================
def generate_invoice_pdf(bill_data, customer_data):
    """Generate PDF invoice"""
    try:
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30,
            alignment=1
        )
        
        # Header
        elements.append(Paragraph('RetailHub Invoice', title_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Bill details
        bill_info = f"""
        <b>Bill ID:</b> #{bill_data['id']}<br/>
        <b>Date:</b> {bill_data['bill_date'][:10]}<br/>
        <b>Customer:</b> {customer_data['name']}<br/>
        <b>Email:</b> {customer_data['email']}<br/>
        <b>Phone:</b> {customer_data['phone']}
        """
        elements.append(Paragraph(bill_info, styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Items table
        items = bill_data.get('items', [])
        table_data = [['Product ID', 'Qty', 'Price (₹)', 'Total (₹)']]
        
        for item in items:
            qty = float(item.get('quantity', 0))
            price = float(item.get('price', 0))
            total = qty * price
            table_data.append([
                str(item.get('product_id', '')),
                str(int(qty)),
                f"{price:.2f}",
                f"{total:.2f}"
            ])
        
        # Add totals
        table_data.append(['', '', '', ''])
        table_data.append(['', 'Subtotal:', '', f"₹{bill_data['total_amount']:.2f}"])
        table_data.append(['', 'GST (18%):', '', f"₹{bill_data['gst_amount']:.2f}"])
        table_data.append(['', 'Total:', '', f"₹{bill_data['final_amount']:.2f}"])
        
        table = Table(table_data, colWidths=[2*inch, 1*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -4), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph('Thank you for your purchase!', styles['Normal']))
        
        doc.build(elements)
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()
    
    except Exception as e:
        print(f"PDF generation error: {str(e)}")
        return None


# ============================================
# SEND INVOICE EMAIL
# ============================================
@email_bp.route('/send-invoice', methods=['POST'])
def send_invoice_email():
    """Send invoice via email"""
    try:
        data = request.get_json()
        
        bill_id = data.get('bill_id')
        recipient_email = data.get('recipient_email')
        
        if not bill_id or not recipient_email:
            return jsonify({
                'status': 'error',
                'message': 'bill_id and recipient_email required'
            }), 400
        
        # Get bill data
        bill_res = supabase.table('bills').select('*').eq('id', int(bill_id)).execute()
        if not bill_res.data:
            return jsonify({
                'status': 'error',
                'message': 'Bill not found'
            }), 404
        
        bill = bill_res.data[0]
        
        # Get customer data
        cust_res = supabase.table('customers').select('*').eq('id', bill['customer_id']).execute()
        customer = cust_res.data[0] if cust_res.data else {'name': 'N/A', 'email': 'N/A', 'phone': 'N/A'}
        
        # Generate PDF
        pdf_data = generate_invoice_pdf(bill, customer)
        if not pdf_data:
            return jsonify({
                'status': 'error',
                'message': 'Failed to generate PDF'
            }), 500
        
        # Send email
        try:
            msg = MIMEMultipart()
            msg['From'] = SENDER_EMAIL
            msg['To'] = recipient_email
            msg['Subject'] = f'Invoice #{bill_id} from RetailHub'
            
            body = f"""
            Dear {customer['name']},
            
            Please find attached your invoice from RetailHub.
            
            Bill Amount: ₹{bill['final_amount']:.2f}
            Bill Date: {bill['bill_date'][:10]}
            
            Thank you for your business!
            
            RetailHub Team
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach PDF
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(pdf_data)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename= "Invoice_{bill_id}.pdf"')
            msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
            server.quit()
            
            return jsonify({
                'status': 'success',
                'message': 'Invoice sent successfully'
            }), 200
        
        except Exception as email_error:
            return jsonify({
                'status': 'error',
                'message': f'Email send failed: {str(email_error)}'
            }), 500
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================
# GET CUSTOMER EMAILS
# ============================================
@email_bp.route('/customer-emails', methods=['GET'])
def get_customer_emails():
    """Get all customer emails for dropdown"""
    try:
        customers_res = supabase.table('customers').select('id, name, email').execute()
        customers = customers_res.data if customers_res.data else []
        
        return jsonify({
            'status': 'success',
            'data': customers
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500