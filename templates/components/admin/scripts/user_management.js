<script>
// 🎯 USER MANAGEMENT MICROSERVICE - Single Responsibility: User administration
// Handles: User profiles, user details, admin management, status changes

// User profiles functionality
async function loadUserProfiles(sortBy = 'value') {
    const display = document.getElementById('dataDisplay');
    display.innerHTML = '<div class="text-center py-8"><div class="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full mx-auto mb-4"></div><p class="text-gray-400">Loading user profiles...</p></div>';
    
    announceToScreenReader(`Loading user profiles sorted by ${sortBy}`);

    try {
        const response = await fetch(`/api/admin/user-profiles?sort_by=${sortBy}`);
        const data = await response.json();

        let html = `
            <div class="mb-6">
                <h2 class="text-2xl font-bold text-white mb-4 flex items-center gap-3">
                    <i class="ri-user-search-line text-blue-400"></i>
                    User Profiles
                </h2>
            </div>
        `;

        if (data.users && data.users.length > 0) {
            html += `
                <div class="overflow-x-auto">
                    <table class="w-full border-collapse">
                        <thead>
                            <tr class="border-b border-gray-700">
                                <th class="text-left py-3 px-4 text-gray-400 font-medium">Username</th>
                                <th class="text-left py-3 px-4 text-gray-400 font-medium">Value</th>
                                <th class="text-left py-3 px-4 text-gray-400 font-medium">Vulnerability</th>
                                <th class="text-left py-3 px-4 text-gray-400 font-medium">Last Seen</th>
                                <th class="text-left py-3 px-4 text-gray-400 font-medium">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
            `;

            data.users.forEach(user => {
                const scoreColor = (user.vulnerability_score || 0) > 70 ? 'text-red-400' :
                                   (user.vulnerability_score || 0) > 40 ? 'text-yellow-400' : 'text-green-400';

                html += `
                    <tr class="border-b border-gray-800 hover:bg-gray-800/50">
                        <td class="py-3 px-4 text-white font-medium">${user.username}</td>
                        <td class="py-3 px-4 text-green-400">${(user.total_market_value || 0).toLocaleString()}</td>
                        <td class="py-3 px-4 ${scoreColor}">${user.vulnerability_score || 0}/100</td>
                        <td class="py-3 px-4 text-gray-300">${new Date(user.last_seen).toLocaleDateString()}</td>
                        <td class="py-3 px-4">
                            <button onclick="viewUserDetail(${user.id})" 
                                    class="bg-primary/10 text-primary px-3 py-1 rounded text-sm hover:bg-primary/20 transition-colors">
                                View Detail
                            </button>
                        </td>
                    </tr>
                `;
            });

            html += '</tbody></table></div>';
        } else {
            html += '<div class="text-center py-8"><p class="text-gray-400">No user profiles found.</p></div>';
        }

        display.innerHTML = html;
        announceToScreenReader(`User profiles loaded, showing ${data.users ? data.users.length : 0} users`);
        
    } catch (error) {
        display.innerHTML = `<div class="text-center py-8"><i class="ri-error-warning-line text-red-400 text-3xl mb-4"></i><p class="text-red-400">Error loading user profiles: ${error.message}</p></div>`;
        announceToScreenReader('Error loading user profiles');
    }
}

// User detail view
async function viewUserDetail(userId) {
    const display = document.getElementById('dataDisplay');
    display.innerHTML = '<div class="text-center py-8"><div class="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full mx-auto mb-4"></div><p class="text-gray-400">Loading user details...</p></div>';
    announceToScreenReader(`Loading details for user ${userId}`);

    try {
        const response = await fetch(`/api/admin/user/${userId}`);
        const user = await response.json();

        if (!user || !user.id) {
            display.innerHTML = `<div class="text-center py-8"><p class="text-gray-400">User not found.</p></div>`;
            announceToScreenReader('User not found');
            return;
        }

        let scoreColor = user.vulnerability_score > 70 ? 'text-red-400' : user.vulnerability_score > 40 ? 'text-yellow-400' : 'text-green-400';
        let profileHtml = `
            <div class="mb-6">
                <h2 class="text-2xl font-bold text-white mb-4 flex items-center gap-3">
                    <i class="ri-user-3-line text-blue-400"></i>
                    User Detail: ${user.username}
                </h2>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div class="bg-cards p-4 rounded-lg">
                        <p class="text-gray-400 text-sm">ID</p>
                        <p class="text-xl font-bold text-gray-200">${user.id}</p>
                    </div>
                    <div class="bg-cards p-4 rounded-lg">
                        <p class="text-gray-400 text-sm">Market Value</p>
                        <p class="text-xl font-bold text-green-400">${(user.total_market_value || 0).toLocaleString()}</p>
                    </div>
                    <div class="bg-cards p-4 rounded-lg">
                        <p class="text-gray-400 text-sm">Vulnerability</p>
                        <p class="text-xl font-bold ${scoreColor}">${user.vulnerability_score||0}/100</p>
                    </div>
                </div>
            </div>
        `;
        display.innerHTML = profileHtml;
        announceToScreenReader(`User ${user.username} loaded`);
    } catch (error) {
        display.innerHTML = `<div class="text-center py-8"><i class="ri-error-warning-line text-red-400 text-3xl mb-4"></i><p class="text-red-400">Error loading user details: ${error.message}</p></div>`;
        announceToScreenReader('Error loading user detail');
    }
}

