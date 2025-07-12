// Friends Drawer JavaScript - Left-sliding friends management system

let friendsDrawerOpen = false;

// 1. MAIN TRIGGER FUNCTION
function openFriendsDrawer() {
    console.log('👥 Opening Friends Drawer...');
    
    // Prevent duplicate drawer
    if (document.getElementById('friends-drawer')) return;

    // Create drawer
    const drawer = document.createElement('div');
    drawer.id = 'friends-drawer';
    drawer.className = 'fixed inset-y-0 left-0 w-80 bg-gray-800 border-r border-gray-700 shadow-2xl transform -translate-x-full transition-transform duration-300 ease-in-out z-50';
    drawer.innerHTML = createFriendsDrawerHTML();
    
    document.body.appendChild(drawer);
    
    // Force reflow and animate in
    drawer.offsetHeight;
    setTimeout(() => {
        drawer.style.transform = 'translateX(0)';
    }, 10);
    
    // Load friends after drawer is visible
    setTimeout(() => {
        loadFriends();
    }, 100);
    
    // Setup event listeners
    setupFriendsDrawerListeners(drawer);
    
    friendsDrawerOpen = true;
}

// 2. HTML GENERATION FUNCTION
function createFriendsDrawerHTML() {
    return `
        <div class="flex flex-col h-full">
            <!-- Header -->
            <div class="flex items-center justify-between p-4 border-b border-gray-700 bg-gray-800">
                <div class="flex items-center gap-2">
                    <i class="ri-user-3-line text-white text-xl"></i>
                    <h3 class="text-lg font-bold text-white">Friends</h3>
                </div>
                <div class="flex items-center gap-2">
                    <button onclick="openAddFriendModal()" 
                            class="text-gray-400 hover:text-white transition-colors bg-gray-700 hover:bg-gray-600 p-2 rounded-lg"
                            title="Add friend">
                        <i class="ri-user-add-line text-lg"></i>
                    </button>
                    <button onclick="closeFriendsDrawer()" 
                            class="text-gray-400 hover:text-white transition-colors">
                        <i class="ri-close-line text-xl"></i>
                    </button>
                </div>
            </div>
            
            <!-- Search -->
            <div class="p-3 border-b border-gray-700">
                <div class="relative">
                    <i class="ri-search-line absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
                    <input
                        type="text"
                        id="friendsSearchInput"
                        class="w-full bg-gray-900 text-white rounded-lg pl-9 pr-3 py-2 border border-gray-600 focus:border-green-500/50 focus:outline-none text-sm"
                        placeholder="Search friends..."
                        onkeyup="searchFriends()"
                    >
                </div>
            </div>
            
            <!-- Status Filter -->
            <div class="p-3 border-b border-gray-700">
                <div class="flex gap-2">
                    <button class="friend-status-btn active" data-status="all">All</button>
                    <button class="friend-status-btn" data-status="online">🟢 Online</button>
                    <button class="friend-status-btn" data-status="offline">⚫ Offline</button>
                </div>
            </div>
            
            <!-- Friends List -->
            <div class="flex-1 overflow-y-auto" id="friendsList">
                <!-- Loading State -->
                <div id="friendsLoading" class="flex items-center justify-center py-8">
                    <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-green-400"></div>
                </div>
                
                <!-- Friends will be populated here -->
                <div id="friendsContainer" class="hidden"></div>
                
                <!-- Empty State -->
                <div id="friendsEmpty" class="hidden text-center py-8 px-4">
                    <div class="w-16 h-16 bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-3">
                        <i class="ri-user-3-line text-gray-400 text-2xl"></i>
                    </div>
                    <h4 class="text-white font-medium mb-1">No friends yet</h4>
                    <p class="text-gray-400 text-sm mb-4">Add some friends to start connecting!</p>
                    <button onclick="openAddFriendModal()" 
                            class="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition-colors text-sm">
                        Add Friend
                    </button>
                </div>
            </div>
        </div>
    `;
}

// 3. LOAD FRIENDS
async function loadFriends() {
    showFriendsState('loading');
    
    try {
        const response = await api.friends.getFriends();
        
        if (response.success && response.friends && response.friends.length > 0) {
            displayFriends(response.friends);
            showFriendsState('container');
        } else {
            showFriendsState('empty');
        }
    } catch (error) {
        // API not ready yet - show empty state
        showFriendsState('empty');
    }
}

