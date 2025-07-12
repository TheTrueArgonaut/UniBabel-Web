/**
 * WebSocket Client - Real-time messaging integration
 * Handles live messaging, typing indicators, presence updates
 */

class WebSocketClient {
    constructor() {
        this.socket = null;
        this.connected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.currentChatId = null;
        this.messageHandlers = new Map();
        this.typingUsers = new Map();
        this.userPresence = new Map();
        
        console.log('🔌 WebSocket Client initialized');
    }

    // Connection management
    connect() {
        if (this.socket && this.connected) {
            console.log('🔌 Already connected to WebSocket');
            return;
        }

        try {
            // Initialize Socket.IO connection
            this.socket = io({
                transports: ['websocket', 'polling'],
                upgrade: true,
                rememberUpgrade: true
            });

            this.setupEventHandlers();
            console.log('🔌 Connecting to WebSocket...');

        } catch (error) {
            console.error('🔌 Failed to connect to WebSocket:', error);
            this.scheduleReconnect();
        }
    }

    setupEventHandlers() {
        // Connection events
        this.socket.on('connect', () => {
            console.log('✅ WebSocket connected');
            this.connected = true;
            this.reconnectAttempts = 0;
            this.onConnected();
        });

        this.socket.on('disconnect', (reason) => {
            console.log('❌ WebSocket disconnected:', reason);
            this.connected = false;
            this.onDisconnected(reason);
            
            if (reason === 'io server disconnect') {
                // Server initiated disconnect, reconnect manually
                this.scheduleReconnect();
            }
        });

        this.socket.on('connect_error', (error) => {
            console.error('🔌 WebSocket connection error:', error);
            this.scheduleReconnect();
        });

        // Message events
        this.socket.on('new_message', (data) => {
            this.handleNewMessage(data);
        });

        this.socket.on('message_updated', (data) => {
            this.handleMessageUpdated(data);
        });

        this.socket.on('message_deleted', (data) => {
            this.handleMessageDeleted(data);
        });

        // Typing events
        this.socket.on('user_typing', (data) => {
            this.handleUserTyping(data);
        });

        this.socket.on('user_stopped_typing', (data) => {
            this.handleUserStoppedTyping(data);
        });

        // Presence events
        this.socket.on('user_online', (data) => {
            this.handleUserOnline(data);
        });

        this.socket.on('user_offline', (data) => {
            this.handleUserOffline(data);
        });

        // Chat events
        this.socket.on('user_joined_chat', (data) => {
            this.handleUserJoinedChat(data);
        });

        this.socket.on('user_left_chat', (data) => {
            this.handleUserLeftChat(data);
        });

        // Friend events
        this.socket.on('friend_request', (data) => {
            this.handleFriendRequest(data);
        });

        this.socket.on('friend_accepted', (data) => {
            this.handleFriendAccepted(data);
        });
    }

