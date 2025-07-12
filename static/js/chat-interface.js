/**
 * Chat Interface - Real-time messaging with translation
 * Integrates with WebSocket client and API for live messaging
 */

class ChatInterface {
    constructor() {
        this.currentChatId = null;
        this.messages = [];
        this.typingTimeout = null;
        this.messageContainer = null;
        this.messageInput = null;
        this.isTyping = false;
        
        console.log('💬 Chat Interface initialized');
    }

    // Open chat in a modal or new window
    openChat(chatId, chatName) {
        if (this.currentChatId === chatId) {
            console.log('💬 Chat already open');
            return;
        }

        // Close previous chat if open
        if (this.currentChatId) {
            this.closeChat();
        }

        this.currentChatId = chatId;
        this.createChatModal(chatId, chatName);
        this.loadChatHistory();
        this.joinWebSocketRoom();
        
        console.log(`💬 Opened chat: ${chatName} (${chatId})`);
    }

    createChatModal(chatId, chatName) {
        // Remove existing chat modal
        const existingModal = document.getElementById('chat-interface-modal');
        if (existingModal) {
            existingModal.remove();
        }

        // Create new modal
        const modal = document.createElement('div');
        modal.id = 'chat-interface-modal';
        modal.className = 'fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50';
        modal.innerHTML = this.createChatModalHTML(chatId, chatName);
        
        document.body.appendChild(modal);
        
        // Setup event listeners
        this.setupChatEventListeners();
        
        // Focus message input
        setTimeout(() => {
            const messageInput = document.getElementById('chat-message-input');
            if (messageInput) {
                messageInput.focus();
            }
        }, 100);
    }

