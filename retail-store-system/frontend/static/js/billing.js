const BILLING_URL = 'http://localhost:5000/api/billing';
const REPORTS_URL = 'http://localhost:5000/api/reports';
const PAYMENTS_URL = 'http://localhost:5000/api/payments';
const EMAIL_URL = 'http://localhost:5000/api/email';

let products = [];
let customers = [];
let currentBillId = null;
let selectedCustomerEmail = '';

document.addEventListener('DOMContentLoaded', () => {
    loadBills();
    loadProducts();
    loadCustomers();
    loadCustomerEmails();
    setupBillForm();
    setupEmailOption();
});

// ==================== LOAD DATA ====================
async function loadProducts() {
    try {
        const response = await fetch(`${BILLING_URL}/products`);
        const result = await response.json();
        if (result.status === 'success') {
            products = result.data;
            populateProductDropdown();
        }
    } catch (error) {
        console.error('Error loading products:', error);
    }
}

async function loadCustomers() {
    try {
        const response = await fetch(`${BILLING_URL}/customers`);
        const result = await response.json();
        if (result.status === 'success') {
            customers = result.data;
            populateCustomerDropdown();
        }
    } catch (error) {
        console.error('Error loading customers:', error);
    }
}

async function loadCustomerEmails() {
    try {
        const response = await fetch(`${EMAIL_URL}/customer-emails`);
        const result = await response.json();
        if (result.status === 'success') {
            const select = document.getElementById('customerEmailSelect');
            select.innerHTML = '<option value="">-- Select Customer Email --</option>';
            result.data.forEach(customer => {
                const option = document.createElement('option');
                option.value = customer.email;
                option.textContent = `${customer.name} (${customer.email})`;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading emails:', error);
    }
}

// ==================== POPULATE DROPDOWNS ====================
function populateProductDropdown() {
    const container = document.getElementById('billItemsContainer');
    const firstItem = container.querySelector('.bill-item');
    if (firstItem) {
        updateProductOptions(firstItem.querySelector('.product-select'));
    }
}

function populateCustomerDropdown() {
    const select = document.getElementById('billCustomerId');
    select.innerHTML = '<option value="">-- Select Customer --</option>';
    customers.forEach(c => {
        const option = document.createElement('option');
        option.value = c.id;
        option.textContent = `${c.name} (${c.email || 'N/A'})`;
        select.appendChild(option);
    });
}

function updateProductOptions(selectElement) {
    const currentValue = selectElement.value;
    selectElement.innerHTML = '<option value="">-- Select Product --</option>';
    products.forEach(p => {
        const option = document.createElement('option');
        option.value = p.id;
        option.textContent = `${p.name} - ₹${p.price.toFixed(2)} (Stock: ${p.quantity})`;
        option.dataset.price = p.price;
        option.dataset.stock = p.quantity;
        selectElement.appendChild(option);
    });
    selectElement.value = currentValue;
}

// ==================== EMAIL OPTION ====================
function setupEmailOption() {
    document.getElementById('emailOption')?.addEventListener('change', (e) => {
        const customContainer = document.getElementById('customEmailContainer');
        const customerContainer = document.getElementById('customerEmailContainer');
        
        if (e.target.value === 'custom') {
            customContainer.style.display = 'block';
            customerContainer.style.display = 'none';
        } else {
            customContainer.style.display = 'none';
            customerContainer.style.display = 'block';
        }
    });

    document.getElementById('customerEmailSelect')?.addEventListener('change', (e) => {
        selectedCustomerEmail = e.target.value;
    });
}

// ==================== BILL ITEMS ====================
function addBillItem() {
    const html = `
        <div class="bill-item mb-3 p-3 border rounded-3" style="background: #f9f9f9;">
            <div class="row g-2">
                <div class="col-md-4">
                    <label class="form-label small fw-semibold">Product</label>
                    <select required class="form-control rounded-3 product-select" onchange="updatePrice(this)">
                        <option value="">-- Select Product --</option>
                    </select>
                </div>
                <div class="col-md-2">
                    <label class="form-label small fw-semibold">Qty</label>
                    <input required type="number" class="form-control rounded-3 item-quantity" min="1" value="1" onchange="calculateBillTotal()">
                </div>
                <div class="col-md-3">
                    <label class="form-label small fw-semibold">Price (₹)</label>
                    <input required type="number" step="0.01" class="form-control rounded-3 item-price" readonly>
                </div>
                <div class="col-md-2">
                    <label class="form-label small fw-semibold">Total</label>
                    <input type="number" class="form-control rounded-3 item-total" readonly>
                </div>
                <div class="col-md-1">
                    <label class="form-label small fw-semibold">&nbsp;</label>
                    <button type="button" class="btn btn-danger rounded-3 btn-sm w-100" onclick="removeBillItem(this)">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
        </div>
    `;
    document.getElementById('billItemsContainer').insertAdjacentHTML('beforeend', html);
    
    // Update dropdown for new item
    const newSelect = document.querySelectorAll('.product-select');
    updateProductOptions(newSelect[newSelect.length - 1]);
}

function removeBillItem(btn) {
    btn.closest('.bill-item').remove();
    calculateBillTotal();
}

function updatePrice(selectElement) {
    const selectedOption = selectElement.options[selectElement.selectedIndex];
    const priceInput = selectElement.closest('.bill-item').querySelector('.item-price');
    priceInput.value = selectedOption.dataset.price || 0;
    calculateBillTotal();
}

function calculateBillTotal() {
    let subtotal = 0;
    
    document.querySelectorAll('.bill-item').forEach(item => {
        const qty = parseFloat(item.querySelector('.item-quantity').value) || 0;
        const price = parseFloat(item.querySelector('.item-price').value) || 0;
        const itemTotal = qty * price;
        item.querySelector('.item-total').value = itemTotal.toFixed(2);
        subtotal += itemTotal;
    });

    const gst = subtotal * 0.18;
    const total = subtotal + gst;

    document.getElementById('subtotal').textContent = subtotal.toFixed(2);
    document.getElementById('gstAmount').textContent = gst.toFixed(2);
    document.getElementById('finalAmount').textContent = total.toFixed(2);
}

// ==================== FORM SUBMISSION ====================
function setupBillForm() {
    const form = document.getElementById('createBillForm');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const customerId = document.getElementById('billCustomerId').value;
        if (!customerId) {
            showToast('Please select a customer', 'danger');
            return;
        }

        const items = [];
        document.querySelectorAll('.bill-item').forEach(item => {
            const productId = item.querySelector('.product-select').value;
            const quantity = parseFloat(item.querySelector('.item-quantity').value);
            const price = parseFloat(item.querySelector('.item-price').value);
            
            if (productId && quantity && price) {
                items.push({
                    product_id: parseInt(productId),
                    quantity: quantity,
                    price: price
                });
            }
        });

        if (items.length === 0) {
            showToast('Please add at least one item', 'danger');
            return;
        }

        const data = {
            customer_id: parseInt(customerId),
            items: items
        };

        try {
            const response = await fetch(`${BILLING_URL}/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await response.json();

            if (result.status === 'success') {
                currentBillId = result.data.id;
                const finalAmount = result.data.final_amount;
                
                // Check payment method
                const paymentMethod = document.querySelector('input[name="paymentMethod"]:checked').value;
                
                if (paymentMethod === 'cash') {
                    // For cash, send email
                    await handleBillComplete();
                } else {
                    // For online, process Razorpay
                    await initiateRazorpayPayment(currentBillId, finalAmount);
                }
            } else {
                showToast(result.message || 'Failed to create bill', 'danger');
            }
        } catch (error) {
            console.error('Error:', error);
            showToast('Error creating bill: ' + error.message, 'danger');
        }
    });
}

// ==================== PAYMENT & EMAIL ====================
async function handleBillComplete() {
    let emailToSend = '';
    if (document.getElementById('emailOption').value === 'custom') {
        emailToSend = document.getElementById('customEmail').value;
    } else {
        emailToSend = selectedCustomerEmail;
    }

    if (!emailToSend) {
        showToast('Please select or enter an email address', 'danger');
        return;
    }

    await sendInvoice(currentBillId, emailToSend);
}

async function initiateRazorpayPayment(billId, amount) {
    try {
        const orderResponse = await fetch(`${PAYMENTS_URL}/create-order`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                amount: amount,
                bill_id: billId
            })
        });

        const orderData = await orderResponse.json();

        if (orderData.status !== 'success') {
            showToast('Failed to create payment order', 'danger');
            return;
        }

        const options = {
            key: orderData.key,
            amount: orderData.amount,
            currency: "INR",
            name: "RetailHub",
            description: `Bill #${billId}`,
            order_id: orderData.order_id,
            handler: async function(response) {
                const verifyResponse = await fetch(`${PAYMENTS_URL}/verify-payment`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        payment_id: response.razorpay_payment_id,
                        order_id: response.razorpay_order_id,
                        signature: response.razorpay_signature
                    })
                });

                const verifyData = await verifyResponse.json();

                if (verifyData.status === 'success') {
                    showToast('Payment successful! Sending invoice...', 'success');
                    await handleBillComplete();
                } else {
                    showToast('Payment verification failed', 'danger');
                }
            },
            theme: {
                color: "#667eea"
            }
        };

        const rzp = new Razorpay(options);
        rzp.open();

    } catch (error) {
        showToast('Payment error: ' + error.message, 'danger');
    }
}

