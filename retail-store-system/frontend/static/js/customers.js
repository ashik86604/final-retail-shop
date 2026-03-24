const BASE_URL = "http://localhost:5000/api/customers";

document.addEventListener('DOMContentLoaded', () => {
    console.log('Customers page loaded');
    loadCustomers();
    setupForms();
    setupSearch();
});

async function loadCustomers() {
    try {
        console.log('Loading customers...');
        const response = await fetch(`${BASE_URL}/`);
        const result = await response.json();

        console.log('Customers response:', result);

        if (result.status === 'success' && result.data.length > 0) {
            displayCustomers(result.data);
            document.getElementById('emptyState').style.display = 'none';
            document.getElementById('totalCustomers').textContent = result.count;
        } else {
            document.getElementById('customersBody').innerHTML = '';
            document.getElementById('emptyState').style.display = 'block';
            document.getElementById('totalCustomers').textContent = '0';
        }
    } catch (error) {
        console.error('Error loading customers:', error);
        showToast('Error loading customers: ' + error.message, 'danger');
    }
}

function displayCustomers(customers) {
    let rows = '';
    customers.forEach(c => {
        rows += `
            <tr>
                <td class="ps-4"><strong>#${c.id}</strong></td>
                <td>${c.name}</td>
                <td>${c.email || '-'}</td>
                <td>${c.phone || '-'}</td>
                <td><small class="text-muted">${new Date(c.created_at).toLocaleDateString('en-IN')}</small></td>
                <td class="pe-4 text-center">
                    <button class="btn btn-sm btn-info rounded-3" onclick="editCustomer(${c.id}, '${c.name.replace(/'/g, "\\'")}', '${(c.email || '').replace(/'/g, "\\'")}', '${(c.phone || '').replace(/'/g, "\\'")}')">Edit</button>
                    <button class="btn btn-sm btn-danger rounded-3" onclick="deleteCustomer(${c.id})">Delete</button>
                </td>
            </tr>
        `;
    });
    document.getElementById('customersBody').innerHTML = rows;
}

function setupForms() {
    // Add Customer
    document.getElementById('addCustomerForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const name = document.getElementById('customerName').value.trim();
        const email = document.getElementById('customerEmail').value.trim();
        const phone = document.getElementById('customerPhone').value.trim();

        const data = {
            name: name,
            email: email || null,
            phone: phone || null
        };

        try {
            const response = await fetch(`${BASE_URL}/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();

            if (result.status === 'success') {
                showToast('Customer added successfully!', 'success');
                e.target.reset();
                bootstrap.Modal.getInstance(document.getElementById('addCustomerModal')).hide();
                loadCustomers();
            } else {
                showToast(result.message || 'Failed to add customer', 'danger');
            }
        } catch (error) {
            console.error('Error adding customer:', error);
            showToast('Error adding customer: ' + error.message, 'danger');
        }
    });

    // Edit Customer
    document.getElementById('editCustomerForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = document.getElementById('editCustomerId').value;
        const data = {
            name: document.getElementById('editCustomerName').value.trim(),
            email: document.getElementById('editCustomerEmail').value.trim() || null,
            phone: document.getElementById('editCustomerPhone').value.trim() || null
        };

        try {
            const response = await fetch(`${BASE_URL}/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await response.json();

            if (result.status === 'success') {
                showToast('Customer updated!', 'success');
                bootstrap.Modal.getInstance(document.getElementById('editCustomerModal')).hide();
                loadCustomers();
            } else {
                showToast(result.message, 'danger');
            }
        } catch (error) {
            console.error('Error updating customer:', error);
            showToast('Error updating customer: ' + error.message, 'danger');
        }
    });
}

function editCustomer(id, name, email, phone) {
    document.getElementById('editCustomerId').value = id;
    document.getElementById('editCustomerName').value = name;
    document.getElementById('editCustomerEmail').value = email;
    document.getElementById('editCustomerPhone').value = phone;
    new bootstrap.Modal(document.getElementById('editCustomerModal')).show();
}

async function deleteCustomer(id) {
    if (confirm('Are you sure?')) {
        try {
            const response = await fetch(`${BASE_URL}/${id}`, { method: 'DELETE' });
            const result = await response.json();
            if (result.status === 'success') {
                showToast('Customer deleted!', 'success');
                loadCustomers();
            } else {
                showToast(result.message, 'danger');
            }
        } catch (error) {
            console.error('Error deleting customer:', error);
            showToast('Error deleting customer: ' + error.message, 'danger');
        }
    }
}

function setupSearch() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keyup', (e) => {
            const term = e.target.value.toLowerCase();
            document.querySelectorAll('#customersBody tr').forEach(row => {
                const name = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
                row.style.display = name.includes(term) ? '' : 'none';
            });
        });
    }
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center border-0 text-white bg-${type} rounded-3`;
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body fw-semibold">
                <i class="bi bi-${type === 'success' ? 'check-circle' : 'exclamation-circle'} me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    document.getElementById('toastContainer').appendChild(toast);
    new bootstrap.Toast(toast).show();
}