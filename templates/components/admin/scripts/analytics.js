<script>
// 🎯 ANALYTICS MICROSERVICE - Single Responsibility: Analytics and reporting
// Handles: Analytics dashboard, performance metrics, trend analysis

// Load real Analytics dashboard
async function loadAnalytics() {
    const display = document.getElementById('dataDisplay');
    display.innerHTML = '<div class="text-center py-8"><div class="animate-spin w-8 h-8 border-2 border-purple-400 border-t-transparent rounded-full mx-auto mb-4"></div><p class="text-gray-400">Loading analytics...</p></div>';
    announceToScreenReader('Loading analytics dashboard');

    try {
        const response = await fetch('/api/admin/analytics');
        const data = await response.json();

        let html = `
            <div class="mb-6">
                <h2 class="text-2xl font-bold text-white mb-4 flex items-center gap-3">
                    <i class="ri-bar-chart-2-line text-purple-400"></i>
                    Analytics Dashboard
                </h2>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                    <div class="bg-cards p-4 rounded-lg">
                        <p class="text-gray-400 text-sm">Revenue (Last 30d)</p>
                        <p class="text-2xl font-bold text-green-400">${(data.revenue_last_30d||0).toLocaleString()}</p>
                    </div>
                    <div class="bg-cards p-4 rounded-lg">
                        <p class="text-gray-400 text-sm">Data Sales (Last 30d)</p>
                        <p class="text-2xl font-bold text-blue-400">${data.sales_last_30d||0}</p>
                    </div>
                    <div class="bg-cards p-4 rounded-lg">
                        <p class="text-gray-400 text-sm">Avg. User Value</p>
                        <p class="text-2xl font-bold text-purple-400">${(data.average_user_value||0).toLocaleString()}</p>
                    </div>
                </div>
            </div>
        `;

        html += `
            <div class="mb-8">
                <h3 class="text-white font-semibold mb-2">Top 5 Performing Segments</h3>
                <ul class="space-y-2">
        `;
        if(Array.isArray(data.top_segments)) {
            data.top_segments.forEach(seg => {
                html += `<li class="flex justify-between border-b border-gray-700 pb-1">
                    <span class="text-gray-300">${seg.segment_name}</span>
                    <span class="text-green-400 font-bold">${(seg.revenue||0).toLocaleString()}</span>
                </li>`;
            });
        }
        html += `</ul></div>`;

        html += `
            <div class="mb-8">
                <h3 class="text-white font-semibold mb-2">Recent Trends (Days)</h3>
                <div class="overflow-x-auto">
                    <table class="w-full border-collapse">
                        <thead>
                            <tr class="border-b border-gray-700">
                                <th class="text-left py-2 px-2 text-gray-400 text-xs">Date</th>
                                <th class="text-left py-2 px-2 text-gray-400 text-xs">Revenue</th>
                                <th class="text-left py-2 px-2 text-gray-400 text-xs">Sales</th>
                                <th class="text-left py-2 px-2 text-gray-400 text-xs">New Users</th>
                            </tr>
                        </thead>
                        <tbody>
        `;
        if(Array.isArray(data.daily_trends)) {
            data.daily_trends.forEach(day => {
                html += `<tr class="border-b border-gray-800">
                    <td class="py-2 px-2 text-gray-200">${new Date(day.date).toLocaleDateString()}</td>
                    <td class="py-2 px-2 text-green-400">${(day.revenue||0).toLocaleString()}</td>
                    <td class="py-2 px-2 text-blue-400">${day.sales||0}</td>
                    <td class="py-2 px-2 text-yellow-400">${day.new_users||0}</td>
                </tr>`;
            });
        }
        html += `</tbody></table></div></div>`;

        display.innerHTML = html;
        announceToScreenReader('Analytics loaded successfully');
    } catch (error) {
        display.innerHTML = `<div class="text-center py-8"><i class="ri-error-warning-line text-red-400 text-3xl mb-4"></i><p class="text-red-400">Error loading analytics: ${error.message}</p></div>`;
        announceToScreenReader('Error loading analytics');
    }
}
</script>