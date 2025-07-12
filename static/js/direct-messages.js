// Direct Messages JavaScript - Drawer-style messaging system

let dmDrawerOpen = false;
let currentConversation = null;

// 1. MAIN TRIGGER FUNCTION
function openDirectMessages() {
    console.log('💬 Opening Direct Messages...');
    
    // Prevent duplicate drawer
    if (document.getElementById('dm-drawer')) return;

    // Create drawer
    const drawer = document.createElement('div');
    drawer.id = 'dm-drawer';
    drawer.className = 'fixed inset-y-0 right-0 w-80 bg-gray-800 border-l border-gray-700 shadow-2xl transform translate-x-full transition-transform duration-300 ease-in-out z-50';
    drawer.innerHTML = createDirectMessagesHTML();
    
    document.body.appendChild(drawer);
    
    // Animate in
    setTimeout(() => {
        drawer.classList.remove('translate-x-full');
    }, 10);
    
    // Load conversations
    loadConversations();
    
    // Setup event listeners
    setupDirectMessagesListeners(drawer);
    
    dmDrawerOpen = true;
}

// 2. HTML GENERATION FUNCTION
function createDirectMessagesHTML() {
    return `
        <div class="flex flex-col h-full">
            <!-- Header -->
            <div class="flex items-center justify-between p-4 border-b border-gray-700 bg-gray-800">
                <div class="flex items-center gap-2">
                    <i class="ri-chat-3-line text-white text-xl"></i>
                    <h3 class="text-lg font-bold text-white">Direct Messages</h3>
                </div>
                <div class="flex items-center gap-2">
                    <button onclick="openNewMessageModal()" 
                            class="text-gray-400 hover:text-white transition-colors bg-gray-700 hover:bg-gray-600 p-2 rounded-lg"
                            title="New message">
                        <i class="ri-add-line text-lg"></i>
                    </button>
                    <button onclick="closeDirectMessages()" 
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
                        id="dmSearchInput"
                        class="w-full bg-gray-900 text-white rounded-lg pl-9 pr-3 py-2 border border-gray-600 focus:border-primary/50 focus:outline-none text-sm"
                        placeholder="Search conversations..."
                        onkeyup="searchConversations()"
                    >
                </div>
            </div>
            
            <!-- Conversations List -->
            <div class="flex-1 overflow-y-auto" id="conversationsList">
                <!-- Loading State -->
                <div id="dmLoading" class="flex items-center justify-center py-8">
                    <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
                </div>
                
                <!-- Conversations will be populated here -->
                <div id="dmConversations" class="hidden"></div>
                
                <!-- Empty State -->
                <div id="dmEmpty" class="hidden text-center py-8 px-4">
                    <div class="w-16 h-16 bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-3">
                        <i class="ri-chat-3-line text-gray-400 text-2xl"></i>
                    </div>
                    <h4 class="text-white font-medium mb-1">No messages yet</h4>
                    <p class="text-gray-400 text-sm mb-4">Start a conversation with someone!</p>
                    <button onclick="openNewMessageModal()" 
                            class="bg-primary text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors text-sm">
                        Send Message
                    </button>
                </div>
            </div>
        </div>
    `;
}

// 3. DATA LOADING FUNCTION
async function loadConversations() {
    showDMState('loading');
    
    try {
        // Try real API first
        const response = await fetch('/api/messages/conversations');
        const data = await response.json();
        
        if (data.success && data.conversations.length > 0) {
            displayConversations(data.conversations);
            showDMState('conversations');
        } else {
            showDMState('empty');
        }
    } catch (error) {
        console.log('Could not load conversations - API not ready yet');
        // Show empty state when API isn't available
        showDMState('empty');
    }
}

