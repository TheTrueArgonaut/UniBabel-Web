<script>
// 🎯 DATA WAREHOUSE MICROSERVICE - Single Responsibility: Data warehouse operations
// Handles: Data warehouse loading, user profiles display, data export

// Data warehouse functionality
async function loadDataWarehouse() {
    const display = document.getElementById('dataDisplay');
    display.innerHTML = '<div class="text-center py-8"><div class="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full mx-auto mb-4"></div><p class="text-gray-400">Loading data warehouse...</p></div>';
    
    announceToScreenReader('Loading data warehouse');

    try {
        const response = await fetch('/api/admin/data-warehouse');
        const data = await response.json();

        let html = `
            <div class="mb-6">
                <h2 class="text-2xl font-bold text-white mb-4 flex items-center gap-3">
                    <i class="ri-database-2-line text-primary"></i>
                    Data Warehouse
                </h2>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                    <div class="bg-cards p-4 rounded-lg">
                        <p class="text-gray-400 text-sm">Total Users Profiled</p>
                        <p class="text-2xl font-bold text-white">${data.total_users_profiled || 0}</p>
                    </div>
                    <div class="bg-cards p-4 rounded-lg">
                        <p class="text-gray-400 text-sm">Revenue Potential</p>
                        <p class="text-2xl font-bold text-green-400">${(data.total_revenue_potential || 0).toLocaleString()}</p>
                    </div>
                </div>
            </div>
        `;

        html += '<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">';
        
        for (const [userId, profile] of Object.entries(data.user_profiles || {})) {
            const vulnerabilityColor = profile.vulnerability_score > 70 ? 'border-red-500/50' :
                                       profile.vulnerability_score > 40 ? 'border-yellow-500/50' : 'border-green-500/50';
            
            const scoreColor = profile.vulnerability_score > 70 ? 'text-red-400' :
                               profile.vulnerability_score > 40 ? 'text-yellow-400' : 'text-green-400';

            html += `
                <div class="bg-cards p-4 rounded-lg border ${vulnerabilityColor}" role="article" aria-label="User ${userId} profile">
                    <div class="flex items-center justify-between mb-3">
                        <h4 class="text-white font-semibold">User ${userId}</h4>
                        <span class="text-xs ${scoreColor} bg-gray-800 px-2 py-1 rounded">${profile.vulnerability_score || 0}/100</span>
                    </div>
                    <div class="space-y-2 text-sm">
                        <p class="text-gray-400">Value: <span class="text-green-400">${(profile.total_market_value || 0).toLocaleString()}</span></p>
                        <p class="text-gray-400">Updated: <span class="text-gray-300">${new Date(profile.last_updated).toLocaleDateString()}</span></p>
                    </div>
                </div>
            `;
        }
        html += '</div>';

        display.innerHTML = html;
        announceToScreenReader(`Data warehouse loaded with ${data.total_users_profiled || 0} user profiles`);
        
    } catch (error) {
        display.innerHTML = `<div class="text-center py-8"><i class="ri-error-warning-line text-red-400 text-3xl mb-4"></i><p class="text-red-400">Error loading data warehouse: ${error.message}</p></div>`;
        announceToScreenReader('Error loading data warehouse');
    }
}

// Export data functionality
function exportData() {
    const filters = {
        min_value: parseFloat(prompt('Minimum user value:') || '0'),
        min_vulnerability: parseFloat(prompt('Minimum vulnerability score:') || '0'),
        data_categories: ['psychological', 'financial', 'behavioral']
    };

    announceToScreenReader('Exporting data with specified filters');

    fetch('/api/admin/data-export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ export_type: 'json', filters: filters })
    })
    .then(response => response.json())
    .then(data => {
        const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `data_export_${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
        announceToScreenReader('Data export completed successfully');
    })
    .catch(error => {
        alert(`Error exporting data: ${error.message}`);
        announceToScreenReader('Error exporting data');
    });
}
</script>