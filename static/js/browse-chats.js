// Browse Chats - SRIMI Architecture
// Smart room discovery with Twitch-like interface and live previews

class BrowseChatsManager {
    constructor() {
        this.rooms = [];
        this.recommendedRooms = [];
        this.currentFilter = 'all';
        this.currentSort = 'activity';
        this.isListView = false;
        this.previewRoom = null;
        this.previewTimer = null;
        
        this.init();
    }

    init() {
        console.log('🔥 Initializing Browse Chats with Twitch-like discovery');
        this.setupEventListeners();
        this.loadRooms();
        this.loadRecommendations();
        this.startRealTimeUpdates();
    }

    setupEventListeners() {
        // Search functionality with debouncing
        const searchInput = document.getElementById('room-search');
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.filterRooms(e.target.value);
                }, 300);
            });
        }

        // Close modals on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closePreview();
                this.closeCreateRoom();
            }
        });

        // Close modals on backdrop click
        document.getElementById('live-preview-modal')?.addEventListener('click', (e) => {
            if (e.target === e.currentTarget) this.closePreview();
        });
        
        document.getElementById('create-room-modal')?.addEventListener('click', (e) => {
            if (e.target === e.currentTarget) this.closeCreateRoom();
        });
    }

    async loadRooms() {
        try {
            this.showLoading(true);
            
            // Mock data - replace with real API call
            const response = await this.fetchRoomsFromAPI();
            this.rooms = response.rooms || this.generateMockRooms();
            
            this.updateRoomCount();
            this.renderRooms();
            this.showLoading(false);
            
            console.log(`📊 Loaded ${this.rooms.length} chat rooms`);
        } catch (error) {
            console.error('Failed to load rooms:', error);
            this.showEmptyState();
        }
    }

    async fetchRoomsFromAPI() {
        // Replace with actual API endpoint
        try {
            const response = await fetch('/api/chat/rooms');
            return await response.json();
        } catch (error) {
            console.log('🔄 Using mock data for development');
            return { rooms: null };
        }
    }

    generateMockRooms() {
        const categories = ['gaming', 'tech', 'social', 'creative', 'general'];
        const gamingRooms = [
            { name: 'Valorant Squad Up', description: 'Looking for ranked teammates', category: 'gaming', trending: true },
            { name: 'Minecraft Builders', description: 'Creative building community', category: 'gaming' },
            { name: 'League Ranked Grind', description: 'Climbing the ladder together', category: 'gaming' },
            { name: 'Indie Game Devs', description: 'Unity & game development', category: 'gaming' }
        ];
        
        const techRooms = [
            { name: 'Python Study Group', description: 'Learning Python together', category: 'tech', trending: true },
            { name: 'Web Dev Bootcamp', description: 'Full-stack development', category: 'tech' },
            { name: 'AI & Machine Learning', description: 'Latest in AI research', category: 'tech' },
            { name: 'Startup Ideas Hub', description: 'Brainstorming the next big thing', category: 'tech' }
        ];
        
        const socialRooms = [
            { name: 'Coffee Chat ☕', description: 'Morning conversations', category: 'social', trending: true },
            { name: 'Study Buddies', description: 'Productive study sessions', category: 'social' },
            { name: 'Random Discussions', description: 'Talk about anything', category: 'social' },
            { name: 'Movie Night Planning', description: 'What to watch tonight?', category: 'social' }
        ];
        
        const allRooms = [...gamingRooms, ...techRooms, ...socialRooms];
        
        return allRooms.map((room, index) => ({
            id: index + 1,
            name: room.name,
            description: room.description,
            category: room.category,
            userCount: Math.floor(Math.random() * 150) + 5,
            activityLevel: Math.floor(Math.random() * 100) + 1,
            isOnline: Math.random() > 0.1,
            trending: room.trending || false,
            lastMessage: this.generateMockMessage(),
            messages: this.generateMockMessages(),
            createdAt: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000),
            tags: this.generateTags(room.category),
            rating: (Math.random() * 2 + 3).toFixed(1) // 3.0 - 5.0
        }));
    }

    generateTags(category) {
        const tagMap = {
            gaming: ['competitive', 'casual', 'team-based'],
            tech: ['programming', 'learning', 'career'],
            social: ['friendly', 'open', 'welcoming'],
            creative: ['art', 'music', 'design'],
            general: ['discussion', 'chat', 'community']
        };
        return tagMap[category] || ['general'];
    }

    generateMockMessage() {
        const messages = [
            'Hey everyone! 👋',
            'Anyone up for a quick game?',
            'Just finished an amazing project!',
            'What\'s everyone working on?',
            'Good morning chat! ☀️',
            'Looking for study partners',
            'This community is awesome!',
            'Anyone else excited about the new update?'
        ];
        return {
            text: messages[Math.floor(Math.random() * messages.length)],
            username: `User${Math.floor(Math.random() * 1000)}`,
            timestamp: new Date(Date.now() - Math.random() * 60000)
        };
    }

    generateMockMessages() {
        const count = Math.floor(Math.random() * 10) + 3;
        return Array.from({ length: count }, () => this.generateMockMessage());
    }

    async loadRecommendations() {
        try {
            // Smart AI recommendations based on user activity
            const userPreferences = this.getUserPreferences();
            this.recommendedRooms = this.generateSmartRecommendations(userPreferences);
            this.renderRecommendedRooms();
            
            console.log('🤖 Generated smart AI recommendations');
        } catch (error) {
            console.error('Failed to load recommendations:', error);
        }
    }

    getUserPreferences() {
        // In real app, this would analyze user's chat history, room joins, etc.
        return {
            favoriteCategories: ['gaming', 'tech'],
            activityTimes: ['evening'],
            preferredRoomSize: 'medium',
            interests: ['programming', 'games', 'learning']
        };
    }

    generateSmartRecommendations(preferences) {
        return this.rooms
            .filter(room => 
                preferences.favoriteCategories.includes(room.category) ||
                room.trending ||
                room.activityLevel > 70
            )
            .sort((a, b) => b.activityLevel - a.activityLevel)
            .slice(0, 4);
    }

    renderRecommendedRooms() {
        const container = document.getElementById('recommended-rooms');
        if (!container) return;

        container.innerHTML = this.recommendedRooms.map(room => this.createRoomCard(room, true)).join('');
    }

    renderRooms() {
        const container = document.getElementById('rooms-container');
        if (!container) return;

        let filteredRooms = this.getFilteredRooms();
        
        if (filteredRooms.length === 0) {
            this.showEmptyState();
            return;
        }

        this.hideEmptyState();
        container.className = this.isListView ? 
            'space-y-4' : 
            'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6';

        container.innerHTML = filteredRooms.map(room => 
            this.isListView ? this.createRoomListItem(room) : this.createRoomCard(room)
        ).join('');

        // Add hover event listeners for live preview
        this.setupRoomHoverEvents();
    }

    createRoomCard(room, isRecommended = false) {
        const categoryEmojis = {
            gaming: '🎮',
            tech: '💻',
            social: '👥',
            creative: '🎨',
            general: '💬'
        };

        const activityColor = room.activityLevel > 70 ? 'text-green-400' : 
                            room.activityLevel > 30 ? 'text-yellow-400' : 'text-gray-400';

        return `
            <div class="room-card rounded-xl p-6 cursor-pointer transform transition-all duration-300 hover:scale-105"
                 data-room-id="${room.id}"
                 onmouseenter="browseChats.startPreviewTimer(${room.id})"
                 onmouseleave="browseChats.cancelPreviewTimer()"
                 onclick="browseChats.joinRoom(${room.id})">
                
                <!-- Room Header -->
                <div class="flex items-start justify-between mb-4">
                    <div class="flex items-center gap-3">
                        <div class="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                            <span class="text-xl">${categoryEmojis[room.category]}</span>
                        </div>
                        <div class="flex-1">
                            <h3 class="font-semibold text-white text-lg mb-1 line-clamp-1">
                                ${room.name}
                            </h3>
                            <div class="flex items-center gap-2">
                                ${room.trending ? '<div class="trending-badge px-2 py-1 rounded-full text-xs font-bold text-white">🔥 TRENDING</div>' : ''}
                                <div class="category-tag px-2 py-1 rounded-full text-xs font-medium text-white">
                                    ${room.category.toUpperCase()}
                                </div>
                            </div>
                        </div>
                    </div>
                    ${isRecommended ? '<div class="text-yellow-400"><i class="ri-star-fill"></i></div>' : ''}
                </div>

                <!-- Room Description -->
                <p class="text-gray-300 text-sm mb-4 line-clamp-2">
                    ${room.description}
                </p>

                <!-- Room Stats -->
                <div class="flex items-center justify-between mb-4">
                    <div class="flex items-center gap-4">
                        <div class="flex items-center gap-1">
                            <i class="ri-user-line text-blue-400"></i>
                            <span class="text-sm text-gray-300">${room.userCount}</span>
                        </div>
                        <div class="flex items-center gap-1">
                            <i class="ri-pulse-line ${activityColor}"></i>
                            <span class="text-sm ${activityColor}">${room.activityLevel}%</span>
                        </div>
                        <div class="flex items-center gap-1">
                            <i class="ri-star-line text-yellow-400"></i>
                            <span class="text-sm text-gray-300">${room.rating}</span>
                        </div>
                    </div>
                    <div class="flex items-center gap-1">
                        <div class="w-2 h-2 rounded-full ${room.isOnline ? 'bg-green-400' : 'bg-gray-400'}"></div>
                        <span class="text-xs text-gray-400">${room.isOnline ? 'Active' : 'Quiet'}</span>
                    </div>
                </div>

                <!-- Tags -->
                <div class="flex flex-wrap gap-2 mb-4">
                    ${room.tags.slice(0, 3).map(tag => 
                        `<span class="px-2 py-1 bg-gray-700 text-gray-300 rounded text-xs">#${tag}</span>`
                    ).join('')}
                </div>

                <!-- Last Message Preview -->
                <div class="bg-gray-900/50 rounded-lg p-3">
                    <div class="flex items-center gap-2 mb-1">
                        <div class="w-4 h-4 rounded-full bg-gray-600"></div>
                        <span class="text-xs text-gray-400">${room.lastMessage.username}</span>
                        <span class="text-xs text-gray-500">${this.formatTime(room.lastMessage.timestamp)}</span>
                    </div>
                    <p class="text-sm text-gray-300 line-clamp-1">${room.lastMessage.text}</p>
                </div>

                <!-- Hover Actions -->
                <div class="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button class="bg-blue-600 hover:bg-blue-700 text-white p-2 rounded-lg text-sm" 
                            onclick="event.stopPropagation(); browseChats.showLivePreview(${room.id})">
                        <i class="ri-eye-line"></i>
                    </button>
                </div>
            </div>
        `;
    }

    createRoomListItem(room) {
        return `
            <div class="room-card rounded-xl p-4 cursor-pointer"
                 data-room-id="${room.id}"
                 onclick="browseChats.joinRoom(${room.id})">
                <div class="flex items-center gap-4">
                    <div class="w-16 h-16 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-2xl">
                        ${this.getCategoryEmoji(room.category)}
                    </div>
                    <div class="flex-1">
                        <div class="flex items-center gap-2 mb-1">
                            <h3 class="font-semibold text-white text-lg">${room.name}</h3>
                            ${room.trending ? '<span class="trending-badge px-2 py-1 rounded text-xs">🔥</span>' : ''}
                        </div>
                        <p class="text-gray-300 text-sm mb-2">${room.description}</p>
                        <div class="flex items-center gap-4 text-sm text-gray-400">
                            <span><i class="ri-user-line mr-1"></i>${room.userCount} users</span>
                            <span><i class="ri-pulse-line mr-1"></i>${room.activityLevel}% active</span>
                            <span class="category-tag px-2 py-1 rounded text-xs">${room.category}</span>
                        </div>
                    </div>
                    <button class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">
                        Join
                    </button>
                </div>
            </div>
        `;
    }

    getCategoryEmoji(category) {
        const emojis = { gaming: '🎮', tech: '💻', social: '👥', creative: '🎨', general: '💬' };
        return emojis[category] || '💬';
    }

    setupRoomHoverEvents() {
        const roomCards = document.querySelectorAll('.room-card');
        roomCards.forEach(card => {
            const roomId = parseInt(card.dataset.roomId);
            
            card.addEventListener('mouseenter', () => {
                this.startPreviewTimer(roomId);
            });
            
            card.addEventListener('mouseleave', () => {
                this.cancelPreviewTimer();
            });
        });
    }

    startPreviewTimer(roomId) {
        this.cancelPreviewTimer();
        this.previewTimer = setTimeout(() => {
            this.showLivePreview(roomId);
        }, 1000); // Show preview after 1 second hover
    }

    cancelPreviewTimer() {
        if (this.previewTimer) {
            clearTimeout(this.previewTimer);
            this.previewTimer = null;
        }
    }

    showLivePreview(roomId) {
        const room = this.rooms.find(r => r.id === roomId);
        if (!room) return;

        this.previewRoom = room;
        
        // Update preview modal content
        document.getElementById('preview-room-name').textContent = room.name;
        document.getElementById('preview-room-users').textContent = `${room.userCount} users`;
        
        // Render live messages
        this.renderPreviewMessages(room.messages);
        
        // Show modal
        document.getElementById('live-preview-modal').style.display = 'block';
        
        // Start live message simulation
        this.startLiveMessageSimulation();
        
        console.log(`👁️ Showing live preview for: ${room.name}`);
    }

    renderPreviewMessages(messages) {
        const container = document.getElementById('preview-messages');
        if (!container) return;

        container.innerHTML = messages.map(msg => `
            <div class="mb-3">
                <div class="flex items-center gap-2 mb-1">
                    <div class="w-6 h-6 rounded-full bg-gray-600 flex items-center justify-center">
                        <i class="ri-user-line text-xs text-gray-300"></i>
                    </div>
                    <span class="text-sm font-medium text-gray-300">${msg.username}</span>
                    <span class="text-xs text-gray-500">${this.formatTime(msg.timestamp)}</span>
                </div>
                <p class="text-gray-200 ml-8">${msg.text}</p>
            </div>
        `).join('');

        container.scrollTop = container.scrollHeight;
    }

    startLiveMessageSimulation() {
        if (this.liveMessageInterval) {
            clearInterval(this.liveMessageInterval);
        }

        this.liveMessageInterval = setInterval(() => {
            if (this.previewRoom) {
                const newMessage = this.generateMockMessage();
                this.previewRoom.messages.push(newMessage);
                this.renderPreviewMessages(this.previewRoom.messages);
            }
        }, 3000 + Math.random() * 7000); // Random interval 3-10 seconds
    }

    closePreview() {
        document.getElementById('live-preview-modal').style.display = 'none';
        
        if (this.liveMessageInterval) {
            clearInterval(this.liveMessageInterval);
            this.liveMessageInterval = null;
        }
        
        this.previewRoom = null;
        this.cancelPreviewTimer();
    }

    joinRoom(roomId) {
        const room = this.rooms.find(r => r.id === roomId);
        if (!room) return;

        console.log(`🚀 Joining room: ${room.name}`);
        
        // Close any open previews
        this.closePreview();
        
        // Implement seamless transition to chat
        this.showJoinAnimation(room);
        
        // In real app: navigate to chat room
        setTimeout(() => {
            window.location.href = `/chat/room/${roomId}`;
        }, 1000);
    }

    joinRoomFromPreview() {
        if (this.previewRoom) {
            this.joinRoom(this.previewRoom.id);
        }
    }

    showJoinAnimation(room) {
        const notification = document.createElement('div');
        notification.className = 'fixed top-4 right-4 bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg z-50 transform translate-x-full transition-transform duration-300';
        notification.innerHTML = `
            <div class="flex items-center gap-3">
                <i class="ri-chat-3-line text-xl"></i>
                <div>
                    <p class="font-semibold">Joining ${room.name}</p>
                    <p class="text-sm opacity-90">Connecting...</p>
                </div>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.remove('translate-x-full');
        }, 100);
        
        setTimeout(() => {
            notification.classList.add('translate-x-full');
            setTimeout(() => notification.remove(), 300);
        }, 2000);
    }

    // Filter and Sort Functions
    filterByCategory(category) {
        this.currentFilter = category;
        
        // Update active filter button
        document.querySelectorAll('.category-filter').forEach(btn => {
            btn.classList.remove('active', 'bg-blue-600', 'text-white');
            btn.classList.add('bg-gray-700', 'text-gray-300');
        });
        
        const activeBtn = document.getElementById(`filter-${category}`);
        if (activeBtn) {
            activeBtn.classList.add('active', 'bg-blue-600', 'text-white');
            activeBtn.classList.remove('bg-gray-700', 'text-gray-300');
        }
        
        this.renderRooms();
        console.log(`🔍 Filtered by category: ${category}`);
    }

    sortRooms(sortBy) {
        this.currentSort = sortBy;
        this.renderRooms();
        console.log(`📊 Sorted by: ${sortBy}`);
    }

    filterRooms(searchTerm) {
        this.searchTerm = searchTerm.toLowerCase();
        this.renderRooms();
        console.log(`🔍 Searching for: ${searchTerm}`);
    }

    getFilteredRooms() {
        let filtered = this.rooms.filter(room => {
            const matchesCategory = this.currentFilter === 'all' || 
                                  this.currentFilter === 'trending' && room.trending ||
                                  room.category === this.currentFilter;
            
            const matchesSearch = !this.searchTerm || 
                                room.name.toLowerCase().includes(this.searchTerm) ||
                                room.description.toLowerCase().includes(this.searchTerm) ||
                                room.tags.some(tag => tag.toLowerCase().includes(this.searchTerm));
            
            return matchesCategory && matchesSearch;
        });

        // Sort filtered rooms
        filtered.sort((a, b) => {
            switch (this.currentSort) {
                case 'activity':
                    return b.activityLevel - a.activityLevel;
                case 'users':
                    return b.userCount - a.userCount;
                case 'newest':
                    return new Date(b.createdAt) - new Date(a.createdAt);
                case 'alphabetical':
                    return a.name.localeCompare(b.name);
                default:
                    return 0;
            }
        });

        return filtered;
    }

    // View Controls
    toggleView(viewType) {
        this.isListView = viewType === 'list';
        
        // Update view toggle buttons
        document.querySelectorAll('.view-toggle').forEach(btn => {
            btn.classList.remove('active', 'bg-gray-700', 'text-white');
            btn.classList.add('bg-gray-800', 'text-gray-400');
        });
        
        const activeBtn = document.getElementById(`${viewType}-view`);
        if (activeBtn) {
            activeBtn.classList.add('active', 'bg-gray-700', 'text-white');
            activeBtn.classList.remove('bg-gray-800', 'text-gray-400');
        }
        
        this.renderRooms();
        console.log(`👁️ Switched to ${viewType} view`);
    }

    clearFilters() {
        this.currentFilter = 'all';
        this.searchTerm = '';
        document.getElementById('room-search').value = '';
        document.getElementById('sort-rooms').value = 'activity';
        this.filterByCategory('all');
    }

    // Room Creation
    showCreateRoom() {
        document.getElementById('create-room-modal').style.display = 'block';
    }

    closeCreateRoom() {
        document.getElementById('create-room-modal').style.display = 'none';
        document.getElementById('new-room-name').value = '';
        document.getElementById('new-room-description').value = '';
        document.getElementById('new-room-category').value = 'social';
    }

    async createRoom(event) {
        event.preventDefault();
        
        const name = document.getElementById('new-room-name').value.trim();
        const description = document.getElementById('new-room-description').value.trim();
        const category = document.getElementById('new-room-category').value;
        
        if (!name) return;
        
        try {
            // In real app: API call to create room
            const newRoom = {
                id: Date.now(),
                name,
                description: description || 'No description provided',
                category,
                userCount: 1,
                activityLevel: 0,
                isOnline: true,
                trending: false,
                lastMessage: { text: 'Room created!', username: 'System', timestamp: new Date() },
                messages: [],
                createdAt: new Date(),
                tags: this.generateTags(category),
                rating: '5.0'
            };
            
            this.rooms.unshift(newRoom);
            this.renderRooms();
            this.closeCreateRoom();
            
            // Show success notification
            this.showNotification(`Room "${name}" created successfully!`, 'success');
            
            // Auto-join the new room
            setTimeout(() => this.joinRoom(newRoom.id), 1000);
            
        } catch (error) {
            console.error('Failed to create room:', error);
            this.showNotification('Failed to create room. Please try again.', 'error');
        }
    }

    // Utility Functions
    updateRoomCount() {
        const countElement = document.getElementById('room-count');
        if (countElement) {
            countElement.textContent = `${this.rooms.length} rooms`;
        }
    }

    formatTime(timestamp) {
        const now = new Date();
        const diff = now - new Date(timestamp);
        const minutes = Math.floor(diff / 60000);
        
        if (minutes < 1) return 'now';
        if (minutes < 60) return `${minutes}m`;
        if (minutes < 1440) return `${Math.floor(minutes / 60)}h`;
        return `${Math.floor(minutes / 1440)}d`;
    }

    showLoading(show) {
        const loading = document.getElementById('loading-state');
        if (loading) {
            loading.style.display = show ? 'block' : 'none';
        }
    }

    showEmptyState() {
        document.getElementById('empty-state').style.display = 'block';
        document.getElementById('rooms-container').style.display = 'none';
    }

    hideEmptyState() {
        document.getElementById('empty-state').style.display = 'none';
        document.getElementById('rooms-container').style.display = 'block';
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        const colors = {
            success: 'bg-green-600',
            error: 'bg-red-600',
            info: 'bg-blue-600'
        };
        
        notification.className = `fixed top-4 right-4 ${colors[type]} text-white px-6 py-3 rounded-lg shadow-lg z-50 transform translate-x-full transition-transform duration-300`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => notification.classList.remove('translate-x-full'), 100);
        setTimeout(() => {
            notification.classList.add('translate-x-full');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    startRealTimeUpdates() {
        // Update room activity and user counts periodically
        setInterval(() => {
            this.rooms.forEach(room => {
                // Simulate activity changes
                room.activityLevel = Math.max(0, room.activityLevel + (Math.random() - 0.5) * 10);
                room.userCount = Math.max(1, room.userCount + Math.floor((Math.random() - 0.5) * 3));
                
                // Occasionally add new messages
                if (Math.random() < 0.1) {
                    room.lastMessage = this.generateMockMessage();
                    room.messages.push(room.lastMessage);
                }
            });
            
            // Re-render if needed
            if (this.currentSort === 'activity' || this.currentSort === 'users') {
                this.renderRooms();
            }
        }, 30000); // Update every 30 seconds
    }
}

// Global functions for event handlers
let browseChats;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    browseChats = new BrowseChatsManager();
});