// 4. DISPLAY FUNCTION
function displayConversations(conversations) {
    const container = document.getElementById('dmConversations');
    container.innerHTML = '';
    
    conversations.forEach(conversation => {
        const conversationEl = document.createElement('div');
        conversationEl.className = `conversation-item flex items-center gap-3 p-3 hover:bg-gray-700 cursor-pointer border-l-2 ${conversation.unreadCount > 0 ? 'border-primary bg-gray-700/30' : 'border-transparent'}`;
        conversationEl.onclick = () => openConversation(conversation.id);
        
        conversationEl.innerHTML = `
            <div class="relative flex-shrink-0">
                <div class="w-12 h-12 rounded-full bg-gray-600 flex items-center justify-center text-xl">
                    ${conversation.user.avatar || '👤'}
                </div>
                <div class="absolute -bottom-1 -right-1 w-4 h-4 rounded-full border-2 border-gray-800 ${conversation.user.status === 'online' ? 'bg-green-400' : 'bg-gray-500'}"></div>
            </div>
            
            <div class="flex-1 min-w-0">
                <div class="flex items-center justify-between mb-1">
                    <span class="font-medium text-white truncate">${conversation.user.name}</span>
                    <span class="text-xs text-gray-400">${conversation.lastMessage.timestamp}</span>
                </div>
                <div class="flex items-center justify-between">
                    <p class="text-sm text-gray-300 truncate">${conversation.lastMessage.text}</p>
                    ${conversation.unreadCount > 0 ? `<div class="ml-2 min-w-5 h-5 bg-primary text-white text-xs rounded-full flex items-center justify-center font-bold">${conversation.unreadCount}</div>` : ''}
                </div>
            </div>
        `;
        
        container.appendChild(conversationEl);
    });
}

// 5. UTILITY FUNCTIONS
function showDMState(state) {
    const loading = document.getElementById('dmLoading');
    const conversations = document.getElementById('dmConversations');
    const empty = document.getElementById('dmEmpty');
    
    // Hide all
    loading.style.display = 'none';
    conversations.style.display = 'none';
    empty.style.display = 'none';
    
    // Show selected
    switch(state) {
        case 'loading':
            loading.style.display = 'flex';
            break;
        case 'conversations':
            conversations.style.display = 'block';
            break;
        case 'empty':
            empty.style.display = 'block';
            break;
    }
}

// 6. EVENT HANDLERS
function setupDirectMessagesListeners(drawer) {
    // Click outside to close
    document.addEventListener('click', function handleClickOutside(e) {
        if (!drawer.contains(e.target) && !e.target.closest('button[onclick="openDirectMessages()"]')) {
            closeDirectMessages();
            document.removeEventListener('click', handleClickOutside);
        }
    });
    
    // ESC to close
    document.addEventListener('keydown', function handleEscape(e) {
        if (e.key === 'Escape' && dmDrawerOpen) {
            closeDirectMessages();
            document.removeEventListener('keydown', handleEscape);
        }
    });
}

// 7. CONVERSATION ACTIONS
function openConversation(conversationId) {
    console.log('Opening conversation:', conversationId);
    currentConversation = conversationId;
    
    // Mark as read
    markConversationAsRead(conversationId);
    
    // TODO: Open chat interface or mini chat window
    alert(`Opening conversation ${conversationId} - Chat interface coming soon!`);
}

function markConversationAsRead(conversationId) {
    // Update UI to remove unread indicators
    const conversationEl = document.querySelector(`.conversation-item:nth-child(${conversationId})`);
    if (conversationEl) {
        conversationEl.classList.remove('border-primary', 'bg-gray-700/30');
        conversationEl.classList.add('border-transparent');
        
        // Remove unread count badge
        const unreadBadge = conversationEl.querySelector('.bg-primary.text-white');
        if (unreadBadge) {
            unreadBadge.remove();
        }
    }
    
    // Update header notification
    updateNotificationIndicator();
}

