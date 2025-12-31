// Existing DOMContentLoaded listener remains unchanged

// Polling for live seat price updates
function fetchBusPrices() {
    fetch('/api/buses')
        .then(response => response.json())
        .then(data => {
            data.forEach(bus => {
                bus.seats.forEach(seat => {
                    const selector = `.price-item[data-bus-id="${bus.id}"][data-seat-type="${seat.seat_type}"] .price-value`;
                    const priceElem = document.querySelector(selector);
                    if (priceElem) {
                        const current = priceElem.textContent.trim();
                        if (current !== String(seat.price)) {
                            priceElem.textContent = seat.price;
                            showToast(`Price for ${seat.seat_type} on ${bus.bus_name} updated to ${seat.price}`, 'info');
                        }
                    }
                });
            });
        })
        .catch(err => console.error('Error fetching bus prices:', err));
}

// Start polling every 5 seconds
setInterval(fetchBusPrices, 5000);


document.addEventListener('DOMContentLoaded', () => {
    // Fade in elements with class .fade-in on scroll (simple version)
    const fadeElements = document.querySelectorAll('.fade-in');
    fadeElements.forEach(el => {
        el.style.opacity = 1; // Already handled by CSS animation, but ensures visibility if JS runs late
    });

    // Auto-hide flash messages
    const flashMessages = document.querySelectorAll('.flash-message');
    if (flashMessages.length > 0) {
        setTimeout(() => {
            flashMessages.forEach(msg => {
                msg.style.opacity = '0';
                msg.style.transform = 'translateY(-10px)';
                setTimeout(() => msg.remove(), 500);
            });
        }, 4000);
    }
});

// Helper for Toast Notifications
function showToast(message, type = 'success') {
    // Create toast container if not exists
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = 'position: fixed; bottom: 20px; right: 20px; z-index: 9999; display: flex; flex-direction: column; gap: 10px;';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.style.cssText = `
        background: var(--primary);
        color: white;
        padding: 12px 24px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        display: flex;
        align-items: center;
        gap: 10px;
        animation: slideIn 0.3s ease-out;
        min-width: 250px;
    `;

    // Icon based on type
    const icon = type === 'success' ? 'check-circle' : 'exclamation-circle';

    toast.innerHTML = `
        <i class="fas fa-${icon}"></i>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    // Remove after 3s
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-in forwards';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Add animation keyframes dynamically
const styleSheet = document.createElement("style");
styleSheet.innerText = `
@keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}
@keyframes slideOut {
    from { transform: translateX(0); opacity: 1; }
    to { transform: translateX(100%); opacity: 0; }
}
`;
document.head.appendChild(styleSheet);
