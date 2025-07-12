// Rooms Settings JavaScript - Room Settings Modal Management
class RoomsSettings {
    constructor() {
        this.currentRoomId = null;
        this.currentTab = 'overview';
        this.originalSettings = {};
        this.setupEventListeners();
    }

    setupEventListeners() {
        document.addEventListener('DOMContentLoaded', () => {
            this.initializeSettingsModal();
        });
    }

    initializeSettingsModal() {
        // Color picker synchronization
        const colorPicker = document.getElementById('roomColor');
        const colorHex = document.getElementById('roomColorHex');

        if (colorPicker && colorHex) {
            colorPicker.addEventListener('change', (e) => {
                colorHex.value = e.target.value;
            });

            colorHex.addEventListener('input', (e) => {
                if (this.isValidHexColor(e.target.value)) {
                    colorPicker.value = e.target.value;
                }
            });
        }
    }

    async openRoomSettings(roomId) {
        this.currentRoomId = roomId;
        const modal = document.getElementById('roomSettingsModal');
        
        if (!modal) return;

        // Show modal
        modal.classList.remove('hidden');
        
        // Load room settings
        await this.loadRoomSettings(roomId);
        
        // Show default tab
        this.showSettingsTab('overview');
    }

    closeRoomSettings() {
        const modal = document.getElementById('roomSettingsModal');
        if (modal) {
            modal.classList.add('hidden');
            this.currentRoomId = null;
            this.currentTab = 'overview';
        }
    }

    async loadRoomSettings(roomId) {
        try {
            const settings = await window.roomsApi.getRoomSettings(roomId);
            if (settings) {
                this.originalSettings = settings;
                this.populateSettingsForm(settings);
                await this.loadMembersTab(roomId);
            }
        } catch (error) {
            console.error('Error loading room settings:', error);
        }
    }

    populateSettingsForm(settings) {
        // Overview tab
        this.setInputValue('roomName', settings.name);
        this.setInputValue('roomDescription', settings.description);
        this.setInputValue('roomTopic', settings.topic);
        this.setCheckboxValue('isDiscoverableToggle', settings.discoverable);

        // Appearance tab
        this.setInputValue('roomColor', settings.color || '#dc2626');
        this.setInputValue('roomColorHex', settings.color || '#dc2626');
        this.setInputValue('welcomeMessage', settings.welcome_message);
        this.setInputValue('roomRules', settings.rules);

        // Moderation tab
        this.setCheckboxValue('autoModerate', settings.auto_moderate !== false);
        this.setInputValue('slowModeSeconds', settings.slow_mode_seconds || 0);
        this.setInputValue('messageHistoryLimit', settings.message_history_limit || 1000);
        this.setInputValue('bannedWords', settings.banned_words ? settings.banned_words.join(', ') : '');

        // Privacy tab
        this.setCheckboxValue('hideMemberList', settings.hide_member_list);
        this.setCheckboxValue('requireInviteApproval', settings.require_invite_approval);
        this.setCheckboxValue('restrictFileUploads', settings.restrict_file_uploads);
        this.setCheckboxValue('disableVoiceChat', settings.disable_voice_chat);
        this.setInputValue('autoDeleteDays', settings.auto_delete_days || 0);
    }

    async loadMembersTab(roomId) {
        try {
            const members = await window.roomsApi.getRoomMembers(roomId);
            this.displayMembers(members);
        } catch (error) {
            console.error('Error loading members:', error);
        }
    }

    displayMembers(members) {
        const container = document.getElementById('membersList');
        if (!container) return;

        if (members.length === 0) {
            container.innerHTML = '<p class="text-gray-400">No members found.</p>';
            return;
        }

        container.innerHTML = members.map(member => this.createMemberCard(member)).join('');
    }

