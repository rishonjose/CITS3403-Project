// DEBUG: Confirm script loads
console.log("[DEBUG] auth-redirect.js loaded!");

// Handle authentication redirect buttons (login/signup)
document.querySelectorAll('[data-auth-redirect]').forEach(button => {
    console.log(`[DEBUG] Found auth button:`, button);
    
    button.addEventListener('click', (e) => {
        e.preventDefault();
        const action = button.dataset.authRedirect || 'login'; // Default to login
        const url = `/login?form=${action}`;
        
        console.log(`[DEBUG] Redirecting to: ${url}`);
        window.location.href = url;
    });
});

// Handle regular page redirect buttons
document.querySelectorAll('[data-page-redirect]').forEach(button => {
    console.log(`[DEBUG] Found page redirect button:`, button);
    
    button.addEventListener('click', (e) => {
        e.preventDefault();
        const url = button.dataset.href;
        
        if (url) {
            console.log(`[DEBUG] Redirecting to: ${url}`);
            window.location.href = url;
        } else {
            console.error('[ERROR] No href specified for redirect');
        }
    });
});