// Main JavaScript file for the application
document.addEventListener('DOMContentLoaded', function() {
    // Any global initialization can go here
    console.log('Sistema de Préstamos de Computadoras iniciado');
});

// Function to show notifications (could be enhanced with a library)
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;

    // Add to page
    document.body.appendChild(notification);

    // Remove after timeout
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Add CSS for notifications (could be moved to CSS file)
const style = document.createElement('style');
style.textContent = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 24px;
        border-radius: 4px;
        color: white;
        font-weight: 500;
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
    }

    .notification-info { background-color: #3498db; }
    .notification-success { background-color: #2ecc71; }
    .notification-warning { background-color: #f1c40f; color: #333; }
    .notification-error { background-color: #e74c3c; }

    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
`;
document.head.appendChild(style);