// Global functions called from HTML
function filterByCategory(category) {
    browseChats?.filterByCategory(category);
}

function sortRooms(sortBy) {
    browseChats?.sortRooms(sortBy);
}

function toggleView(viewType) {
    browseChats?.toggleView(viewType);
}

function clearFilters() {
    browseChats?.clearFilters();
}

function showCreateRoom() {
    browseChats?.showCreateRoom();
}

function closeCreateRoom() {
    browseChats?.closeCreateRoom();
}

function createRoom(event) {
    browseChats?.createRoom(event);
}

function closePreview() {
    browseChats?.closePreview();
}

function joinRoomFromPreview() {
    browseChats?.joinRoomFromPreview();
}

// Browse Chats JavaScript - Twitch + Discord trending rooms discovery

// 1. MAIN TRIGGER FUNCTION
function openBrowseChats() {
    console.log('🔥 Opening Browse Chats...');
    
    // Prevent duplicate modal
    if (document.getElementById('browse-chats-modal')) return;

    // Create modal
    const modal = document.createElement('div');
    modal.id = 'browse-chats-modal';
    modal.className = 'fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50';
    modal.innerHTML = createBrowseChatsModalHTML();
    
    document.body.appendChild(modal);
    
    // Load trending rooms data
    loadTrendingRooms();
    
    // Setup event listeners
    setupBrowseChatsListeners(modal);
}