// 4. DISPLAY FRIENDS
function displayFriends(friends) {
    const container = document.getElementById('friendsContainer');
    container.innerHTML = '';
    
    friends.forEach(friend => {
        const friendElement = document.createElement('div');
        friendElement.className = `friend-item flex items-center gap-3 p-3 hover:bg-gray-700/50 transition-colors border-l-2 ${friend.status === 'online' ? 'border-green-400' : 'border-transparent'}`;
        
        friendElement.innerHTML = `
            <div class="relative flex-shrink-0">
                <div class="w-12 h-12 rounded-full bg-gray-600 flex items-center justify-center text-xl cursor-pointer"
                     onclick="viewFriendProfile(${friend.id})" title="View profile">
                    ${friend.avatar || '👤'}
                </div>
                <!-- Status indicator -->
                <div class="absolute -bottom-1 -right-1 w-4 h-4 rounded-full border-2 border-gray-800 ${friend.status === 'online' ? 'bg-green-400' : 'bg-gray-500'}"></div>
            </div>
            
            <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-1">
                    <span class="font-medium text-white truncate">${friend.name}</span>
                    ${friend.status === 'online' ? '<span class="text-xs text-green-400">● online</span>' : '<span class="text-xs text-gray-500">● offline</span>'}
                </div>
                <p class="text-xs text-gray-400 truncate">@${friend.username}</p>
                ${friend.status === 'online' && friend.activity ? `<p class="text-xs text-blue-400 truncate">${friend.activity}</p>` : ''}
            </div>
            
            <!-- Action buttons -->
            <div class="flex flex-col gap-1">
                <button onclick="messageFriend(${friend.id})" 
                        class="bg-blue-500 text-white p-1 rounded text-xs hover:bg-blue-600 transition-colors"
                        title="Send message">
                    <i class="ri-message-3-line"></i>
                </button>
                <button onclick="removeFriend(${friend.id})" 
                        class="bg-gray-600 text-white p-1 rounded text-xs hover:bg-red-600 transition-colors"
                        title="Remove friend">
                    <i class="ri-user-unfollow-line"></i>
                </button>
            </div>
        `;
        
        container.appendChild(friendElement);
    });
}

// 5. UTILITY FUNCTIONS
function showFriendsState(state) {
    const loading = document.getElementById('friendsLoading');
    const container = document.getElementById('friendsContainer');
    const empty = document.getElementById('friendsEmpty');
    
    // Hide all
    loading.style.display = 'none';
    container.style.display = 'none';
    empty.style.display = 'none';
    
    // Show selected
    switch(state) {
        case 'loading':
            loading.style.display = 'flex';
            break;
        case 'container':
            container.style.display = 'block';
            break;
        case 'empty':
            empty.style.display = 'block';
            break;
    }
}

// 6. FRIEND ACTIONS
function messageFriend(friendId) {
    console.log('Messaging friend:', friendId);
    closeFriendsDrawer();
    // Open direct messages and start conversation with this friend
    openDirectMessages();
    // TODO: Pre-select this friend in the DM interface
}

function viewFriendProfile(friendId) {
    console.log('Viewing profile for friend:', friendId);
    // TODO: Open friend profile modal or page
    alert(`Viewing profile for friend ${friendId} - Profile system coming soon!`);
}

function removeFriend(friendId) {
    if (confirm('Are you sure you want to remove this friend?')) {
        api.friends.removeFriend(friendId)
            .then(response => {
                if (response.success) {
                    loadFriends(); // Refresh the list
                } else {
                    alert(response.message || 'Failed to remove friend');
                }
            })
            .catch(error => {
                console.error('Error removing friend:', error);
                alert('Failed to remove friend. Please try again.');
            });
    }
}