// User management
async function loadUserManagement() {
    const display = document.getElementById('dataDisplay');
    display.innerHTML = '<div class="text-center py-8"><div class="animate-spin w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full mx-auto mb-4"></div><p class="text-gray-400">Loading user management...</p></div>';
    announceToScreenReader('Loading user management');

    try {
        const response = await fetch('/api/admin/user-management');
        const data = await response.json();
        let html = `
            <div class="mb-6">
                <h2 class="text-2xl font-bold text-white mb-4 flex items-center gap-3">
                    <i class="ri-user-settings-line text-cyan-400"></i>
                    User Management
                </h2>
            </div>
        `;

        if (Array.isArray(data.admins) && data.admins.length > 0) {
            html += '<div class="overflow-x-auto"><table class="w-full border-collapse"><thead><tr class="border-b border-gray-700"><th class="text-left py-3 px-4 text-gray-400 font-medium">Username</th><th class="text-left py-3 px-4 text-gray-400 font-medium">Email</th><th class="text-left py-3 px-4 text-gray-400 font-medium">Role</th><th class="text-left py-3 px-4 text-gray-400 font-medium">Status</th><th class="text-left py-3 px-4 text-gray-400 font-medium">Actions</th></tr></thead><tbody>';
            data.admins.forEach(admin => {
                html += `<tr class="border-b border-gray-800 hover:bg-gray-800/50"><td class="py-3 px-4 text-white font-medium">${admin.username}</td><td class="py-3 px-4 text-gray-400">${admin.email}</td><td class="py-3 px-4 text-green-400">${admin.role}</td><td class="py-3 px-4 text-yellow-400">${admin.status}</td><td class="py-3 px-4"><button onclick="changeUserStatus('${admin.id}','${admin.status}')" class="bg-primary/10 text-primary px-3 py-1 rounded text-sm hover:bg-primary/20 transition-colors">${admin.status === 'active' ? 'Deactivate' : 'Activate'}</button></td></tr>`;
            });
            html += '</tbody></table></div>';
        } else {
            html += '<div class="text-center py-8"><p class="text-gray-400">No admin users found.</p></div>';
        }
        html += `<div class="mt-6"><button onclick="generateInvitation()" class="bg-primary text-white px-6 py-2 rounded-button hover:bg-accent transition-colors"><i class="ri-mail-send-line mr-2"></i>Generate Invitation</button></div>`;

        display.innerHTML = html;
        announceToScreenReader('User management loaded');
    } catch (error) {
        display.innerHTML = `<div class="text-center py-8"><i class="ri-error-warning-line text-red-400 text-3xl mb-4"></i><p class="text-red-400">Error loading user management: ${error.message}</p></div>`;
        announceToScreenReader('Error loading user management');
    }
}

// Activate/Deactivate user function
async function changeUserStatus(userId, currentStatus) {
    const action = currentStatus === "active" ? "deactivate" : "activate";
    if(!confirm(`Are you sure you want to ${action} this user?`)) return;

    announceToScreenReader(`${action} user ${userId}...`);
    try {
        await fetch(`/api/admin/user/${userId}/${action}`, { method: "POST" });
        loadUserManagement();
        announceToScreenReader(`User status updated`);
    } catch (error) {
        alert('Error changing user status');
        announceToScreenReader('Error changing user status');
    }
}

// Generate admin invitation
async function generateInvitation() {
    announceToScreenReader('Generating admin invitation');
    const display = document.getElementById('dataDisplay');
    display.innerHTML = '<div class="text-center py-8"><div class="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full mx-auto mb-4"></div><p class="text-gray-400">Generating invitation...</p></div>';

    try {
        const response = await fetch('/api/admin/generate-invite', { method: "POST" });
        const data = await response.json();
        if(data.invite_link) {
            display.innerHTML = `<div class="text-center py-8"><div class="text-green-400 font-bold mb-2">Invitation Generated</div><div class="mb-2"><input type="text" value="${data.invite_link}" class="bg-gray-700 text-white px-4 py-2 rounded-lg w-96 max-w-full" readonly></div><p class="text-gray-300 text-sm">Copy and send this link to invite a new admin.</p></div>`;
            announceToScreenReader('Admin invitation link generated');
        } else {
            throw new Error('No invitation link returned');
        }
    } catch (error) {
        display.innerHTML = `<div class="text-center py-8"><i class="ri-error-warning-line text-red-400 text-3xl mb-4"></i><p class="text-red-400">Error generating invitation: ${error.message}</p></div>`;
        announceToScreenReader('Error generating invitation');
    }
}
</script>