// 2. HTML GENERATION FUNCTION
function createBrowseChatsModalHTML() {
    return `
        <div class="bg-gray-800 rounded-xl max-w-7xl w-full mx-4 h-[700px] flex flex-col">
            <!-- Header -->
            <div class="flex items-center justify-between p-4 border-b border-gray-700">
                <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center border border-blue-500/50">
                        <i class="ri-fire-line text-xl text-orange-400"></i>
                    </div>
                    <div>
                        <h3 class="text-xl font-bold text-white">🔥 Browse Trending Rooms</h3>
                        <p class="text-sm text-gray-400">Discover popular chat communities with live activity</p>
                    </div>
                </div>
                <div class="flex items-center gap-2">
                    <button onclick="popOutBrowseChats()" 
                            class="text-gray-400 hover:text-white transition-colors bg-gray-700 hover:bg-gray-600 px-3 py-1 rounded-lg text-sm"
                            title="Pop out to new window">
                        <i class="ri-external-link-line"></i> Pop Out
                    </button>
                    <button onclick="closeBrowseChats()" class="text-gray-400 hover:text-white">
                        <i class="ri-close-line text-xl"></i>
                    </button>
                </div>
            </div>
            
            <!-- Category Filters -->
            <div class="p-4 border-b border-gray-700 bg-gray-900/30">
                <div class="flex flex-wrap gap-2" id="browseFilters">
                    <button class="filter-btn active" data-filter="all">🔥 All Trending</button>
                    <button class="filter-btn" data-filter="gaming">🎮 Gaming</button>
                    <button class="filter-btn" data-filter="language">🌍 Language</button>
                    <button class="filter-btn" data-filter="music">🎵 Music</button>
                    <button class="filter-btn" data-filter="tech">💻 Tech</button>
                    <button class="filter-btn" data-filter="art">🎨 Art</button>
                    <button class="filter-btn" data-filter="fitness">💪 Fitness</button>
                </div>
            </div>
            
            <!-- Main Content Area -->
            <div class="flex-1 overflow-y-auto p-4 bg-gray-900/20">
                <!-- Loading State -->
                <div id="browseLoading" class="text-center py-12">
                    <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-orange-400"></div>
                    <p class="text-gray-400 mt-2">Loading trending rooms...</p>
                </div>
                
                <!-- Trending Rooms Grid -->
                <div id="browseRoomsGrid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 hidden">
                    <!-- Room cards will be populated here -->
                </div>
                
                <!-- Empty State -->
                <div id="browseEmpty" class="text-center py-12 hidden">
                    <div class="w-16 h-16 rounded-full bg-orange-400/10 flex items-center justify-center mx-auto mb-4">
                        <i class="ri-fire-line text-2xl text-orange-400"></i>
                    </div>
                    <h3 class="text-lg font-bold text-white mb-2">No trending rooms</h3>
                    <p class="text-gray-400 mb-4">Try a different category or create your own room!</p>
                    <button class="bg-primary text-white px-6 py-2 rounded-lg hover:bg-red-700 transition-colors">
                        Create New Room
                    </button>
                </div>
            </div>
        </div>
    `;
}

