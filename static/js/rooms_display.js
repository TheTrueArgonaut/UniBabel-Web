// Rooms Display JavaScript - Room Card Rendering & Content Display
class RoomsDisplay {
    constructor() {
        this.containers = {
            myRooms: document.getElementById('my-rooms'),
            trendingRooms: document.getElementById('trending-rooms'),
            discoverableRooms: document.getElementById('discoverable-rooms'),
            pendingInvites: document.getElementById('pending-invites')
        };
    }

    displayMyRooms(rooms) {
        if (!this.containers.myRooms) return;

        if (rooms.length === 0) {
            this.containers.myRooms.innerHTML = this.createEmptyState();
            return;
        }

        this.containers.myRooms.innerHTML = rooms.map(room => 
            this.createRoomCard(room, 'my-rooms')
        ).join('');

        // Update room count
        const roomCount = document.getElementById('roomCount');
        if (roomCount) {
            roomCount.textContent = rooms.length;
        }
    }

    displayTrendingRooms(rooms) {
        if (!this.containers.trendingRooms) return;
        
        this.containers.trendingRooms.innerHTML = rooms.map(room => 
            this.createRoomCard(room, 'trending')
        ).join('');
    }

    displayDiscoverableRooms(rooms) {
        if (!this.containers.discoverableRooms) return;
        
        this.containers.discoverableRooms.innerHTML = rooms.map(room => 
            this.createRoomCard(room, 'discoverable')
        ).join('');
    }

    displayPendingInvites(invites) {
        if (!this.containers.pendingInvites) return;
        
        this.containers.pendingInvites.innerHTML = invites.map(invite => 
            this.createInviteCard(invite)
        ).join('');
    }

    createEmptyState() {
        return `
            <div class="col-span-full text-center py-8">
                <div class="w-16 h-16 bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4">
                    <i class="ri-search-line text-2xl text-gray-400"></i>
                </div>
                <h3 class="text-lg font-semibold text-white mb-2">No rooms found</h3>
                <p class="text-gray-400">Try adjusting your search criteria or create a new room!</p>
            </div>
        `;
    }

    createRoomCard(room, type) {
        const actionButton = this.createActionButton(room, type);
        const badges = this.createBadges(room, type);
        const roomIcon = room.voice_enabled ? '🎙️' : '💬';

        return `
            <div class="room-card p-6 rounded-xl border border-gray-700" data-room-id="${room.id}">
                <div class="flex items-start justify-between mb-4">
                    <div class="flex items-center space-x-3">
                        <div class="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center text-2xl">
                            ${roomIcon}
                        </div>
                        <div>
                            <h3 class="font-semibold text-white">${this.escapeHtml(room.name)}</h3>
                            <p class="text-sm text-gray-400">${this.escapeHtml(room.description || 'General • All Ages')}</p>
                        </div>
                    </div>
                    <div class="online-count px-2 py-1 rounded-full text-xs text-white font-semibold">
                        ${room.participant_count || 0} ${type === 'trending' || type === 'discoverable' ? 'members' : 'online'}
                    </div>
                </div>
                
                <p class="text-gray-300 text-sm mb-4">
                    ${this.escapeHtml(room.description || 'Join the conversation!')}
                </p>
                
                <div class="flex flex-wrap gap-2 mb-4">
                    ${badges}
                </div>
                
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-2 text-sm text-gray-400">
                        <i class="ri-user-line"></i>
                        <span>${room.participant_count || 0} members</span>
                        ${room.owner_name ? `<span class="ml-2">by ${this.escapeHtml(room.owner_name)}</span>` : ''}
                    </div>
                    ${actionButton}
                </div>
            </div>
        `;
    }

    createInviteCard(invite) {
        return `
            <div class="bg-yellow-900 bg-opacity-30 border border-yellow-500 p-4 rounded-lg flex items-center justify-between">
                <div class="flex items-center space-x-3">
                    <div class="w-10 h-10 bg-yellow-500 rounded-lg flex items-center justify-center">
                        🎮
                    </div>
                    <div>
                        <h3 class="font-semibold text-white">${this.escapeHtml(invite.room_name)}</h3>
                        <p class="text-sm text-yellow-200">Invited by ${this.escapeHtml(invite.invited_by)} • ${invite.member_count} members</p>
                    </div>
                </div>
                <div class="flex space-x-2">
                    <button onclick="window.roomsApi.acceptInvite(${invite.room_id})" 
                            class="bg-green-600 hover:bg-green-700 px-3 py-1 rounded text-sm transition-colors">
                        Accept
                    </button>
                    <button onclick="window.roomsApi.declineInvite(${invite.room_id})" 
                            class="bg-red-600 hover:bg-red-700 px-3 py-1 rounded text-sm transition-colors">
                        Decline
                    </button>
                </div>
            </div>
        `;
    }

