<script>
// 🎯 SALES MANAGEMENT MICROSERVICE - Single Responsibility: Sales operations
// Handles: Sales data loading, sale recording, revenue tracking

// Sales management functionality
async function loadSalesData() {
    const display = document.getElementById('dataDisplay');
    display.innerHTML = '<div class="text-center py-8"><div class="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full mx-auto mb-4"></div><p class="text-gray-400">Loading sales data...</p></div>';
    
    announceToScreenReader('Loading sales data');

    try {
        const response = await fetch('/api/admin/sales-management');
        const data = await response.json();

        let html = `
            <div class="mb-6">
                <h2 class="text-2xl font-bold text-white mb-4 flex items-center gap-3">
                    <i class="ri-money-dollar-circle-line text-green-400"></i>
                    Sales Management
                </h2>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                    <div class="bg-cards p-4 rounded-lg">
                        <p class="text-gray-400 text-sm">Total Sales</p>
                        <p class="text-2xl font-bold text-white">${data.total_sales || 0}</p>
                    </div>
                    <div class="bg-cards p-4 rounded-lg">
                        <p class="text-gray-400 text-sm">Total Revenue</p>
                        <p class="text-2xl font-bold text-green-400">${(data.total_revenue || 0).toLocaleString()}</p>
                    </div>
                </div>
            </div>
        `;

        if (data.sales && data.sales.length > 0) {
            html += `
                <div class="overflow-x-auto">
                    <table class="w-full border-collapse">
                        <thead>
                            <tr class="border-b border-gray-700">
                                <th class="text-left py-3 px-4 text-gray-400 font-medium">Buyer</th>
                                <th class="text-left py-3 px-4 text-gray-400 font-medium">Data Type</th>
                                <th class="text-left py-3 px-4 text-gray-400 font-medium">Users</th>
                                <th class="text-left py-3 px-4 text-gray-400 font-medium">Price</th>
                                <th class="text-left py-3 px-4 text-gray-400 font-medium">Date</th>
                            </tr>
                        </thead>
                        <tbody>
            `;

            data.sales.forEach(sale => {
                html += `
                    <tr class="border-b border-gray-800 hover:bg-gray-800/50">
                        <td class="py-3 px-4 text-white font-medium">${sale.buyer_company}</td>
                        <td class="py-3 px-4 text-gray-300">${sale.data_type}</td>
                        <td class="py-3 px-4 text-gray-300">${sale.user_count}</td>
                        <td class="py-3 px-4 text-green-400">${(sale.sale_price || 0).toLocaleString()}</td>
                        <td class="py-3 px-4 text-gray-300">${new Date(sale.sale_date).toLocaleDateString()}</td>
                    </tr>
                `;
            });

            html += '</tbody></table></div>';
        } else {
            html += '<div class="text-center py-8"><p class="text-gray-400">No sales recorded yet.</p></div>';
        }

        display.innerHTML = html;
        announceToScreenReader(`Sales data loaded, showing ${data.sales ? data.sales.length : 0} sales records`);
        
    } catch (error) {
        display.innerHTML = `<div class="text-center py-8"><i class="ri-error-warning-line text-red-400 text-3xl mb-4"></i><p class="text-red-400">Error loading sales data: ${error.message}</p></div>`;
        announceToScreenReader('Error loading sales data');
    }
}

// Record sale functionality
function recordSale() {
    const buyer = prompt('Buyer Company:');
    const dataType = prompt('Data Type (e.g., psychological, financial):');
    const userCount = prompt('Number of Users:');
    const price = prompt('Sale Price:');

    if (buyer && dataType && userCount && price) {
        announceToScreenReader('Recording sale transaction');
        
        fetch('/api/admin/record-sale', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                buyer_company: buyer,
                data_type: dataType,
                user_count: parseInt(userCount),
                sale_price: parseFloat(price),
                industry: 'Unknown',
                purpose: 'Data analysis'
            })
        })
        .then(response => response.json())
        .then(data => {
            alert(`Sale recorded! Sale ID: ${data.sale_id}`);
            announceToScreenReader(`Sale recorded successfully with ID ${data.sale_id}`);
            loadSalesData();
        })
        .catch(error => {
            alert(`Error recording sale: ${error.message}`);
            announceToScreenReader('Error recording sale');
        });
    }
}
</script>