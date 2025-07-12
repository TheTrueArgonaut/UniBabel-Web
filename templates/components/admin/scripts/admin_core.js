<script>
// 🎯 ADMIN CORE MICROSERVICE - Single Responsibility: Core admin utilities
// Handles: Screen reader announcements, animated counters, initialization

// Screen reader announcements
function announceToScreenReader(message) {
    const announcements = document.getElementById('announcements');
    announcements.textContent = message;
    setTimeout(() => announcements.textContent = '', 3000);
}

// Animated counters
function animateCounter(element, target) {
    const increment = target > 100 ? Math.ceil(target / 50) : 1;
    let current = 0;
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        element.textContent = current;
    }, 50);
}

// Initialize dashboard
window.addEventListener('load', function() {
    loadDashboardStats();
    announceToScreenReader('UniBabel Admin Dashboard loaded successfully');
});

// Add smooth scrolling for better UX
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});
</script>