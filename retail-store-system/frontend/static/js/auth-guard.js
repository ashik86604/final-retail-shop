// ==================== SESSION MANAGEMENT ====================

const AUTH = {
    token: localStorage.getItem('auth_token'),
    user: localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')) : null,
    
    isAuthenticated() {
        return this.token !== null && this.token !== '';
    },
    
    login(token, user, refreshToken = null) {
        localStorage.setItem('auth_token', token);
        localStorage.setItem('user', JSON.stringify(user));
        if (refreshToken) {
            localStorage.setItem('refresh_token', refreshToken);
        }
        this.token = token;
        this.user = user;
    },
    
    logout() {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
        localStorage.removeItem('refresh_token');
        this.token = null;
        this.user = null;
    },
    
    getToken() {
        return this.token;
    },
    
    getUser() {
        return this.user;
    }
};
// Add to auth-guard.js
document.addEventListener('DOMContentLoaded', () => {
    const user = AUTH.getUser();
    if (user && user.role === 'admin') {
        const adminLink = document.getElementById('adminNavItem');
        if (adminLink) adminLink.style.display = 'block';
    }
});
// ==================== ROUTE PROTECTION ====================
document.addEventListener('DOMContentLoaded', () => {
    const currentPath = window.location.pathname;
    const isAuthenticated = AUTH.isAuthenticated();
    
    // Public pages
    const publicPages = ['/', '/login', '/signup'];
    const isPublicPage = publicPages.includes(currentPath);
    
    // Protected pages
    const protectedPages = ['/dashboard', '/inventory', '/billing', '/customers', '/chatbot'];
    const isProtectedPage = protectedPages.includes(currentPath);
    
    console.log(`Current path: ${currentPath}`);
    console.log(`Is authenticated: ${isAuthenticated}`);
    
    // If trying to access protected page without auth
    if (isProtectedPage && !isAuthenticated) {
        console.warn('Unauthorized access! Redirecting to login...');
        window.location.href = '/login';
        return;
    }
    
    // If accessing public page while authenticated, show dashboard
    if (isPublicPage && isAuthenticated && currentPath === '/') {
        console.log('Already logged in, redirecting to dashboard...');
        window.location.href = '/dashboard';
        return;
    }
    
    // Display user name in navbar (for protected pages)
    if (isProtectedPage && isAuthenticated) {
        displayUserName();
    }
});

// Display user name in navbar
function displayUserName() {
    const user = AUTH.getUser();
    const nameDisplay = document.getElementById('userNameDisplay');
    if (user && nameDisplay) {
        nameDisplay.textContent = user.full_name || user.email || 'User';
    }
}

// Add to auth-guard.js after displayUserName()
function checkAdminAccess() {
    const user = AUTH.getUser();
    const adminLink = document.getElementById('adminNavLink');
    const reportsLink = document.getElementById('reportsNavLink');
    
    if (user && user.role === 'admin') {
        if (adminLink) adminLink.style.display = 'block';
        if (reportsLink) reportsLink.style.display = 'block';
    } else {
        if (adminLink) adminLink.style.display = 'none';
        if (reportsLink) reportsLink.style.display = 'none';
    }
}

// Call after DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
    checkAdminAccess();
});
// ==================== LOGOUT ====================
function handleLogout() {
    const token = AUTH.getToken();
    
    if (token) {
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

function performLogout() {
    AUTH.logout();
    
    // Clear history and redirect
    window.location.href = '/login';
}

// ==================== PREVENT BACK BUTTON ====================
window.addEventListener('popstate', () => {
    if (!AUTH.isAuthenticated()) {
        window.location.href = '/login';
    }
});

// ==================== FETCH WITH AUTH ====================
function fetchWithAuth(url, options = {}) {
    const token = AUTH.getToken();
    
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