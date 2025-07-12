// Dashboard Main JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Babel app if not already initialized
    if (!window.babelApp) {
        console.log('Initializing Babel app from dashboard...');
        // The babel-services.js will create the babelApp instance
    }

    // Animate stats on load
    const statNumbers = document.querySelectorAll('h3');
    statNumbers.forEach(stat => {
        if (stat.textContent.match(/^\d+$/)) {
            const finalValue = parseInt(stat.textContent);
            let currentValue = 0;
            const increment = Math.ceil(finalValue / 20);
            const timer = setInterval(() => {
                currentValue += increment;
                if (currentValue >= finalValue) {
                    currentValue = finalValue;
                    clearInterval(timer);
                }
                stat.textContent = currentValue;
            }, 50);
        }
    });

    // Load friend groups
    if (typeof loadFriendGroups === 'function') {
        loadFriendGroups();
    }
});

// Modal close functionality
window.addEventListener('click', function(e) {
    const createGroupModal = document.getElementById('createGroupModal');
    const profilePictureModal = document.getElementById('profilePictureModal');
    const translationReviewModal = document.getElementById('translationReviewModal');

    if (e.target === createGroupModal) {
        closeModal();
    }
    if (e.target === profilePictureModal) {
        closeProfilePictureModal();
    }
    if (e.target === translationReviewModal) {
        closeTranslationReviewModal();
    }
});

// Admin Chat functionality
function openAdminChat() {
    // This would be populated based on user permissions
    alert('Admin Communications - Feature will be implemented based on user permissions');
}