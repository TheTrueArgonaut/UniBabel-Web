// Rooms Filters JavaScript - Filter & Search Functionality
class RoomsFilters {
    constructor() {
        this.filters = {
            search: '',
            type: 'all',
            voice: false,
            discoverable: false
        };
        this.debounceTimer = null;
        this.setupEventListeners();
    }

    setupEventListeners() {
        document.addEventListener('DOMContentLoaded', () => {
            this.initializeFilters();
        });
    }

    initializeFilters() {
        const searchInput = document.getElementById('searchInput');
        const roomTypeFilter = document.getElementById('roomTypeFilter');

        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.handleSearchInput(e.target.value);
            });
        }

        if (roomTypeFilter) {
            roomTypeFilter.addEventListener('change', (e) => {
                this.handleTypeFilter(e.target.value);
            });
        }
    }

    handleSearchInput(value) {
        this.filters.search = value.trim();
        this.debounceFilter();
    }

    handleTypeFilter(value) {
        this.filters.type = value;
        this.applyFilters();
    }

    debounceFilter() {
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }

        this.debounceTimer = setTimeout(() => {
            this.applyFilters();
        }, 300);
    }

    applyFilters() {
        if (window.roomsCore) {
            window.roomsCore.currentFilter.search = this.filters.search;
            window.roomsCore.currentFilter.category = this.filters.type;
            window.roomsCore.loadAllRooms();
        }
    }

    clearFilters() {
        this.filters = {
            search: '',
            type: 'all',
            voice: false,
            discoverable: false
        };

        // Reset UI elements
        const searchInput = document.getElementById('searchInput');
        const roomTypeFilter = document.getElementById('roomTypeFilter');

        if (searchInput) {
            searchInput.value = '';
        }

        if (roomTypeFilter) {
            roomTypeFilter.value = 'all';
        }

        this.applyFilters();
    }

    getActiveFilters() {
        return { ...this.filters };
    }

    setFilters(newFilters) {
        this.filters = { ...this.filters, ...newFilters };
        this.updateFilterUI();
        this.applyFilters();
    }

    updateFilterUI() {
        const searchInput = document.getElementById('searchInput');
        const roomTypeFilter = document.getElementById('roomTypeFilter');

        if (searchInput && this.filters.search !== searchInput.value) {
            searchInput.value = this.filters.search;
        }

        if (roomTypeFilter && this.filters.type !== roomTypeFilter.value) {
            roomTypeFilter.value = this.filters.type;
        }
    }

    filterRooms(rooms, filterType = 'my') {
        let filteredRooms = [...rooms];

        // Apply search filter
        if (this.filters.search) {
            const searchTerm = this.filters.search.toLowerCase();
            filteredRooms = filteredRooms.filter(room => 
                room.name.toLowerCase().includes(searchTerm) ||
                (room.description && room.description.toLowerCase().includes(searchTerm)) ||
                (room.topic && room.topic.toLowerCase().includes(searchTerm))
            );
        }

        // Apply type filter for my rooms
        if (filterType === 'my' && this.filters.type !== 'all') {
            switch (this.filters.type) {
                case 'owned':
                    filteredRooms = filteredRooms.filter(room => room.is_owner);
                    break;
                case 'member':
                    filteredRooms = filteredRooms.filter(room => !room.is_owner);
                    break;
                case 'voice':
                    filteredRooms = filteredRooms.filter(room => room.voice_enabled);
                    break;
            }
        }

        return filteredRooms;
    }

    createFilterSummary() {
        const activeFilters = [];

        if (this.filters.search) {
            activeFilters.push(`Search: "${this.filters.search}"`);
        }

        if (this.filters.type !== 'all') {
            const typeLabels = {
                owned: 'Rooms I Own',
                member: 'Rooms I\'m In',
                voice: 'Voice Enabled'
            };
            activeFilters.push(`Type: ${typeLabels[this.filters.type] || this.filters.type}`);
        }

        return activeFilters;
    }

    showFilterSummary() {
        const summary = this.createFilterSummary();
        
        if (summary.length === 0) {
            this.hideFilterSummary();
            return;
        }

        let summaryElement = document.getElementById('filter-summary');
        
        if (!summaryElement) {
            summaryElement = document.createElement('div');
            summaryElement.id = 'filter-summary';
            summaryElement.className = 'bg-blue-900 bg-opacity-50 border border-blue-500 p-3 rounded-lg mb-4';
            
            const filtersContainer = document.querySelector('.bg-secondary.p-4.border-b');
            if (filtersContainer) {
                filtersContainer.insertAdjacentElement('afterend', summaryElement);
            }
        }

        summaryElement.innerHTML = `
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-2">
                    <i class="ri-filter-line text-blue-400"></i>
                    <span class="text-blue-200 text-sm">Active filters: ${summary.join(', ')}</span>
                </div>
                <button onclick="window.roomsFilters.clearFilters()" 
                        class="text-blue-400 hover:text-blue-300 text-sm">
                    Clear all
                </button>
            </div>
        `;
    }

    hideFilterSummary() {
        const summaryElement = document.getElementById('filter-summary');
        if (summaryElement) {
            summaryElement.remove();
        }
    }

    exportFilters() {
        return JSON.stringify(this.filters);
    }

    importFilters(filtersJson) {
        try {
            const filters = JSON.parse(filtersJson);
            this.setFilters(filters);
            return true;
        } catch (error) {
            console.error('Error importing filters:', error);
            return false;
        }
    }
}

// Initialize global instance
window.roomsFilters = new RoomsFilters();