// 3. DATA LOADING FUNCTION
async function loadTrendingRooms(category = 'all') {
    showBrowseState('loading');
    
    try {
        // Simulate API call - replace with real endpoint
        const response = await fetch(`/api/rooms/trending?category=${category}`);
        const data = await response.json();
        
        if (data.success && data.rooms.length > 0) {
            displayTrendingRooms(data.rooms);
            showBrowseState('grid');
        } else {
            showBrowseState('empty');
        }
    } catch (error) {
        console.error('Error loading trending rooms:', error);
        // Use mock data for demo
        const mockRooms = generateMockTrendingRooms(category);
        displayTrendingRooms(mockRooms);
        showBrowseState('grid');
    }
}

// 4. MOCK DATA GENERATOR
function generateMockTrendingRooms(category) {
    const allRooms = [
        { id: 1, name: 'Epic Gaming Hub', category: 'gaming', participants: 2847, activity: 'Very Active', topic: 'Latest game releases & tips', official: true, preview_img: '🎮', tags: ['PC', 'Console', 'Mobile'] },
        { id: 2, name: 'Global Language Exchange', category: 'language', participants: 1923, activity: 'Active', topic: 'Practice languages with natives', official: true, preview_img: '🌍', tags: ['Spanish', 'French', 'Japanese'] },
        { id: 3, name: 'Music Discovery Lounge', category: 'music', participants: 1456, activity: 'Active', topic: 'Share and discover new music', official: false, preview_img: '🎵', tags: ['Indie', 'Rock', 'Electronic'] },
        { id: 4, name: 'Code & Coffee', category: 'tech', participants: 987, activity: 'Moderate', topic: 'Programming discussions & help', official: false, preview_img: '💻', tags: ['JavaScript', 'Python', 'React'] },
        { id: 5, name: 'Digital Art Studio', category: 'art', participants: 734, activity: 'Moderate', topic: 'Share artwork & get feedback', official: false, preview_img: '🎨', tags: ['Digital', 'Traditional', 'AI Art'] },
        { id: 6, name: 'Fitness Motivation', category: 'fitness', participants: 612, activity: 'Active', topic: 'Workout routines & motivation', official: false, preview_img: '💪', tags: ['Cardio', 'Strength', 'Yoga'] }
    ];
    
    return category === 'all' ? allRooms : allRooms.filter(room => room.category === category);
}