    createActionButton(room, type) {
        if (type === 'trending' || type === 'discoverable') {
            return `
                <button onclick="window.roomsApi.joinDiscoverableRoom(${room.id})" 
                        class="bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg text-sm font-semibold transition-colors">
                    Join Room
                </button>
            `;
        }

        const settingsButton = room.is_owner ? `
            <button onclick="window.roomsSettings.openRoomSettings(${room.id})" 
                    class="bg-gray-600 hover:bg-gray-500 px-4 py-2 rounded-lg text-sm transition-colors" 
                    title="Room Settings">
                <i class="ri-settings-3-line"></i>
            </button>
        ` : '';

        return `
            <div class="flex space-x-2">
                <button onclick="window.roomsApi.joinRoom(${room.id})" 
                        class="bg-primary hover:bg-red-700 px-4 py-2 rounded-lg text-sm font-semibold transition-colors">
                    Join Room
                </button>
                ${settingsButton}
            </div>
        `;
    }

    createBadges(room, type) {
        const badges = [];

        // Type badge
        if (type === 'trending') {
            badges.push(`<span class="bg-orange-500 px-2 py-1 rounded-full text-xs text-white">🔥 Trending</span>`);
        } else if (type === 'discoverable') {
            badges.push(`<span class="bg-blue-500 px-2 py-1 rounded-full text-xs text-white">🌐 Public</span>`);
        } else {
            badges.push(`<span class="bg-gray-600 px-2 py-1 rounded-full text-xs text-white">Private</span>`);
        }

        // Voice badge
        if (room.voice_enabled) {
            badges.push(`<span class="bg-purple-600 px-2 py-1 rounded-full text-xs text-white">🎙️ Voice</span>`);
        }

        // Age badge
        badges.push(`<span class="age-badge-teen px-2 py-1 rounded-full text-xs text-white">All Ages</span>`);

        // Language badge
        badges.push(`<span class="bg-gray-600 px-2 py-1 rounded-full text-xs text-gray-200">Auto-Translate</span>`);
        badges.push(`<span class="language-badge px-2 py-1 rounded-full text-xs text-white">Global</span>`);

        // Activity badge for trending rooms
        if (type === 'trending' && room.activity_score) {
            badges.push(`<span class="bg-yellow-600 px-2 py-1 rounded-full text-xs text-white">Activity: ${room.activity_score}</span>`);
        }

        return badges.join('');
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    updateRoomCard(roomId, updates) {
        const card = document.querySelector(`[data-room-id="${roomId}"]`);
        if (!card) return;

        // Update specific elements in the card
        if (updates.name) {
            const nameElement = card.querySelector('h3');
            if (nameElement) {
                nameElement.textContent = updates.name;
            }
        }

        if (updates.description) {
            const descElement = card.querySelector('.text-gray-300');
            if (descElement) {
                descElement.textContent = updates.description;
            }
        }

        if (updates.participant_count !== undefined) {
            const countElement = card.querySelector('.online-count');
            if (countElement) {
                countElement.textContent = `${updates.participant_count} online`;
            }
        }
    }

    removeRoomCard(roomId) {
        const card = document.querySelector(`[data-room-id="${roomId}"]`);
        if (card) {
            card.remove();
        }
    }

    showLoadingState(containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `
                <div class="col-span-full text-center py-8">
                    <div class="w-16 h-16 bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4 animate-spin">
                        <i class="ri-loader-4-line text-2xl text-gray-400"></i>
                    </div>
                    <p class="text-gray-400">Loading rooms...</p>
                </div>
            `;
        }
    }

    showErrorState(containerId, message) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `
                <div class="col-span-full text-center py-8">
                    <div class="w-16 h-16 bg-red-900 rounded-full flex items-center justify-center mx-auto mb-4">
                        <i class="ri-error-warning-line text-2xl text-red-400"></i>
                    </div>
                    <h3 class="text-lg font-semibold text-white mb-2">Error Loading Rooms</h3>
                    <p class="text-gray-400">${message}</p>
                </div>
            `;
        }
    }
}

// Initialize global instance
window.roomsDisplay = new RoomsDisplay();