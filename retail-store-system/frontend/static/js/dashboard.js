const DASHBOARD_URL = 'http://localhost:5000/api/dashboard';

document.addEventListener('DOMContentLoaded', () => {
    console.log('Dashboard loaded');
    loadDashboardStats();
    loadRecentBills();
    loadTopProducts();
});

// ==================== LOAD STATS ====================
async function loadDashboardStats() {
    try {
        console.log('Loading stats...');
        const response = await fetch(`${DASHBOARD_URL}/stats`);
        const result = await response.json();

        console.log('Stats response:', result);

        if (result.status === 'success') {
            const data = result.data;
            
            // Update all stat cards
            document.getElementById('totalProducts').textContent = data.total_products;
            document.getElementById('totalCustomers').textContent = data.total_customers;
            document.getElementById('totalBills').textContent = data.total_bills;
            document.getElementById('todaySales').textContent = '₹' + data.today_sales.toFixed(2);
            
            document.getElementById('totalSales').textContent = '₹' + data.total_sales.toFixed(2);
            document.getElementById('totalGst').textContent = '₹' + data.total_gst.toFixed(2);
            document.getElementById('avgBill').textContent = '₹' + data.avg_bill.toFixed(2);
            
            document.getElementById('inventoryValue').textContent = '₹' + data.inventory_value.toFixed(2);
            document.getElementById('lowStockCount').textContent = data.low_stock_count;
            
            console.log('✅ Stats loaded successfully');
        } else {
            console.error('Error:', result.message);
            showNotification('Error loading stats', 'danger');
        }
    } catch (error) {
        console.error('Fetch error:', error);
        showNotification('Error: ' + error.message, 'danger');
    }
}

// ==================== LOAD RECENT BILLS ====================
async function loadRecentBills() {
    try {
        const response = await fetch(`${DASHBOARD_URL}/recent-bills`);
        const result = await response.json();

        if (result.status === 'success') {
            displayRecentBills(result.data);
        }
    } catch (error) {
        console.error('Error loading bills:', error);
    }
}

function displayRecentBills(bills) {
    let html = '';
    if (bills.length === 0) {
        html = '<tr><td colspan="4" class="text-center py-3 text-muted">No bills yet</td></tr>';
    } else {
        bills.forEach(bill => {
            html += `
                <tr>
                    <td class="ps-4"><strong>#${bill.id}</strong></td>
                    <td>${bill.customer_name}</td>
                    <td>₹${bill.amount.toFixed(2)}</td>
                    <td><small class="text-muted">${bill.date}</small></td>
                </tr>
            `;
        });
    }
    document.getElementById('recentBillsBody').innerHTML = html;
}

// ==================== LOAD TOP PRODUCTS ====================
async function loadTopProducts() {
    try {
        const response = await fetch(`${DASHBOARD_URL}/top-products`);
        const result = await response.json();

        if (result.status === 'success') {
            displayTopProducts(result.data);
        }
    } catch (error) {
        console.error('Error loading products:', error);
    }
}

function displayTopProducts(products) {
    let html = '';
    if (products.length === 0) {
        html = '<tr><td colspan="4" class="text-center py-3 text-muted">No products yet</td></tr>';
    } else {
        products.forEach(product => {
            html += `
                <tr>
                    <td class="ps-4"><strong>${product.name}</strong></td>
                    <td>₹${product.price.toFixed(2)}</td>
                    <td><span class="badge bg-info">${product.quantity} units</span></td>
                    <td>₹${product.value.toFixed(2)}</td>
                </tr>
            `;
        });
    }
    document.getElementById('topProductsBody').innerHTML = html;
}

// ==================== NOTIFICATIONS ====================
function showNotification(message, type = 'info') {
    console.log(`[${type}] ${message}`);
}