    createMemberCard(member) {
        const roleColors = {
            owner: 'bg-red-600',
            admin: 'bg-purple-600',
            moderator: 'bg-blue-600',
            member: 'bg-gray-600'
        };

        const roleColor = roleColors[member.role] || 'bg-gray-600';

        return `
            <div class="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
                <div class="flex items-center space-x-3">
                    <div class="w-10 h-10 bg-primary rounded-full flex items-center justify-center text-white font-semibold">
                        ${member.display_name ? member.display_name[0] : member.username[0]}
                    </div>
                    <div>
                        <p class="text-white font-medium">${this.escapeHtml(member.display_name || member.username)}</p>
                        <p class="text-sm text-gray-400">Joined ${this.formatDate(member.joined_at)}</p>
                    </div>
                </div>
                <div class="flex items-center space-x-2">
                    <span class="${roleColor} px-2 py-1 rounded-full text-xs text-white">${member.role}</span>
                    ${this.canManageMember(member) ? this.createMemberActions(member) : ''}
                </div>
            </div>
        `;
    }

    createMemberActions(member) {
        if (member.role === 'owner') return '';

        return `
            <div class="relative">
                <button onclick="window.roomsSettings.toggleMemberMenu(${member.id})" 
                        class="text-gray-400 hover:text-white p-1">
                    <i class="ri-more-line"></i>
                </button>
                <div id="member-menu-${member.id}" class="absolute right-0 mt-2 w-48 bg-gray-800 rounded-lg shadow-lg z-10 hidden">
                    <div class="py-1">
                        <button onclick="window.roomsSettings.changeRole(${member.id}, 'admin')" 
                                class="block w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-gray-700">
                            Make Admin
                        </button>
                        <button onclick="window.roomsSettings.changeRole(${member.id}, 'moderator')" 
                                class="block w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-gray-700">
                            Make Moderator
                        </button>
                        <button onclick="window.roomsSettings.changeRole(${member.id}, 'member')" 
                                class="block w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-gray-700">
                            Make Member
                        </button>
                        <hr class="border-gray-600">
                        <button onclick="window.roomsSettings.kickMember(${member.id})" 
                                class="block w-full text-left px-4 py-2 text-sm text-red-300 hover:bg-gray-700">
                            Remove from Room
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    showSettingsTab(tabName) {
        // Hide all content
        document.querySelectorAll('.settings-content').forEach(content => {
            content.classList.add('hidden');
        });

        // Remove active class from all tabs
        document.querySelectorAll('.settings-tab').forEach(tab => {
            tab.classList.remove('active');
        });

        // Show selected content
        const content = document.getElementById(`${tabName}-tab`);
        if (content) {
            content.classList.remove('hidden');
        }

        // Add active class to selected tab
        const tab = document.querySelector(`[data-tab="${tabName}"]`);
        if (tab) {
            tab.classList.add('active');
        }

        this.currentTab = tabName;

        // Load specific tab content
        if (tabName === 'members' && this.currentRoomId) {
            this.loadMembersTab(this.currentRoomId);
        }
    }

    async saveRoomSettings() {
        if (!this.currentRoomId) return;

        const settings = this.collectSettings();
        
        // Validate settings
        const validation = this.validateSettings(settings);
        if (!validation.valid) {
            window.roomsApi.showNotification(validation.message, 'error');
            return;
        }

        try {
            const result = await window.roomsApi.updateRoomSettings(this.currentRoomId, settings);
            if (result) {
                this.originalSettings = { ...settings };
            }
        } catch (error) {
            console.error('Error saving settings:', error);
        }
    }

    collectSettings() {
        return {
            name: this.getInputValue('roomName'),
            description: this.getInputValue('roomDescription'),
            topic: this.getInputValue('roomTopic'),
            discoverable: this.getCheckboxValue('isDiscoverableToggle'),
            color: this.getInputValue('roomColorHex'),
            welcome_message: this.getInputValue('welcomeMessage'),
            rules: this.getInputValue('roomRules'),
            auto_moderate: this.getCheckboxValue('autoModerate'),
            slow_mode_seconds: parseInt(this.getInputValue('slowModeSeconds')) || 0,
            message_history_limit: parseInt(this.getInputValue('messageHistoryLimit')) || 1000,
            banned_words: this.getInputValue('bannedWords').split(',').map(w => w.trim()).filter(w => w),
            hide_member_list: this.getCheckboxValue('hideMemberList'),
            require_invite_approval: this.getCheckboxValue('requireInviteApproval'),
            restrict_file_uploads: this.getCheckboxValue('restrictFileUploads'),
            disable_voice_chat: this.getCheckboxValue('disableVoiceChat'),
            auto_delete_days: parseInt(this.getInputValue('autoDeleteDays')) || 0
        };
    }

    validateSettings(settings) {
        if (!settings.name || settings.name.trim() === '') {
            return { valid: false, message: 'Room name is required' };
        }
        if (settings.name.length > 50) {
            return { valid: false, message: 'Room name must be less than 50 characters' };
        }
        if (settings.description && settings.description.length > 500) {
            return { valid: false, message: 'Description must be less than 500 characters' };
        }
        if (settings.slow_mode_seconds < 0 || settings.slow_mode_seconds > 3600) {
            return { valid: false, message: 'Slow mode must be between 0 and 3600 seconds' };
        }
        if (settings.message_history_limit < 100 || settings.message_history_limit > 10000) {
            return { valid: false, message: 'Message history limit must be between 100 and 10000' };
        }
        if (settings.auto_delete_days < 0 || settings.auto_delete_days > 365) {
            return { valid: false, message: 'Auto-delete days must be between 0 and 365' };
        }
        return { valid: true };
    }

    async deleteRoom() {
        if (!this.currentRoomId) return;

        const confirmed = confirm('Are you sure you want to delete this room? This action cannot be undone.');
        if (!confirmed) return;

        const success = await window.roomsApi.deleteRoom(this.currentRoomId);
        if (success) {
            this.closeRoomSettings();
        }
    }

    async changeRole(userId, newRole) {
        if (!this.currentRoomId) return;

        const success = await window.roomsApi.updateMemberRole(this.currentRoomId, userId, newRole);
        if (success) {
            await this.loadMembersTab(this.currentRoomId);
        }
    }

    async kickMember(userId) {
        if (!this.currentRoomId) return;

        const confirmed = confirm('Are you sure you want to remove this member from the room?');
        if (!confirmed) return;

        const success = await window.roomsApi.kickMember(this.currentRoomId, userId);
        if (success) {
            await this.loadMembersTab(this.currentRoomId);
        }
    }

    // Utility methods
    setInputValue(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.value = value || '';
        }
    }

    getInputValue(id) {
        const element = document.getElementById(id);
        return element ? element.value : '';
    }

    setCheckboxValue(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.checked = Boolean(value);
        }
    }

    getCheckboxValue(id) {
        const element = document.getElementById(id);
        return element ? element.checked : false;
    }

    isValidHexColor(hex) {
        return /^#([0-9A-F]{3}){1,2}$/i.test(hex);
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatDate(dateString) {
        return new Date(dateString).toLocaleDateString();
    }

    canManageMember(member) {
        return member.role !== 'owner';
    }

    toggleMemberMenu(memberId) {
        const menu = document.getElementById(`member-menu-${memberId}`);
        if (menu) {
            menu.classList.toggle('hidden');
        }
    }
}

// Global functions for onclick handlers
window.showSettingsTab = (tabName) => window.roomsSettings.showSettingsTab(tabName);
window.saveRoomSettings = () => window.roomsSettings.saveRoomSettings();
window.deleteRoom = () => window.roomsSettings.deleteRoom();
window.closeRoomSettings = () => window.roomsSettings.closeRoomSettings();
window.openRoomSettings = (roomId) => window.roomsSettings.openRoomSettings(roomId);

// Initialize global instance
window.roomsSettings = new RoomsSettings();