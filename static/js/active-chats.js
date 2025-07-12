// Active Chats JavaScript - Pop-out for managing active chat sessions

// 1. MAIN TRIGGER FUNCTION
function openActiveChats() {
    console.log('💬 Opening Active Chats...');
    
    // Prevent duplicate modal
    if (document.getElementById('active-chats-modal')) return;

    // Create modal
    const modal = document.createElement('div');
    modal.id = 'active-chats-modal';
    modal.className = 'fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50';
    modal.innerHTML = createActiveChatsModalHTML();
    
    document.body.appendChild(modal);
    
    // Load active chats
    loadActiveChats();
    
    // Setup event listeners
    setupActiveChatsListeners(modal);
}

// 2. HTML GENERATION FUNCTION
function createActiveChatsModalHTML() {
    return `
        <div class="bg-gray-800 rounded-xl max-w-4xl w-full mx-4 h-[600px] flex flex-col">
            <!-- Header -->
            <div class="flex items-center justify-between p-4 border-b border-gray-700">
                <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center border border-blue-500/50">
                        <i class="ri-chat-3-line text-xl text-blue-400"></i>
                    </div>
                    <div>
                        <h3 class="text-xl font-bold text-white">Active Chats</h3>
                        <p class="text-sm text-gray-400">Rejoin your ongoing conversations</p>
                    </div>
                </div>
                <div class="flex items-center gap-2">
                    <button onclick="popOutActiveChats()" 
                            class="text-gray-400 hover:text-white transition-colors bg-gray-700 hover:bg-gray-600 px-3 py-1 rounded-lg text-sm"
                            title="Pop out to new window">
                        <i class="ri-external-link-line"></i> Pop Out
                    </button>
                    <button onclick="closeActiveChats()" class="text-gray-400 hover:text-white">
                        <i class="ri-close-line text-xl"></i>
                    </button>
                </div>
            </div>
            
            <!-- Search & Filter -->
            <div class="p-4 border-b border-gray-700 bg-gray-900/30">
                <div class="relative mb-3">
                    <i class="ri-search-line absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
                    <input
                        type="text"
                        id="activeChatsSearch"
                        class="w-full bg-gray-900 text-white rounded-lg pl-9 pr-3 py-2 border border-gray-600 focus:border-blue-500/50 focus:outline-none text-sm"
                        placeholder="Search your active chats..."
                        onkeyup="searchActiveChats()"
                    >
                </div>
                
                <!-- Filter buttons -->
                <div class="flex flex-wrap gap-2">
                    <button class="chat-filter-btn active" data-filter="all">All Chats</button>
                    <button class="chat-filter-btn" data-filter="direct">Direct Messages</button>
                    <button class="chat-filter-btn" data-filter="group">Group Chats</button>
                    <button class="chat-filter-btn" data-filter="rooms">Chat Rooms</button>
                </div>
            </div>
            
            <!-- Active Chats List -->
            <div class="flex-1 overflow-y-auto p-4 bg-gray-900/20">
                <!-- Loading State -->
                <div id="activeChatsLoading" class="text-center py-12">
                    <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400"></div>
                    <p class="text-gray-400 mt-2">Loading your active chats...</p>
                </div>
                
                <!-- Active Chats Grid -->
                <div id="activeChatsGrid" class="space-y-3 hidden">
                    <!-- Chat items will be populated here -->
                </div>
                
                <!-- Empty State -->
                <div id="activeChatsEmpty" class="text-center py-12 hidden">
                    <div class="w-16 h-16 bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4">
                        <i class="ri-chat-3-line text-gray-400 text-2xl"></i>
                    </div>
                    <h3 class="text-lg font-bold text-white mb-2">No active chats</h3>
                    <p class="text-gray-400 mb-4">Start a conversation to see it here!</p>
                    <button onclick="openChatDiscovery(); closeActiveChats();" 
                            class="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition-colors">
                        Discover Chats
                    </button>
                </div>
            </div>
        </div>
    `;
}

// 3. LOAD ACTIVE CHATS
async function loadActiveChats() {
    showActiveChatsState('loading');
    
    try {
        const response = await api.chats.getActiveChats();
        
        if (response.success && response.chats && response.chats.length > 0) {
            displayActiveChats(response.chats);
            showActiveChatsState('grid');
        } else {
            showActiveChatsState('empty');
        }
    } catch (error) {
        // API not ready yet - show empty state
        showActiveChatsState('empty');
    }
}

