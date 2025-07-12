<script>
// 🎯 SOCKET MANAGER MICROSERVICE - Single Responsibility: Real-time communication
// Handles: Socket.IO connection, message events, typing indicators

// Socket.IO connection
const socket = io();
const typingIndicator = document.getElementById('typingIndicator');

let currentChatId = 1; // This would come from the backend
let typingTimer;

// Join the current chat
socket.emit('join_chat', { chat_id: currentChatId });

// Socket event listeners with accessibility
socket.on('new_message', (data) => {
    if (data.sender_id !== {{ current_user.id }}) {
        addMessageToUI(data.text, false, {
            originalText: data.original_text,
            cached: data.was_cached
        });
        
        // Announce new message for accessibility
        announceToScreenReader(`New message received: ${data.text.substring(0, 50)}${data.text.length > 50 ? '...' : ''}`);
    }
});

socket.on('user_typing', (data) => {
    if (data.user_id !== {{ current_user.id }}) {
        const isTyping = data.is_typing;
        typingIndicator.style.display = isTyping ? 'flex' : 'none';
        
        // Announce typing status for accessibility
        if (isTyping) {
            announceToScreenReader('User is typing');
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        } else {
            announceToScreenReader('User stopped typing');
        }
    }
});

// Typing indicators
messageInput.addEventListener('input', () => {
    socket.emit('typing', { chat_id: currentChatId, is_typing: true });
    
    clearTimeout(typingTimer);
    typingTimer = setTimeout(() => {
        socket.emit('typing', { chat_id: currentChatId, is_typing: false });
    }, 1000);
});
</script>