// 5. DISPLAY FUNCTION
function displayTrendingRooms(rooms) {
    const grid = document.getElementById('browseRoomsGrid');
    grid.innerHTML = '';
    
    rooms.forEach(room => {
        const roomCard = document.createElement('div');
        roomCard.className = 'trending-room-card bg-gray-800/80 rounded-xl p-4 border border-gray-700 hover:border-orange-400/50 transition-all duration-300 hover:scale-105 cursor-pointer';
        roomCard.innerHTML = `
            <div class="relative mb-3">
                <div class="w-full h-32 bg-gradient-to-br from-${getColorByCategory(room.category)}-500/20 to-${getColorByCategory(room.category)}-600/20 rounded-lg flex items-center justify-center text-4xl">
                    ${room.preview_img}
                </div>
                ${room.official ? '<div class="absolute top-2 right-2 bg-blue-500 text-white px-2 py-1 rounded-full text-xs font-bold">OFFICIAL</div>' : ''}
                <div class="absolute bottom-2 left-2 bg-black/70 text-white px-2 py-1 rounded-full text-xs flex items-center gap-1">
                    <div class="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                    ${room.activity}
                </div>
            </div>
            
            <h4 class="font-bold text-white text-lg mb-2 truncate">${room.name}</h4>
            <p class="text-gray-300 text-sm mb-3 line-clamp-2">${room.topic}</p>
            
            <div class="flex flex-wrap gap-1 mb-3">
                ${room.tags.map(tag => `<span class="bg-${getColorByCategory(room.category)}-500/20 text-${getColorByCategory(room.category)}-400 px-2 py-1 rounded-full text-xs">${tag}</span>`).join('')}
            </div>
            
            <div class="flex items-center justify-between">
                <div class="flex items-center gap-2 text-sm text-gray-400">
                    <i class="ri-user-line"></i>
                    <span>${room.participants.toLocaleString()}</span>
                    <span class="text-gray-500">•</span>
                    <span class="capitalize">${room.category}</span>
                </div>
                <button onclick="joinTrendingRoom(${room.id})" 
                        class="bg-orange-500 hover:bg-orange-600 text-white px-3 py-1 rounded-lg text-sm font-medium transition-colors">
                    Join
                </button>
            </div>
        `;
        
        // Add hover preview functionality
        roomCard.addEventListener('mouseenter', () => showRoomPreview(room));
        roomCard.addEventListener('mouseleave', hideRoomPreview);
        
        grid.appendChild(roomCard);
    });
}