// 8. NEW MESSAGE MODAL
function openNewMessageModal() {
    // Create new message modal
    const modal = document.createElement('div');
    modal.id = 'new-message-modal';
    modal.className = 'fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-60';
    modal.innerHTML = `
        <div class="bg-gray-800 rounded-xl max-w-md w-full mx-4 border border-gray-700">
            <div class="flex items-center justify-between p-4 border-b border-gray-700">
                <h3 class="text-lg font-bold text-white">New Message</h3>
                <button onclick="closeNewMessageModal()" class="text-gray-400 hover:text-white">
                    <i class="ri-close-line text-xl"></i>
                </button>
            </div>
            
            <div class="p-4 space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-300 mb-2">Send to:</label>
                    <div class="relative">
                        <i class="ri-search-line absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
                        <input
                            type="text"
                            id="userSearchInput"
                            class="w-full bg-gray-900 text-white rounded-lg pl-9 pr-3 py-2 border border-gray-600 focus:border-primary/50 focus:outline-none"
                            placeholder="Search users by name or @username..."
                            onkeyup="searchUsers()"
                        >
                    </div>
                    <div id="userSearchResults" class="mt-2 max-h-40 overflow-y-auto hidden"></div>
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-300 mb-2">Message:</label>
                    <textarea
                        id="newMessageText"
                        class="w-full bg-gray-900 text-white rounded-lg px-3 py-2 border border-gray-600 focus:border-primary/50 focus:outline-none resize-none"
                        rows="3"
                        placeholder="Type your message..."
                    ></textarea>
                </div>
                
                <div class="flex gap-3">
                    <button onclick="closeNewMessageModal()" 
                            class="flex-1 bg-gray-700 text-white py-2 rounded-lg hover:bg-gray-600 transition-colors">
                        Cancel
                    </button>
                    <button onclick="sendNewMessage()" 
                            class="flex-1 bg-primary text-white py-2 rounded-lg hover:bg-red-700 transition-colors">
                        Send Message
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

// 9. CLOSE FUNCTIONS
function closeDirectMessages() {
    const drawer = document.getElementById('dm-drawer');
    if (drawer) {
        drawer.classList.add('translate-x-full');
        setTimeout(() => {
            drawer.remove();
        }, 300);
    }
    dmDrawerOpen = false;
}

function closeNewMessageModal() {
    const modal = document.getElementById('new-message-modal');
    if (modal) modal.remove();
}

// 10. SEARCH FUNCTIONS
function searchConversations() {
    const query = document.getElementById('dmSearchInput').value.toLowerCase();
    const conversations = document.querySelectorAll('.conversation-item');
    
    conversations.forEach(conv => {
        const name = conv.querySelector('.font-medium').textContent.toLowerCase();
        const lastMessage = conv.querySelector('.text-gray-300').textContent.toLowerCase();
        
        if (name.includes(query) || lastMessage.includes(query)) {
            conv.style.display = 'flex';
        } else {
            conv.style.display = 'none';
        }
    });
}

function searchUsers() {
    const query = document.getElementById('userSearchInput').value.trim();
    const resultsContainer = document.getElementById('userSearchResults');
    
    if (!query) {
        resultsContainer.classList.add('hidden');
        return;
    }
    
    // TODO: Search real users from API
    // For now, hide results until API is ready
    resultsContainer.classList.add('hidden');
}

// 11. MESSAGE ACTIONS
function selectUser(userId, name, username) {
    document.getElementById('userSearchInput').value = `${name} (@${username})`;
    document.getElementById('userSearchResults').classList.add('hidden');
}

function sendNewMessage() {
    const recipient = document.getElementById('userSearchInput').value;
    const message = document.getElementById('newMessageText').value.trim();
    
    if (!recipient || !message) {
        alert('Please select a recipient and enter a message.');
        return;
    }
    
    // TODO: Send message via API
    console.log('Sending message to:', recipient, 'Message:', message);
    alert('Message sent! (This would actually send via API)');
    closeNewMessageModal();
    
    // Refresh conversations
    loadConversations();
}

// 12. NOTIFICATION MANAGEMENT
function updateNotificationIndicator() {
    // TODO: Get real unread count from API
    const notificationDot = document.getElementById('dmNotificationDot');
    const unreadCount = document.getElementById('dmUnreadCount');
    
    // Hide notifications until we have real data
    if (unreadCount) unreadCount.classList.add('hidden');
    if (notificationDot) notificationDot.classList.add('hidden');
}

// 13. INITIALIZATION
document.addEventListener('DOMContentLoaded', function() {
    // Update notification indicator on load
    updateNotificationIndicator();
});