async function sendInvoice(billId, email) {
    try {
        const response = await fetch(`${EMAIL_URL}/send-invoice`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                bill_id: billId,
                recipient_email: email
            })
        });

        const result = await response.json();

        if (result.status === 'success') {
            showToast('✅ Bill created and invoice sent to ' + email, 'success');
            document.getElementById('createBillForm').reset();
            bootstrap.Modal.getInstance(document.getElementById('createBillModal')).hide();
            setTimeout(() => loadBills(), 2000);
        } else {
            showToast(result.message || 'Bill created but invoice sending failed', 'warning');
            loadBills();
        }
    } catch (error) {
        showToast('Email error: ' + error.message, 'warning');
        loadBills();
    }
}

// ==================== LOAD & DISPLAY BILLS ====================
async function loadBills() {
    try {
        const response = await fetch(`${BILLING_URL}/`);
        const result = await response.json();

        if (result.status === 'success' && result.data.length > 0) {
            displayBills(result.data);
            loadSummary();
            document.getElementById('emptyState').style.display = 'none';
        } else {
            document.getElementById('billsBody').innerHTML = '';
            document.getElementById('emptyState').style.display = 'block';
        }
    } catch (error) {
        console.error('Error loading bills:', error);
        showToast('Error loading bills', 'danger');
    }
}

