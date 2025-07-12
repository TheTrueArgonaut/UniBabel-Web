<script>
// 🎯 DASHBOARD STATS MICROSERVICE - Single Responsibility: Dashboard statistics
// Handles: Loading stats, updating counters, age protection status

// Load dashboard stats
async function loadDashboardStats() {
    try {
        announceToScreenReader('Loading dashboard statistics');
        
        const response = await fetch('/api/admin/revenue-analytics');
        const data = await response.json();
        
        // Update counters with animation
        const adultUsersEl = document.getElementById('adult-users').querySelector('h3');
        const minorUsersEl = document.getElementById('minor-users').querySelector('h3');
        const highValueEl = document.getElementById('high-value').querySelector('h3');
        const vulnerableEl = document.getElementById('vulnerable').querySelector('h3');
        const harvestersEl = document.getElementById('harvesters').querySelector('h3');
        const salesEl = document.getElementById('sales').querySelector('h3');
        
        animateCounter(adultUsersEl, data.adult_users || 0);
        animateCounter(minorUsersEl, data.minor_users || 0);
        animateCounter(highValueEl, data.high_value_users || 0);
        animateCounter(vulnerableEl, data.vulnerable_users || 0);
        
        // Update revenue with currency formatting
        document.getElementById('revenue').textContent = `${(data.estimated_inventory_value || 0).toLocaleString()}`;
        
        // Age protection status
        const protectionEl = document.getElementById('protection');
        if (data.age_protection?.protection_active) {
            protectionEl.textContent = `ACTIVE (${data.age_protection.minor_users_blocked} blocked)`;
        } else {
            protectionEl.textContent = 'INACTIVE';
            protectionEl.classList.remove('text-green-400');
            protectionEl.classList.add('text-red-400');
        }
        
        // Get system status
        const systemResponse = await fetch('/api/admin/system-health');
        const systemData = await systemResponse.json();
        animateCounter(harvestersEl, systemData.system_status?.active_harvesters || 0);

        // Get sales data
        const salesResponse = await fetch('/api/admin/sales-management');
        const salesData = await salesResponse.json();
        animateCounter(salesEl, salesData.total_sales || 0);
        
        announceToScreenReader('Dashboard statistics loaded successfully');

    } catch (error) {
        console.error('Error loading dashboard stats:', error);
        announceToScreenReader('Error loading dashboard statistics');
    }
}
</script>