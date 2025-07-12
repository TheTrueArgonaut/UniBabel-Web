// Rooms Core JavaScript - State Management & Initialization
class RoomsCore {
    constructor() {
        this.currentFilter = {
            category: '',
            age: 'all',
            search: ''
        };
        this.premiumFeatures = null;
        this.rooms = {
            my: [],
            trending: [],
            discoverable: [],
            pendingInvites: []
        };
        this.init();
    }

    init() {
        this.loadPremiumFeatures();
        this.setupEventListeners();
        this.loadAllRooms();
    }

    async loadPremiumFeatures() {
        try {
            const response = await fetch('/api/premium/features');
            const data = await response.json();
            
            if (response.ok) {
                this.premiumFeatures = data;
                this.updateUIBasedOnFeatures(data);
            }
        } catch (error) {
            console.error('Error loading premium features:', error);
        }
    }

    updateUIBasedOnFeatures(features) {
        // No restrictions - everyone gets all features
        this.updateCreateRoomButton(true, null);
    }

    updateCreateRoomButton(isPremium, roomLimits) {
        // No restrictions - everyone can create unlimited rooms
        const button = document.getElementById('createRoomBtn');
        if (button) {
            button.disabled = false;
            button.title = 'Create a new room';
        }
    }

    setupEventListeners() {
        document.addEventListener('DOMContentLoaded', () => {
            // Initialize all components
            this.loadAllRooms();
            
            // Setup global event listeners
            this.setupModalListeners();
            this.setupFilterListeners();
        });
    }

    setupModalListeners() {
        // Modal close on background click
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('fixed') && e.target.classList.contains('inset-0')) {
                this.closeAllModals();
            }
        });

        // ESC key to close modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });
    }

    setupFilterListeners() {
        const searchInput = document.getElementById('searchInput');
        const roomTypeFilter = document.getElementById('roomTypeFilter');

        if (searchInput) {
            searchInput.addEventListener('input', this.debounce((e) => {
                this.currentFilter.search = e.target.value;
                this.loadAllRooms();
            }, 300));
        }

        if (roomTypeFilter) {
            roomTypeFilter.addEventListener('change', (e) => {
                this.currentFilter.category = e.target.value;
                this.loadAllRooms();
            });
        }
    }

    async loadAllRooms() {
        await Promise.all([
            this.loadMyRooms(),
            this.loadTrendingRooms(),
            this.loadDiscoverableRooms(),
            this.loadPendingInvites()
        ]);
    }

    async loadMyRooms() {
        try {
            const params = new URLSearchParams(this.currentFilter);
            const response = await fetch(`/api/rooms?${params}`);
            const data = await response.json();
            
            if (data.rooms) {
                this.rooms.my = data.rooms;
                window.roomsDisplay.displayMyRooms(data.rooms);
            }
        } catch (error) {
            console.error('Error loading my rooms:', error);
        }
    }

    async loadTrendingRooms() {
        try {
            const response = await fetch('/api/rooms/trending');
            const data = await response.json();
            
            if (data.rooms && data.rooms.length > 0) {
                this.rooms.trending = data.rooms;
                window.roomsDisplay.displayTrendingRooms(data.rooms);
            } else {
                document.getElementById('trendingRoomsSection').style.display = 'none';
            }
        } catch (error) {
            console.error('Error loading trending rooms:', error);
            document.getElementById('trendingRoomsSection').style.display = 'none';
        }
    }

    async loadDiscoverableRooms() {
        try {
            const params = new URLSearchParams({
                search: this.currentFilter.search || '',
                category: this.currentFilter.category || ''
            });
            
            const response = await fetch(`/api/rooms/discoverable?${params}`);
            const data = await response.json();
            
            if (data.rooms && data.rooms.length > 0) {
                this.rooms.discoverable = data.rooms;
                window.roomsDisplay.displayDiscoverableRooms(data.rooms);
            } else {
                document.getElementById('discoverableRoomsSection').style.display = 'none';
            }
        } catch (error) {
            console.error('Error loading discoverable rooms:', error);
            document.getElementById('discoverableRoomsSection').style.display = 'none';
        }
    }

    async loadPendingInvites() {
        try {
            const response = await fetch('/api/rooms/pending-invites');
            const data = await response.json();
            
            if (data.success && data.invites && data.invites.length > 0) {
                this.rooms.pendingInvites = data.invites;
                window.roomsDisplay.displayPendingInvites(data.invites);
                document.getElementById('pendingInvitesSection').classList.remove('hidden');
                document.getElementById('inviteCount').textContent = data.invites.length;
            } else {
                document.getElementById('pendingInvitesSection').classList.add('hidden');
            }
        } catch (error) {
            console.error('Error loading pending invites:', error);
        }
    }

    closeAllModals() {
        const modals = document.querySelectorAll('.fixed.inset-0');
        modals.forEach(modal => {
            if (!modal.classList.contains('hidden')) {
                modal.classList.add('hidden');
            }
        });
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    refreshRooms() {
        this.loadAllRooms();
    }

    getRoomById(roomId) {
        const allRooms = [
            ...this.rooms.my,
            ...this.rooms.trending,
            ...this.rooms.discoverable
        ];
        return allRooms.find(room => room.id === roomId);
    }
}

// Initialize global instance
window.roomsCore = new RoomsCore();