function displayBills(bills) {
    let rows = '';
    bills.forEach(b => {
        const customerName = customers.find(c => c.id === b.customer_id)?.name || `Customer #${b.customer_id}`;
        rows += `
            <tr>
                <td class="ps-4"><strong>#${b.id}</strong></td>
                <td>${customerName}</td>
                <td>₹${parseFloat(b.total_amount).toFixed(2)}</td>
                <td>₹${parseFloat(b.gst_amount).toFixed(2)}</td>
                <td><strong>₹${parseFloat(b.final_amount).toFixed(2)}</strong></td>
                <td><small class="text-muted">${new Date(b.bill_date).toLocaleDateString('en-IN')}</small></td>
                <td class="pe-4 text-center">
                    <button class="btn btn-sm btn-info rounded-3" onclick="showBillDetails(${b.id})">View</button>
                    <button class="btn btn-sm btn-warning rounded-3" onclick="emailBill(${b.id})">Email</button>
                </td>
            </tr>
        `;
    });
    document.getElementById('billsBody').innerHTML = rows;
}

async function loadSummary() {
    try {
        const response = await fetch(`${BILLING_URL}/summary`);
        const result = await response.json();

        if (result.status === 'success') {
            const s = result.summary;
            document.getElementById('totalBills').textContent = s.total_bills;
            document.getElementById('totalSales').textContent = '₹' + s.total_sales.toFixed(2);
            document.getElementById('totalGst').textContent = '₹' + s.total_gst.toFixed(2);
            document.getElementById('avgBill').textContent = '₹' + s.average_bill.toFixed(2);
        }
    } catch (error) {
        console.error('Error loading summary:', error);
    }
}

