<script>
// 🎯 ACCESSIBILITY MICROSERVICE - Single Responsibility: ADA Compliance
// Handles: Screen reader announcements, keyboard navigation, accessibility features

// Screen reader announcements
function announceToScreenReader(message) {
    const announcements = document.getElementById('announcements');
    announcements.textContent = message;
    setTimeout(() => announcements.textContent = '', 1000);
}

// Keyboard navigation support
document.addEventListener('keydown', function(e) {
    // Alt + C to focus chat input
    if (e.altKey && e.key === 'c') {
        e.preventDefault();
        document.getElementById('messageInput').focus();
        announceToScreenReader('Chat input focused');
    }
    
    // Alt + S to focus search
    if (e.altKey && e.key === 's') {
        e.preventDefault();
        document.getElementById('searchInput').focus();
        announceToScreenReader('Search input focused');
    }
    
    // Escape to clear focus
    if (e.key === 'Escape') {
        document.activeElement.blur();
    }
});

// Character count for screen readers
messageInput.addEventListener('input', function() {
    const remaining = 1000 - this.value.length;
    if (remaining <= 50) {
        announceToScreenReader(`${remaining} characters remaining`);
    }
});

// Announce page load
document.addEventListener('DOMContentLoaded', function() {
    announceToScreenReader('UniBabel chat application loaded. Press Alt+C to focus chat input, Alt+S to focus search');
});

// High contrast mode detection
if (window.matchMedia('(prefers-contrast: high)').matches) {
    document.body.classList.add('high-contrast');
}

// Reduced motion detection
if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    document.body.classList.add('reduce-motion');
}
</script>