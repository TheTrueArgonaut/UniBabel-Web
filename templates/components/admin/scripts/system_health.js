<script>
// 🎯 SYSTEM HEALTH MICROSERVICE - Single Responsibility: System monitoring
// Handles: System health dashboard, harvester status, system logs

// System health dashboard
async function loadSystemHealth() {
    const display = document.getElementById('dataDisplay');
    display.innerHTML = '<div class="text-center py-8"><div class="animate-spin w-8 h-8 border-2 border-orange-400 border-t-transparent rounded-full mx-auto mb-4"></div><p class="text-gray-400">Loading system health...</p></div>';
    announceToScreenReader('Loading system health dashboard');

    try {
        const response = await fetch('/api/admin/system-health');
        const data = await response.json();

        let html = `
            <div class="mb-6">
                <h2 class="text-2xl font-bold text-white mb-4 flex items-center gap-3">
                    <i class="ri-computer-line text-orange-400"></i>
                    System Health
                </h2>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                    <div class="bg-cards p-4 rounded-lg">
                        <p class="text-gray-400 text-sm">Active Harvesters</p>
                        <p class="text-2xl font-bold text-orange-400">${data.system_status?.active_harvesters ?? 0}</p>
                    </div>
                    <div class="bg-cards p-4 rounded-lg">
                        <p class="text-gray-400 text-sm">API Latency (ms)</p>
                        <p class="text-2xl font-bold text-yellow-400">${data.system_status?.api_latency_ms ?? 'N/A'}</p>
                    </div>
                    <div class="bg-cards p-4 rounded-lg">
                        <p class="text-gray-400 text-sm">Error Rate</p>
                        <p class="text-2xl font-bold text-red-400">${data.system_status?.error_rate ?? '0'}%</p>
                    </div>
                </div>
            </div>
        `;

        html += `
            <div class="mb-8">
                <h3 class="text-white font-semibold mb-2">Harvester Status</h3>
                <div class="overflow-x-auto">
                    <table class="w-full border-collapse">
                        <thead>
                            <tr class="border-b border-gray-700">
                                <th class="text-left py-2 px-2 text-gray-400 text-xs">Name</th>
                                <th class="text-left py-2 px-2 text-gray-400 text-xs">Status</th>
                                <th class="text-left py-2 px-2 text-gray-400 text-xs">Uptime</th>
                                <th class="text-left py-2 px-2 text-gray-400 text-xs">Last Error</th>
                            </tr>
                        </thead>
                        <tbody>
        `;
        if (Array.isArray(data.harvesters)) {
            data.harvesters.forEach(h => {
                const statusClass = h.status === 'active' ? 'text-green-400' : 'text-red-400';
                html += `<tr class="border-b border-gray-800">
                    <td class="py-2 px-2 text-gray-200">${h.name}</td>
                    <td class="py-2 px-2 ${statusClass}">${h.status}</td>
                    <td class="py-2 px-2 text-gray-300">${h.uptime}</td>
                    <td class="py-2 px-2 text-red-300">${h.last_error || '-'}</td>
                </tr>`;
            });
        }
        html += `</tbody></table></div></div>`;

        html += `
            <div class="mb-8">
                <h3 class="text-white font-semibold mb-2">Recent System Events</h3>
                <ul class="space-y-1 max-h-40 overflow-auto text-xs">
        `;
        if (Array.isArray(data.system_log)) {
            data.system_log.slice(0, 12).forEach(log => {
                html += `<li class="border-b border-gray-800 py-1 flex gap-2">
                    <span class="text-gray-500 min-w-[5.5rem]">${new Date(log.timestamp).toLocaleTimeString()}</span>
                    <span class="text-gray-300">${log.message}</span>
                </li>`;
            });
        }
        html += '</ul></div>';

        display.innerHTML = html;
        announceToScreenReader('System health information loaded');
    } catch (error) {
        display.innerHTML = `<div class="text-center py-8"><i class="ri-error-warning-line text-red-400 text-3xl mb-4"></i><p class="text-red-400">Error loading system health: ${error.message}</p></div>`;
        announceToScreenReader('Error loading system health');
    }
}

// Logs display
async function loadSystemLogs() {
    announceToScreenReader('Loading system logs');
    const display = document.getElementById('dataDisplay');
    display.innerHTML = '<div class="text-center py-8"><div class="animate-spin w-8 h-8 border-2 border-gray-400 border-t-transparent rounded-full mx-auto mb-4"></div><p class="text-gray-400">Loading system logs...</p></div>';
    
    try {
        const response = await fetch('/api/admin/system-logs');
        const data = await response.json();
        let html = `
            <div class="mb-6">
                <h2 class="text-2xl font-bold text-white mb-4 flex items-center gap-3">
                    <i class="ri-file-list-line text-gray-400"></i>
                    System Logs
                </h2>
                <div class="max-h-96 overflow-auto text-xs">
                    <table class="w-full border-collapse">
                        <thead>
                            <tr class="border-b border-gray-700">
                                <th class="text-left py-2 px-2 text-gray-400">Time</th>
                                <th class="text-left py-2 px-2 text-gray-400">Level</th>
                                <th class="text-left py-2 px-2 text-gray-400">Message</th>
                            </tr>
                        </thead>
                        <tbody>
        `;
        if (Array.isArray(data.system_logs)) {
            data.system_logs.forEach(log => {
                let levelColor = log.level === "ERROR" ? "text-red-400"
                    : log.level === "WARN" ? "text-yellow-300"
                    : log.level === "INFO" ? "text-blue-400"
                    : "text-gray-400";
                html += `<tr class="border-b border-gray-800">
                    <td class="py-2 px-2 text-gray-400">${new Date(log.timestamp).toLocaleString()}</td>
                    <td class="py-2 px-2 ${levelColor}">${log.level}</td>
                    <td class="py-2 px-2 text-gray-300">${log.message}</td>
                </tr>`;
            });
        }
        html += '</tbody></table></div></div>';

        display.innerHTML = html;
        announceToScreenReader('System logs loaded');
    } catch (error) {
        display.innerHTML = `<div class="text-center py-8"><i class="ri-error-warning-line text-red-400 text-3xl mb-4"></i><p class="text-red-400">Error loading system logs: ${error.message}</p></div>`;
        announceToScreenReader('Error loading system logs');
    }
}
</script>