// ==================== VIEW BILL DETAILS ====================
async function showBillDetails(billId) {
    try {
        const response = await fetch(`${BILLING_URL}/${billId}`);
        const result = await response.json();

        if (result.status === 'success') {
            const bill = result.data;
            const customer = customers.find(c => c.id === bill.customer_id) || { name: 'N/A', email: 'N/A', phone: 'N/A' };
            
            let itemsHtml = '';
            bill.items.forEach(item => {
                const product = products.find(p => p.id === item.product_id);
                const total = item.quantity * item.price;
                itemsHtml += `
                    <tr>
                        <td>${product?.name || 'Product #' + item.product_id}</td>
                        <td>${item.quantity}</td>
                        <td>₹${item.price.toFixed(2)}</td>
                        <td>₹${total.toFixed(2)}</td>
                    </tr>
                `;
            });

            const html = `
                <div class="mb-4">
                    <h6 class="fw-bold">Bill Information</h6>
                    <p><strong>Bill #:</strong> ${bill.id}</p>
                    <p><strong>Date:</strong> ${new Date(bill.bill_date).toLocaleString('en-IN')}</p>
                    <p><strong>Customer:</strong> ${customer.name}</p>
                    <p><strong>Email:</strong> ${customer.email}</p>
                    <p><strong>Phone:</strong> ${customer.phone}</p>
                </div>

                <div class="mb-4">
                    <h6 class="fw-bold">Items</h6>
                    <table class="table table-sm">
                        <thead class="table-light">
                            <tr>
                                <th>Product</th>
                                <th>Qty</th>
                                <th>Price</th>
                                <th>Total</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${itemsHtml}
                        </tbody>
                    </table>
                </div>

                <div class="bg-light p-3 rounded-3">
                    <div class="row text-end">
                        <div class="col-6">
                            <p class="text-muted mb-1">Subtotal:</p>
                            <p class="fw-bold">₹${bill.total_amount.toFixed(2)}</p>
                        </div>
                        <div class="col-6">
                            <p class="text-muted mb-1">GST (18%):</p>
                            <p class="fw-bold">₹${bill.gst_amount.toFixed(2)}</p>
                        </div>
                        <div class="col-12 mt-2 pt-2 border-top">
                            <p class="text-muted mb-1">Total Amount:</p>
                            <h5 class="fw-bold text-success">₹${bill.final_amount.toFixed(2)}</h5>
                        </div>
                    </div>
                </div>
            `;

            document.getElementById('billDetailsContent').innerHTML = html;
            new bootstrap.Modal(document.getElementById('viewBillModal')).show();
        }
    } catch (error) {
        showToast('Error loading bill details', 'danger');
    }
}

// ==================== EMAIL BILL ====================
async function emailBill(billId) {
    const email = prompt('Enter email address to send invoice:');
    if (!email) return;

    await sendInvoice(billId, email);
}

// ==================== PRINT BILL ====================
function printBill() {
    window.print();
}

// ==================== TOAST NOTIFICATIONS ====================
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center border-0 text-white bg-${type} rounded-3`;
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body fw-semibold">
                <i class="bi bi-${type === 'success' ? 'check-circle' : type === 'warning' ? 'exclamation-triangle' : 'exclamation-circle'} me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    document.getElementById('toastContainer').appendChild(toast);
    new bootstrap.Toast(toast).show();
}