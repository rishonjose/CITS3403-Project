// Find all auth redirect buttons
// DEBUG: Confirm script loads
console.log("[DEBUG] auth-redirect.js loaded!");

document.querySelectorAll('[data-auth-redirect]').forEach(button => {
    // DEBUG: Confirm button detection
    console.log(`[DEBUG] Found button:`, button);
    
    button.addEventListener('click', (e) => {
        e.preventDefault();
        const action = button.dataset.authRedirect;
        const url = `/login?form=${action}`;
        
        // DEBUG: Show redirect URL
        console.log(`[DEBUG] Redirecting to: ${url}`);
        window.location.href = url;
    });
});