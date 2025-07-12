<script>
// 🎯 CHAT CORE MICROSERVICE - Single Responsibility: Core chat messaging
// Handles: message sending, message display, message UI

let messageCount = 0;

// Send message
function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;
    
    // Announce message sent for accessibility
    announceToScreenReader(`Message sent: ${message.substring(0, 50)}${message.length > 50 ? '...' : ''}`);
    
    // Add message to UI immediately (optimistic UI)
    addMessageToUI(message, true);
    
    // Send to server via socket
    socket.emit('send_message', {
        chat_id: currentChatId,
        message: message
    });
    
    messageInput.value = '';
    messageInput.focus(); // Return focus to input
}

// Add message to UI with accessibility features
function addMessageToUI(message, isSent = false, metadata = {}) {
    messageCount++;
    const messageDiv = document.createElement('div');
    messageDiv.className = `flex items-start space-x-3 ${isSent ? 'justify-end' : ''}`;
    messageDiv.setAttribute('role', 'article');
    messageDiv.setAttribute('aria-label', `Message ${messageCount}: ${message}`);
    
    const timestamp = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    const timestampISO = new Date().toISOString();
    
    if (isSent) {
        messageDiv.innerHTML = `
            <div class="flex-1 max-w-xs">
                <div class="message-sent p-3 text-white ml-auto">
                    <p class="text-sm break-words">${message}</p>
                </div>
                <div class="mt-1 text-xs text-gray-500 text-right flex items-center justify-end space-x-2">
                    <span class="translation-badge px-2 py-0.5 rounded-full text-white" 
                          aria-label="Translation status">🌐 Translating...</span>
                    <span>•</span>
                    <time datetime="${timestampISO}" aria-label="Message sent at ${timestamp}">${timestamp}</time>
                    <i class="ri-time-line text-gray-400" aria-hidden="true"></i>
                </div>
            </div>
            <div class="w-8 h-8 user-avatar rounded-full flex items-center justify-center text-white text-sm font-semibold flex-shrink-0"
                 aria-label="Your message">
                {{ current_user.display_name[0] if current_user.display_name else current_user.username[0] }}
            </div>
        `;
    } else {
        messageDiv.innerHTML = `
            <div class="w-8 h-8 user-avatar rounded-full flex items-center justify-center text-white text-sm font-semibold flex-shrink-0"
                 aria-label="Message from contact">
                MR
            </div>
            <div class="flex-1 max-w-xs">
                <div class="message-received p-3 text-white">
                    <p class="text-sm break-words">${message}</p>
                </div>
                <div class="mt-1 text-xs text-gray-500 flex items-center space-x-2">
                    <time datetime="${timestampISO}" aria-label="Message received at ${timestamp}">${timestamp}</time>
                    ${metadata.originalText ? `
                        <span>•</span>
                        <span class="flex items-center">
                            <i class="ri-translate-2 mr-1" aria-hidden="true"></i>
                            <span aria-label="Original text">Original: "${metadata.originalText}"</span>
                        </span>
                    ` : ''}
                    <span class="translation-badge px-2 py-0.5 rounded-full text-white" 
                          aria-label="Translation method">
                            ${metadata.cached ? '⚡ Cached' : '🌐 Translated'}
                    </span>
                </div>
            </div>
        `;
    }
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Initialize chat core elements
const messagesContainer = document.getElementById('messagesContainer');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');

// Event listeners for chat core
sendButton.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Focus management
messageInput.focus();
</script>