// 6. UTILITY FUNCTIONS
function getColorByCategory(category) {
    const colors = {
        gaming: 'green',
        language: 'blue', 
        music: 'purple',
        tech: 'yellow',
        art: 'pink',
        fitness: 'red'
    };
    return colors[category] || 'gray';
}

function showBrowseState(state) {
    const loading = document.getElementById('browseLoading');
    const grid = document.getElementById('browseRoomsGrid');
    const empty = document.getElementById('browseEmpty');
    
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
            grid.style.display = 'grid';
            break;
        case 'empty':
            empty.style.display = 'block';
            break;
    }
}

// 7. EVENT HANDLERS
function setupBrowseChatsListeners(modal) {
    // Category filter buttons
    const filterButtons = modal.querySelectorAll('.filter-btn');
    filterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            // Update active state
            filterButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Load rooms for category
            const category = btn.dataset.filter;
            loadTrendingRooms(category);
        });
    });
    
    // Keyboard accessibility
    modal.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeBrowseChats();
        }
    });
}

// 8. ROOM ACTIONS
function joinTrendingRoom(roomId) {
    window.open(`/chat?room=${roomId}`, '_blank');
    closeBrowseChats();
}

function showRoomPreview(room) {
    // Could implement live chat preview here
    console.log('Previewing room:', room.name);
}

