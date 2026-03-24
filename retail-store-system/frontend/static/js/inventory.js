const BASE_URL = "http://localhost:5000/api/inventory";

document.addEventListener('DOMContentLoaded', () => {
    console.log('Inventory page loaded');
    loadProducts();
    setupFormListeners();
    setupSearchListener();
});

// ==================== LOAD & DISPLAY PRODUCTS ====================
async function loadProducts() {
    try {
        console.log('Loading products...');
        const response = await fetch(`${BASE_URL}/`);
        const result = await response.json();

        console.log('Products response:', result);

        if (result.status === 'success' && result.data.length > 0) {
            displayProducts(result.data);
            updateStats(result.data);
            document.getElementById('emptyState').style.display = 'none';
        } else {
            document.getElementById('productsBody').innerHTML = '';
            document.getElementById('emptyState').style.display = 'block';
            document.getElementById('totalProducts').textContent = '0';
            document.getElementById('lowStockCount').textContent = '0';
            document.getElementById('totalValue').textContent = '₹0';
        }
    } catch (error) {
        console.error('Error loading products:', error);
        showToast('Error loading products: ' + error.message, 'danger');
    }
}

function displayProducts(products) {
    let rows = '';
    products.forEach(product => {
        const isLowStock = product.quantity < 5;
        const statusBadge = isLowStock 
            ? `<span class="badge bg-danger"><i class="bi bi-exclamation-circle"></i> Low Stock</span>`
            : `<span class="badge bg-success"><i class="bi bi-check-circle"></i> In Stock</span>`;

        rows += `
            <tr>
                <td class="ps-4"><strong>#${product.id}</strong></td>
                <td>
                    <div>
                        <strong>${product.name}</strong>
                    </div>
                </td>
                <td>
                    <strong>₹${parseFloat(product.price).toFixed(2)}</strong>
                </td>
                <td>
                    <span class="badge ${isLowStock ? 'bg-danger' : 'bg-secondary'} rounded-pill">
                        ${product.quantity} units
                    </span>
                </td>
                <td>
                    ${statusBadge}
                </td>
                <td>
                    <small class="text-muted">
                        ${new Date(product.created_at).toLocaleDateString('en-IN')}
                    </small>
                </td>
                <td class="pe-4">
                    <button class="btn btn-sm btn-info rounded-3" onclick="showEditModal(${product.id}, '${product.name.replace(/'/g, "\\'")}', ${product.price}, ${product.quantity})">
                        <i class="bi bi-pencil-square"></i> Edit
                    </button>
                    <button class="btn btn-sm btn-danger rounded-3" onclick="showDeleteModal(${product.id})">
                        <i class="bi bi-trash"></i> Delete
                    </button>
                </td>
            </tr>
        `;
    });
    document.getElementById('productsBody').innerHTML = rows;
}

function updateStats(products) {
    const totalProducts = products.length;
    const lowStockCount = products.filter(p => p.quantity < 5).length;
    const totalValue = products.reduce((sum, p) => sum + (p.price * p.quantity), 0);

    document.getElementById('totalProducts').textContent = totalProducts;
    document.getElementById('lowStockCount').textContent = lowStockCount;
    document.getElementById('totalValue').textContent = `₹${totalValue.toFixed(2)}`;
}

// ==================== FORM HANDLERS ====================
function setupFormListeners() {
    // Add Product
    document.getElementById('addProductForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = {
            name: document.getElementById('productName').value.trim(),
            price: parseFloat(document.getElementById('productPrice').value),
            quantity: parseInt(document.getElementById('productQty').value)
        };

        try {
            const response = await fetch(`${BASE_URL}/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
            const result = await response.json();

            if (result.status === 'success') {
                showToast('Product added successfully!', 'success');
                document.getElementById('addProductForm').reset();
                bootstrap.Modal.getInstance(document.getElementById('addProductModal')).hide();
                loadProducts();
            } else {
                showToast(result.message || 'Failed to add product', 'danger');
            }
        } catch (error) {
            console.error('Error:', error);
            showToast('Error adding product: ' + error.message, 'danger');
        }
    });

    // Edit Product
    document.getElementById('editProductForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const productId = document.getElementById('editProductId').value;
        const formData = {
            name: document.getElementById('editProductName').value.trim(),
            price: parseFloat(document.getElementById('editProductPrice').value),
            quantity: parseInt(document.getElementById('editProductQty').value)
        };

        try {
            const response = await fetch(`${BASE_URL}/${productId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
            const result = await response.json();

            if (result.status === 'success') {
                showToast('Product updated successfully!', 'success');
                bootstrap.Modal.getInstance(document.getElementById('editProductModal')).hide();
                loadProducts();
            } else {
                showToast(result.message || 'Failed to update product', 'danger');
            }
        } catch (error) {
            console.error('Error:', error);
            showToast('Error updating product: ' + error.message, 'danger');
        }
    });
}

// ==================== MODAL CONTROLS ====================
function showEditModal(id, name, price, quantity) {
    document.getElementById('editProductId').value = id;
    document.getElementById('editProductName').value = name;
    document.getElementById('editProductPrice').value = price;
    document.getElementById('editProductQty').value = quantity;
    new bootstrap.Modal(document.getElementById('editProductModal')).show();
}

function showDeleteModal(id) {
    document.getElementById('deleteProductId').value = id;
    new bootstrap.Modal(document.getElementById('deleteProductModal')).show();
}

async function confirmDelete() {
    const productId = document.getElementById('deleteProductId').value;

    try {
        const response = await fetch(`${BASE_URL}/${productId}`, {
            method: 'DELETE'
        });
        const result = await response.json();

        if (result.status === 'success') {
            showToast('Product deleted successfully!', 'success');
            bootstrap.Modal.getInstance(document.getElementById('deleteProductModal')).hide();
            loadProducts();
        } else {
            showToast(result.message || 'Failed to delete product', 'danger');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Error deleting product: ' + error.message, 'danger');
    }
}

// ==================== SEARCH FUNCTIONALITY ====================
function setupSearchListener() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keyup', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            const rows = document.querySelectorAll('#productsBody tr');

            rows.forEach(row => {
                const productName = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
                if (productName.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }
}

// ==================== TOAST NOTIFICATIONS ====================
function showToast(message, type = 'info') {
    const toastHTML = `
        <div class="toast align-items-center border-0 text-white bg-${type} rounded-3" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body fw-semibold">
                    <i class="bi bi-${type === 'success' ? 'check-circle' : 'exclamation-circle'} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;

    const toastContainer = document.getElementById('toastContainer');
    if (toastContainer) {
        toastContainer.insertAdjacentHTML('beforeend', toastHTML);
        const toastElement = toastContainer.lastElementChild;
        const toast = new bootstrap.Toast(toastElement);
        toast.show();

        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }
}