// ==================== AUTH HELPERS ====================

// Check if user is authenticated
function isAuthenticated() {
    return localStorage.getItem('auth_token') !== null;
}

// Get auth token
function getAuthToken() {
    return localStorage.getItem('auth_token');
}

// Get current user
function getCurrentUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
}

// Display user name in navbar
function displayUserName() {
    const user = getCurrentUser();
    const nameDisplay = document.getElementById('userNameDisplay');
    if (user && nameDisplay) {
        nameDisplay.textContent = user.full_name || user.email || 'User';
    }
}

// Handle logout
function handleLogout() {
    const token = getAuthToken();
    
    if (token) {
        // Call logout API
        fetch('http://localhost:5000/api/auth/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        }).then(() => {
            performLogout();
        }).catch(error => {
            console.error('Logout error:', error);
            performLogout();
        });
    } else {
        performLogout();
    }
}

// Actually perform logout
function performLogout() {
    // Clear storage
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    localStorage.removeItem('refresh_token');
    
    // Show message
    alert('You have been logged out successfully!');
    
    // Redirect to login
    window.location.href = '/login';
}

// Edit profile (placeholder)
function editProfile() {
    alert('Profile editing coming soon!');
}

// Check authentication on page load
document.addEventListener('DOMContentLoaded', () => {
    displayUserName();
    
    // Redirect to login if not authenticated (except on login/signup pages)
    const currentPage = window.location.pathname;
    const publicPages = ['/login', '/signup', '/auth'];
    
    if (!isAuthenticated() && !publicPages.includes(currentPage)) {
        // Only redirect if not already on login/signup page
        console.warn('User not authenticated, but allowing page access');
    }
});

// Helper to fetch with auth token
async function fetchWithAuth(url, options = {}) {
    const token = getAuthToken();
    
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    return fetch(url, {
        ...options,
        headers
    });
}