// 7. ADD FRIEND MODAL
function openAddFriendModal() {
    const modal = document.createElement('div');
    modal.id = 'add-friend-modal';
    modal.className = 'fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-60';
    modal.innerHTML = `
        <div class="bg-gray-800 rounded-xl max-w-md w-full mx-4 border border-gray-700">
            <div class="flex items-center justify-between p-4 border-b border-gray-700">
                <h3 class="text-lg font-bold text-white">Add Friend</h3>
                <button onclick="closeAddFriendModal()" class="text-gray-400 hover:text-white">
                    <i class="ri-close-line text-xl"></i>
                </button>
            </div>
            
            <div class="p-4 space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-300 mb-2">Find by username:</label>
                    <div class="relative">
                        <i class="ri-at-line absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
                        <input
                            type="text"
                            id="addFriendInput"
                            class="w-full bg-gray-900 text-white rounded-lg pl-9 pr-3 py-2 border border-gray-600 focus:border-green-500/50 focus:outline-none"
                            placeholder="username"
                            onkeyup="searchUsersToAdd()"
                        >
                    </div>
                    <div id="userSearchResultsAdd" class="mt-2 max-h-40 overflow-y-auto hidden"></div>
                </div>
                
                <div class="flex gap-3">
                    <button onclick="closeAddFriendModal()" 
                            class="flex-1 bg-gray-700 text-white py-2 rounded-lg hover:bg-gray-600 transition-colors">
                        Cancel
                    </button>
                    <button onclick="sendFriendRequest()" 
                            class="flex-1 bg-green-500 text-white py-2 rounded-lg hover:bg-green-600 transition-colors">
                        Send Request
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

function closeAddFriendModal() {
    const modal = document.getElementById('add-friend-modal');
    if (modal) modal.remove();
}

function searchUsersToAdd() {
    const query = document.getElementById('addFriendInput').value.trim();
    const resultsContainer = document.getElementById('userSearchResultsAdd');
    
    if (!query) {
        resultsContainer.classList.add('hidden');
        return;
    }
    
    // TODO: Search real users from API
    // For now, hide results until API is ready
    resultsContainer.classList.add('hidden');
}

function sendFriendRequest() {
    const username = document.getElementById('addFriendInput').value.trim();
    
    if (!username) {
        alert('Please enter a username.');
        return;
    }
    
    // Use API client to send friend request
    api.friends.addFriend(username)
        .then(response => {
            if (response.success) {
                alert(`Friend request sent to @${username}!`);
                closeAddFriendModal();
                loadFriends(); // Refresh friends list
            } else {
                alert(response.message || 'Failed to send friend request');
            }
        })
        .catch(error => {
            console.error('Error sending friend request:', error);
            alert('Failed to send friend request. Please try again.');
        });
}

// 8. SEARCH FUNCTIONS
function searchFriends() {
    const query = document.getElementById('friendsSearchInput').value.toLowerCase();
    const friendItems = document.querySelectorAll('.friend-item');
    
    friendItems.forEach(item => {
        const name = item.querySelector('.font-medium').textContent.toLowerCase();
        const username = item.querySelector('.text-gray-400').textContent.toLowerCase();
        
        if (name.includes(query) || username.includes(query)) {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });
}

// 9. EVENT HANDLERS
function setupFriendsDrawerListeners(drawer) {
    // Status filter buttons
    const statusButtons = drawer.querySelectorAll('.friend-status-btn');
    statusButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            statusButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            const status = btn.dataset.status;
            filterFriendsByStatus(status);
        });
    });
    
    // Click outside to close
    document.addEventListener('click', function handleClickOutside(e) {
        if (!drawer.contains(e.target) && !e.target.closest('button[onclick="openFriendsDrawer()"]')) {
            closeFriendsDrawer();
            document.removeEventListener('click', handleClickOutside);
        }
    });
    
    // ESC to close
    document.addEventListener('keydown', function handleEscape(e) {
        if (e.key === 'Escape' && friendsDrawerOpen) {
            closeFriendsDrawer();
            document.removeEventListener('keydown', handleEscape);
        }
    });
}

// 10. FILTER BY STATUS
function filterFriendsByStatus(status) {
    const friendItems = document.querySelectorAll('.friend-item');
    
    friendItems.forEach(item => {
        const isOnline = item.querySelector('.text-green-400');
        
        if (status === 'all' || 
            (status === 'online' && isOnline) ||
            (status === 'offline' && !isOnline)) {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });
}

// 11. CLOSE FUNCTION
function closeFriendsDrawer() {
    const drawer = document.getElementById('friends-drawer');
    if (drawer) {
        drawer.style.transform = 'translateX(-100%)';
        setTimeout(() => {
            drawer.remove();
        }, 300);
    }
    friendsDrawerOpen = false;
}