    createChatModalHTML(chatId, chatName) {
        return `
            <div class="bg-gray-800 rounded-xl max-w-4xl w-full mx-4 h-[600px] flex flex-col">
                <!-- Header -->
                <div class="flex items-center justify-between p-4 border-b border-gray-700">
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center border border-blue-500/50">
                            <i class="ri-chat-3-line text-xl text-blue-400"></i>
                        </div>
                        <div>
                            <h3 class="text-xl font-bold text-white">${chatName}</h3>
                            <p class="text-sm text-gray-400" id="chat-status">Loading...</p>
                        </div>
                    </div>
                    <div class="flex items-center gap-2">
                        <div id="connection-status" class="connection-status"></div>
                        <button onclick="chatInterface.popOutChat()" 
                                class="text-gray-400 hover:text-white transition-colors bg-gray-700 hover:bg-gray-600 px-3 py-1 rounded-lg text-sm"
                                title="Pop out to new window">
                            <i class="ri-external-link-line"></i> Pop Out
                        </button>
                        <button onclick="chatInterface.closeChat()" 
                                class="text-gray-400 hover:text-white">
                            <i class="ri-close-line text-xl"></i>
                        </button>
                    </div>
                </div>
                
                <!-- Messages Container -->
                <div class="flex-1 overflow-y-auto p-4 bg-gray-900/20" id="chat-messages-container">
                    <div id="chat-loading" class="text-center py-8">
                        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400"></div>
                        <p class="text-gray-400 mt-2">Loading messages...</p>
                    </div>
                    
                    <div id="chat-messages" class="space-y-3 hidden"></div>
                </div>
                
                <!-- Typing Indicators -->
                <div id="typing-indicators" class="px-4 py-2 text-sm text-gray-400" style="display: none;"></div>
                
                <!-- Message Input -->
                <div class="p-4 border-t border-gray-700 bg-gray-800">
                    <div class="flex gap-3">
                        <div class="flex-1 relative">
                            <textarea
                                id="chat-message-input"
                                class="w-full bg-gray-900 text-white rounded-lg px-4 py-3 border border-gray-600 focus:border-blue-500/50 focus:outline-none resize-none"
                                placeholder="Type your message... (Shift+Enter for new line)"
                                rows="1"
                                maxlength="2000"
                            ></textarea>
                            <div class="absolute bottom-2 right-2 text-xs text-gray-500" id="char-count">0/2000</div>
                        </div>
                        <div class="flex flex-col gap-2">
                            <button id="send-message-btn" 
                                    class="bg-blue-500 text-white px-4 py-3 rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                    disabled>
                                <i class="ri-send-plane-line"></i>
                            </button>
                            <button class="bg-gray-600 text-white px-4 py-1 rounded-lg hover:bg-gray-700 transition-colors text-sm"
                                    title="Translation settings"
                                    onclick="translationIntegration.openTranslationSettings()">
                                <i class="ri-translate-2"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    setupChatEventListeners() {
        const messageInput = document.getElementById('chat-message-input');
        const sendButton = document.getElementById('send-message-btn');
        
        if (messageInput) {
            // Auto-resize textarea
            messageInput.addEventListener('input', () => {
                this.handleMessageInput();
                this.autoResizeTextarea(messageInput);
            });

            // Send message on Enter (Shift+Enter for new line)
            messageInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });

            // Typing indicators
            messageInput.addEventListener('input', () => {
                this.handleTypingIndicator();
            });
        }

        if (sendButton) {
            sendButton.addEventListener('click', () => {
                this.sendMessage();
            });
        }

        // Register WebSocket message handler
        if (window.wsClient) {
            wsClient.registerMessageHandler(this.currentChatId, (data) => {
                this.handleIncomingMessage(data);
            });
        }
    }

    autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        const newHeight = Math.min(textarea.scrollHeight, 120); // Max 120px
        textarea.style.height = newHeight + 'px';
    }

    handleMessageInput() {
        const messageInput = document.getElementById('chat-message-input');
        const sendButton = document.getElementById('send-message-btn');
        const charCount = document.getElementById('char-count');
        
        if (messageInput && sendButton && charCount) {
            const message = messageInput.value.trim();
            const length = messageInput.value.length;
            
            sendButton.disabled = message.length === 0;
            charCount.textContent = `${length}/2000`;
            charCount.className = length > 1800 ? 'text-red-400' : 'text-gray-500';
        }
    }

    handleTypingIndicator() {
        if (!window.wsClient || !this.currentChatId) return;

        // Start typing
        if (!this.isTyping) {
            this.isTyping = true;
            wsClient.startTyping(this.currentChatId);
        }

        // Clear existing timeout
        if (this.typingTimeout) {
            clearTimeout(this.typingTimeout);
        }

        // Stop typing after 3 seconds of inactivity
        this.typingTimeout = setTimeout(() => {
            this.isTyping = false;
            wsClient.stopTyping(this.currentChatId);
        }, 3000);
    }

    async loadChatHistory() {
        try {
            const response = await api.chats.getChatHistory(this.currentChatId);
            
            if (response.success) {
                this.messages = response.messages;
                this.displayMessages();
                this.updateChatStatus(`${response.messages.length} messages loaded`);
            } else {
                this.updateChatStatus('Failed to load messages');
            }
            
        } catch (error) {
            console.error('Failed to load chat history:', error);
            this.updateChatStatus('Failed to load messages');
        }
        
        // Hide loading, show messages
        document.getElementById('chat-loading').style.display = 'none';
        document.getElementById('chat-messages').classList.remove('hidden');
    }

    displayMessages() {
        const messagesContainer = document.getElementById('chat-messages');
        if (!messagesContainer) return;

        messagesContainer.innerHTML = '';

        this.messages.forEach(message => {
            const messageElement = this.createMessageElement(message);
            messagesContainer.appendChild(messageElement);
        });

        // Scroll to bottom
        this.scrollToBottom();
    }

    createMessageElement(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message-item flex gap-3';
        messageDiv.dataset.messageId = message.id;

        const timestamp = new Date(message.created_at).toLocaleTimeString();
        const senderName = message.sender.display_name || message.sender.username;

        messageDiv.innerHTML = `
            <div class="w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center text-sm font-bold">
                ${senderName.charAt(0).toUpperCase()}
            </div>
            <div class="flex-1">
                <div class="flex items-center gap-2 mb-1">
                    <span class="font-medium text-white text-sm">${senderName}</span>
                    <span class="text-xs text-gray-400">${timestamp}</span>
                </div>
                <div class="text-gray-300 text-sm whitespace-pre-wrap message-content">${message.content}</div>
            </div>
        `;

        // Process for translation if available
        if (window.translationIntegration) {
            setTimeout(() => {
                translationIntegration.processIncomingMessage(messageDiv, message);
            }, 100);
        }

        return messageDiv;
    }

    handleIncomingMessage(data) {
        console.log('📥 Incoming message in chat:', data);
        
        // Add message to local array
        this.messages.push(data);
        
        // Add message to UI
        const messagesContainer = document.getElementById('chat-messages');
        if (messagesContainer) {
            const messageElement = this.createMessageElement(data);
            messagesContainer.appendChild(messageElement);
            this.scrollToBottom();
        }
    }

    async sendMessage() {
        const messageInput = document.getElementById('chat-message-input');
        const sendButton = document.getElementById('send-message-btn');
        
        if (!messageInput || !sendButton) return;

        const message = messageInput.value.trim();
        if (!message) return;

        // Disable input while sending
        sendButton.disabled = true;
        messageInput.disabled = true;

        try {
            // Send via API first
            const response = await api.chats.sendMessage(this.currentChatId, message);
            
            if (response.success) {
                // Clear input
                messageInput.value = '';
                messageInput.style.height = 'auto';
                
                // Send via WebSocket for real-time
                if (window.wsClient) {
                    wsClient.sendMessage(this.currentChatId, message);
                }
                
                // Stop typing indicator
                if (this.isTyping) {
                    this.isTyping = false;
                    wsClient.stopTyping(this.currentChatId);
                }
                
                this.updateChatStatus('Message sent');
            } else {
                throw new Error(response.error || 'Failed to send message');
            }
            
        } catch (error) {
            console.error('Failed to send message:', error);
            this.updateChatStatus('Failed to send message');
        } finally {
            // Re-enable input
            sendButton.disabled = false;
            messageInput.disabled = false;
            messageInput.focus();
            this.handleMessageInput();
        }
    }

    joinWebSocketRoom() {
        if (window.wsClient && this.currentChatId) {
            wsClient.joinChat(this.currentChatId);
        }
    }

    updateChatStatus(status) {
        const statusElement = document.getElementById('chat-status');
        if (statusElement) {
            statusElement.textContent = status;
        }
    }

    scrollToBottom() {
        const container = document.getElementById('chat-messages-container');
        if (container) {
            container.scrollTop = container.scrollHeight;
        }
    }

    popOutChat() {
        // TODO: Open chat in new window
        console.log('Pop out chat feature coming soon');
    }

    closeChat() {
        if (this.currentChatId && window.wsClient) {
            wsClient.leaveChat(this.currentChatId);
            wsClient.unregisterMessageHandler(this.currentChatId);
        }

        const modal = document.getElementById('chat-interface-modal');
        if (modal) {
            modal.remove();
        }

        this.currentChatId = null;
        this.messages = [];
        
        console.log('💬 Chat closed');
    }
}

// Global chat interface instance
const chatInterface = new ChatInterface();

// Function to open chat (called from active chats)
function openChatInterface(chatId, chatName) {
    chatInterface.openChat(chatId, chatName);
}

// Export for global access
window.chatInterface = chatInterface;
window.openChatInterface = openChatInterface;