// 4. DISPLAY ACTIVE CHATS
function displayActiveChats(chats) {
    const container = document.getElementById('activeChatsGrid');
    container.innerHTML = '';
    
    chats.forEach(chat => {
        const chatElement = document.createElement('div');
        chatElement.className = 'active-chat-item bg-gray-800/80 rounded-xl p-3 border border-gray-700 hover:border-blue-500/50 transition-all duration-300 cursor-pointer';
        chatElement.onclick = () => rejoinChat(chat.id);
        chatElement.setAttribute('data-chat-id', chat.id);
        
        chatElement.innerHTML = `
            <div class="flex items-center gap-3">
                <div class="relative flex-shrink-0">
                    <div class="w-12 h-12 rounded-full bg-blue-500/10 flex items-center justify-center">
                        <i class="ri-${chat.type === 'direct' ? 'user' : chat.type === 'group' ? 'group' : 'chat-3'}-line text-blue-400 text-xl"></i>
                    </div>
                    ${chat.unreadCount > 0 ? `<div class="absolute -top-1 -right-1 w-5 h-5 bg-primary text-white text-xs rounded-full flex items-center justify-center font-bold">${chat.unreadCount}</div>` : ''}
                </div>
                
                <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2 mb-1">
                        <h4 class="font-medium text-white truncate">${chat.name}</h4>
                        <span class="text-xs px-2 py-1 rounded-full bg-${chat.type === 'direct' ? 'green' : chat.type === 'group' ? 'purple' : 'blue'}-500/20 text-${chat.type === 'direct' ? 'green' : chat.type === 'group' ? 'purple' : 'blue'}-400">
                            ${chat.type === 'direct' ? 'DM' : chat.type === 'group' ? 'Group' : 'Room'}
                        </span>
                    </div>
                    <p class="text-sm text-gray-300 truncate">${chat.lastMessage || 'No recent messages'}</p>
                    <div class="flex items-center gap-3 mt-1 text-xs text-gray-400">
                        <span><i class="ri-user-line mr-1"></i>${chat.participantCount || 1} ${chat.participantCount === 1 ? 'participant' : 'participants'}</span>
                        <span><i class="ri-time-line mr-1"></i>${chat.lastActive || 'Active now'}</span>
                    </div>
                </div>
                
                <div class="flex flex-col gap-1">
                    <button onclick="rejoinChat(${chat.id}); event.stopPropagation();" 
                            class="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600 transition-colors">
                        Join
                    </button>
                    <button onclick="leaveChat(${chat.id}); event.stopPropagation();" 
                            class="bg-gray-600 text-white px-3 py-1 rounded text-sm hover:bg-gray-700 transition-colors">
                        Leave
                    </button>
                </div>
            </div>
        `;
        
        container.appendChild(chatElement);
    });
}

// 5. UTILITY FUNCTIONS
function showActiveChatsState(state) {
    const loading = document.getElementById('activeChatsLoading');
    const grid = document.getElementById('activeChatsGrid');
    const empty = document.getElementById('activeChatsEmpty');
    
    // Hide all
    loading.style.display = 'none';
    grid.style.display = 'none';
    empty.style.display = 'none';
    
    // Show selected
    switch(state) {
        case 'loading':
            loading.style.display = 'block';
            break;
        case 'grid':
            grid.style.display = 'block';
            break;
        case 'empty':
            empty.style.display = 'block';
            break;
    }
}

// 6. CHAT ACTIONS
function rejoinChat(chatId) {
    console.log('Rejoining chat:', chatId);
    
    // Get chat name for the interface
    const chatItem = document.querySelector(`[data-chat-id="${chatId}"]`);
    const chatName = chatItem ? chatItem.querySelector('.font-medium').textContent : `Chat ${chatId}`;
    
    // Close active chats modal
    closeActiveChats();
    
    // Open chat interface
    if (window.openChatInterface) {
        openChatInterface(chatId, chatName);
    } else {
        // Fallback to opening in new tab
        window.open(`/chat?id=${chatId}`, '_blank');
    }
}

function leaveChat(chatId) {
    if (confirm('Are you sure you want to leave this chat?')) {
        // TODO: API call to leave chat
        console.log('Leaving chat:', chatId);
        loadActiveChats(); // Refresh the list
    }
}

// 7. SEARCH FUNCTION
function searchActiveChats() {
    const query = document.getElementById('activeChatsSearch').value.toLowerCase();
    const chatItems = document.querySelectorAll('.active-chat-item');
    
    chatItems.forEach(item => {
        const name = item.querySelector('.font-medium').textContent.toLowerCase();
        const lastMessage = item.querySelector('.text-gray-300').textContent.toLowerCase();
        
        if (name.includes(query) || lastMessage.includes(query)) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

// 8. EVENT LISTENERS
function setupActiveChatsListeners(modal) {
    // Filter buttons
    const filterButtons = modal.querySelectorAll('.chat-filter-btn');
    filterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            filterButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            const filter = btn.dataset.filter;
            filterActiveChats(filter);
        });
    });
    
    // Keyboard accessibility
    modal.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeActiveChats();
        }
    });
}

// 9. FILTER FUNCTION
function filterActiveChats(filter) {
    const chatItems = document.querySelectorAll('.active-chat-item');
    
    chatItems.forEach(item => {
        const chatType = item.querySelector('.text-xs.px-2').textContent.toLowerCase();
        
        if (filter === 'all' || 
            (filter === 'direct' && chatType.includes('dm')) ||
            (filter === 'group' && chatType.includes('group')) ||
            (filter === 'rooms' && chatType.includes('room'))) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

// 10. POP OUT FUNCTION
function popOutActiveChats() {
    const popupWindow = window.open('', 'UniBabelActiveChats', 'width=1000,height=700,scrollbars=yes,resizable=yes');
    if (popupWindow) {
        const html = `<!DOCTYPE html><html><head><title>UniBabel - Active Chats</title><script src="https://cdn.tailwindcss.com"></script><link href="https://cdnjs.cloudflare.com/ajax/libs/remixicon/4.6.0/remixicon.min.css" rel="stylesheet"></head><body class="bg-gray-900 text-white"><div class="p-6"><h1 class="text-2xl font-bold mb-4">💬 Active Chats</h1><p>This is your dedicated active chats window!</p><p class="text-gray-400 mt-2">Full functionality coming soon...</p></div></body></html>`;
        popupWindow.document.write(html);
        popupWindow.document.close();
    }
}

// 11. CLOSE FUNCTION
function closeActiveChats() {
    const modal = document.getElementById('active-chats-modal');
    if (modal) modal.remove();
}

// 12. GLOBAL EVENT LISTENERS
document.addEventListener('keydown', function(e) {
    const modal = document.getElementById('active-chats-modal');
    if (modal && e.key === 'Escape') closeActiveChats();
});

window.addEventListener('click', function(e) {
    const modal = document.getElementById('active-chats-modal');
    if (modal && e.target === modal) closeActiveChats();
});