function hideRoomPreview() {
    // Hide any preview overlays
}

// 9. POP OUT FUNCTION
function popOutBrowseChats() {
    const popupWindow = window.open('', 'UniBabelBrowseChats', 'width=1400,height=900,scrollbars=yes,resizable=yes');
    if (popupWindow) {
        const html = `<!DOCTYPE html><html><head><title>UniBabel - Browse Trending Rooms</title><script src="https://cdn.tailwindcss.com"></script><link href="https://cdnjs.cloudflare.com/ajax/libs/remixicon/4.6.0/remixicon.min.css" rel="stylesheet"></head><body class="bg-gray-900 text-white"><div class="p-6"><h1 class="text-2xl font-bold mb-4">🔥 Browse Trending Rooms</h1><p>This is your dedicated trending rooms window!</p><p class="text-gray-400 mt-2">Full functionality with live data coming soon...</p></div></body></html>`;
        popupWindow.document.write(html);
        popupWindow.document.close();
    }
}

// 10. CLOSE FUNCTION
function closeBrowseChats() {
    const modal = document.getElementById('browse-chats-modal');
    if (modal) modal.remove();
}

// 11. GLOBAL EVENT LISTENERS
document.addEventListener('keydown', function(e) {
    const modal = document.getElementById('browse-chats-modal');
    if (modal && e.key === 'Escape') closeBrowseChats();
});

window.addEventListener('click', function(e) {
    const modal = document.getElementById('browse-chats-modal');
    if (modal && e.target === modal) closeBrowseChats();
});