    // Reconnection logic
    scheduleReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('🔌 Max reconnection attempts reached');
            return;
        }

        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts);
        this.reconnectAttempts++;

        console.log(`🔌 Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
        
        setTimeout(() => {
            this.connect();
        }, delay);
    }

    // Event handlers
    onConnected() {
        // Join user's personal room for notifications
        this.socket.emit('join_user_room');
        
        // Join current chat if viewing one
        if (this.currentChatId) {
            this.joinChat(this.currentChatId);
        }

        // Update online status
        this.updateOnlineStatus(true);
    }

    onDisconnected(reason) {
        // Clear typing indicators
        this.typingUsers.clear();
        this.updateTypingIndicators();
        
        // Update UI to show offline state
        this.updateConnectionStatus(false);
    }

    // Message handling
    handleNewMessage(data) {
        console.log('📥 New message received:', data);
        
        // Update active chats list if it's open
        if (document.getElementById('active-chats-modal')) {
            this.updateActiveChatsUI();
        }

        // Update activity feed
        this.updateActivityFeed();

        // Show notification if not in the chat
        if (data.chat_id !== this.currentChatId) {
            this.showMessageNotification(data);
        }

        // Call registered message handlers
        this.messageHandlers.forEach((handler, chatId) => {
            if (chatId === data.chat_id) {
                handler(data);
            }
        });
    }

    handleMessageUpdated(data) {
        console.log('📝 Message updated:', data);
        // Handle message edits
    }

    handleMessageDeleted(data) {
        console.log('🗑️ Message deleted:', data);
        // Handle message deletions
    }

    // Typing indicators
    handleUserTyping(data) {
        if (data.chat_id === this.currentChatId && data.user_id !== this.getCurrentUserId()) {
            this.typingUsers.set(data.user_id, {
                username: data.username,
                timestamp: Date.now()
            });
            this.updateTypingIndicators();
        }
    }

    handleUserStoppedTyping(data) {
        if (data.chat_id === this.currentChatId) {
            this.typingUsers.delete(data.user_id);
            this.updateTypingIndicators();
        }
    }

    updateTypingIndicators() {
        const typingContainer = document.getElementById('typing-indicators');
        if (!typingContainer) return;

        const typingUsernames = Array.from(this.typingUsers.values())
            .map(user => user.username);

        if (typingUsernames.length === 0) {
            typingContainer.innerHTML = '';
            typingContainer.style.display = 'none';
        } else {
            const text = typingUsernames.length === 1 
                ? `${typingUsernames[0]} is typing...`
                : `${typingUsernames.slice(0, -1).join(', ')} and ${typingUsernames[typingUsernames.length - 1]} are typing...`;
            
            typingContainer.innerHTML = `<div class="typing-indicator">${text}</div>`;
            typingContainer.style.display = 'block';
        }
    }

    // Presence handling
    handleUserOnline(data) {
        console.log('🟢 User online:', data);
        this.userPresence.set(data.user_id, 'online');
        this.updateUserPresenceUI(data.user_id, 'online');
        this.updateActivityFeed();
    }

    handleUserOffline(data) {
        console.log('⚫ User offline:', data);
        this.userPresence.set(data.user_id, 'offline');
        this.updateUserPresenceUI(data.user_id, 'offline');
    }

    updateUserPresenceUI(userId, status) {
        // Update friends drawer if open
        const friendsDrawer = document.getElementById('friends-drawer');
        if (friendsDrawer) {
            const friendElement = friendsDrawer.querySelector(`[data-user-id="${userId}"]`);
            if (friendElement) {
                const statusDot = friendElement.querySelector('.status-dot');
                if (statusDot) {
                    statusDot.className = `status-dot ${status === 'online' ? 'bg-green-400' : 'bg-gray-500'}`;
                }
            }
        }
    }

    // Chat events
    handleUserJoinedChat(data) {
        console.log('👋 User joined chat:', data);
        // Update participant list
    }

    handleUserLeftChat(data) {
        console.log('👋 User left chat:', data);
        // Update participant list
    }

    // Friend events
    handleFriendRequest(data) {
        console.log('👥 Friend request received:', data);
        this.showFriendRequestNotification(data);
        this.updateActivityFeed();
    }

    handleFriendAccepted(data) {
        console.log('✅ Friend request accepted:', data);
        this.showFriendAcceptedNotification(data);
        this.updateActivityFeed();
    }

    // Public API methods
    joinChat(chatId) {
        if (!this.connected) {
            console.warn('🔌 Not connected to WebSocket');
            return;
        }

        this.currentChatId = chatId;
        this.socket.emit('join_chat', { chat_id: chatId });
        console.log(`🚪 Joined chat: ${chatId}`);
    }

    leaveChat(chatId) {
        if (!this.connected) return;

        this.socket.emit('leave_chat', { chat_id: chatId });
        
        if (this.currentChatId === chatId) {
            this.currentChatId = null;
        }
        
        console.log(`🚪 Left chat: ${chatId}`);
    }

    sendMessage(chatId, message) {
        if (!this.connected) {
            console.warn('🔌 Not connected to WebSocket');
            return false;
        }

        this.socket.emit('send_message', {
            chat_id: chatId,
            message: message
        });

        return true;
    }

    startTyping(chatId) {
        if (!this.connected) return;

        this.socket.emit('start_typing', { chat_id: chatId });
    }

    stopTyping(chatId) {
        if (!this.connected) return;

        this.socket.emit('stop_typing', { chat_id: chatId });
    }

    updateOnlineStatus(isOnline) {
        if (!this.connected) return;

        this.socket.emit('update_online_status', { online: isOnline });
    }

    // Message handler registration
    registerMessageHandler(chatId, handler) {
        this.messageHandlers.set(chatId, handler);
    }

    unregisterMessageHandler(chatId) {
        this.messageHandlers.delete(chatId);
    }

    // Utility methods
    getCurrentUserId() {
        // Get current user ID from API or session
        return window.currentUserId || null;
    }

    updateActiveChatsUI() {
        // Refresh active chats list
        if (typeof loadActiveChats === 'function') {
            loadActiveChats();
        }
    }

    updateActivityFeed() {
        // Refresh activity feed
        if (typeof loadRealActivityMessages === 'function') {
            loadRealActivityMessages();
        }
    }

    updateConnectionStatus(connected) {
        const statusIndicator = document.getElementById('connection-status');
        if (statusIndicator) {
            statusIndicator.className = connected 
                ? 'connection-status online'
                : 'connection-status offline';
        }
    }

    // Notification methods
    showMessageNotification(data) {
        if (Notification.permission === 'granted') {
            new Notification(`New message from ${data.sender.username}`, {
                body: data.message,
                icon: '/static/img/unibabel-icon.png'
            });
        }
    }

    showFriendRequestNotification(data) {
        if (Notification.permission === 'granted') {
            new Notification('New friend request', {
                body: `${data.sender.username} wants to be your friend`,
                icon: '/static/img/unibabel-icon.png'
            });
        }
    }

    showFriendAcceptedNotification(data) {
        if (Notification.permission === 'granted') {
            new Notification('Friend request accepted', {
                body: `${data.friend.username} accepted your friend request`,
                icon: '/static/img/unibabel-icon.png'
            });
        }
    }

    // Cleanup
    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
        }
        this.connected = false;
        console.log('🔌 WebSocket disconnected');
    }
}

// Global WebSocket client instance
const wsClient = new WebSocketClient();

// Auto-connect when page loads
document.addEventListener('DOMContentLoaded', () => {
    // Request notification permission
    if ('Notification' in window) {
        Notification.requestPermission();
    }
    
    // Connect to WebSocket
    wsClient.connect();
    
    // Update online status periodically
    setInterval(() => {
        wsClient.updateOnlineStatus(true);
    }, 60000); // Every minute
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        wsClient.updateOnlineStatus(false);
    } else {
        wsClient.updateOnlineStatus(true);
    }
});

// Handle page unload
window.addEventListener('beforeunload', () => {
    wsClient.updateOnlineStatus(false);
    wsClient.disconnect();
});

// Export for global access
window.wsClient = wsClient;