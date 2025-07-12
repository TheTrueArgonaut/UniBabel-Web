// Rooms Modals JavaScript - Modal Management & Form Handling
class RoomsModals {
    constructor() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        document.addEventListener('DOMContentLoaded', () => {
            this.initializeButtons();
            this.initializeForms();
        });
    }

    initializeButtons() {
        const createRoomBtn = document.getElementById('createRoomBtn');
        const joinRoomBtn = document.getElementById('joinRoomBtn');

        if (createRoomBtn) {
            createRoomBtn.addEventListener('click', () => this.showCreateRoomModal());
        }

        if (joinRoomBtn) {
            joinRoomBtn.addEventListener('click', () => this.showJoinRoomModal());
        }
    }

    initializeForms() {
        const createRoomForm = document.getElementById('createRoomForm');
        const joinRoomForm = document.getElementById('joinRoomForm');

        if (createRoomForm) {
            createRoomForm.addEventListener('submit', (e) => this.handleCreateRoom(e));
        }

        if (joinRoomForm) {
            joinRoomForm.addEventListener('submit', (e) => this.handleJoinRoom(e));
        }
    }

    showCreateRoomModal() {
        const modal = document.getElementById('createRoomModal');
        if (modal) {
            modal.classList.remove('hidden');
            this.focusFirstInput(modal);
        }
    }

    closeCreateRoomModal() {
        const modal = document.getElementById('createRoomModal');
        if (modal) {
            modal.classList.add('hidden');
            this.resetForm('createRoomForm');
        }
    }

    showJoinRoomModal() {
        const modal = document.getElementById('joinRoomModal');
        if (modal) {
            modal.classList.remove('hidden');
            this.focusFirstInput(modal);
        }
    }

    closeJoinRoomModal() {
        const modal = document.getElementById('joinRoomModal');
        if (modal) {
            modal.classList.add('hidden');
            this.resetForm('joinRoomForm');
        }
    }

    async handleCreateRoom(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const voiceEnabled = formData.get('voice_enabled') !== null;
        const discoverable = formData.get('discoverable') !== null;
        
        const roomData = {
            name: formData.get('name'),
            description: formData.get('description'),
            discoverable: discoverable,
            voice_enabled: voiceEnabled,
        };

        // Validate required fields
        if (!roomData.name || roomData.name.trim() === '') {
            this.showModalError('createRoomModal', 'Room name is required');
            return;
        }

        if (roomData.name.length > 50) {
            this.showModalError('createRoomModal', 'Room name must be less than 50 characters');
            return;
        }

        if (roomData.description && roomData.description.length > 500) {
            this.showModalError('createRoomModal', 'Description must be less than 500 characters');
            return;
        }

        // Disable submit button to prevent double submission
        const submitBtn = e.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.textContent = 'Creating...';

        try {
            await window.roomsApi.createRoom(roomData);
        } catch (error) {
            this.showModalError('createRoomModal', 'Failed to create room');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    }

    async handleJoinRoom(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const inviteCode = formData.get('invite_code');
        
        // Validate invite code
        if (!inviteCode || inviteCode.trim() === '') {
            this.showModalError('joinRoomModal', 'Invite code is required');
            return;
        }

        if (inviteCode.length < 3 || inviteCode.length > 20) {
            this.showModalError('joinRoomModal', 'Invalid invite code format');
            return;
        }

        // Disable submit button to prevent double submission
        const submitBtn = e.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.textContent = 'Joining...';

        try {
            await window.roomsApi.joinRoomWithCode(inviteCode);
        } catch (error) {
            this.showModalError('joinRoomModal', 'Failed to join room');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    }

    showModalError(modalId, message) {
        const modal = document.getElementById(modalId);
        if (!modal) return;

        // Remove existing error messages
        const existingError = modal.querySelector('.modal-error');
        if (existingError) {
            existingError.remove();
        }

        // Create new error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'modal-error bg-red-900 bg-opacity-50 border border-red-500 text-red-200 p-3 rounded-lg mt-4';
        errorDiv.textContent = message;

        // Insert before the button container
        const buttonContainer = modal.querySelector('.flex.justify-end');
        if (buttonContainer) {
            buttonContainer.parentNode.insertBefore(errorDiv, buttonContainer);
        }

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.remove();
            }
        }, 5000);
    }

    hideModalError(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;

        const errorDiv = modal.querySelector('.modal-error');
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    resetForm(formId) {
        const form = document.getElementById(formId);
        if (form) {
            form.reset();
            this.hideModalError(form.closest('.fixed').id);
        }
    }

    focusFirstInput(modal) {
        const firstInput = modal.querySelector('input, textarea, select');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }
    }

    showUpgradeModal(context) {
        // Create upgrade modal dynamically
        const modal = document.createElement('div');
        modal.id = 'upgradeModal';
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        modal.innerHTML = `
            <div class="bg-secondary p-6 rounded-xl max-w-md w-full mx-4">
                <h3 class="text-xl font-bold text-white mb-4">Upgrade to Premium</h3>
                <div class="space-y-4">
                    <div class="bg-gray-700 p-4 rounded-lg">
                        <h4 class="font-semibold text-white mb-2">Premium Features:</h4>
                        <ul class="text-sm text-gray-300 space-y-1">
                            <li>✨ Unlimited rooms (up to 50)</li>
                            <li>🎙️ Voice-enabled rooms</li>
                            <li>🌐 Make rooms discoverable</li>
                            <li>💬 Unlimited messages</li>
                            <li>🛡️ Enhanced privacy protection</li>
                            <li>🚀 Priority translation</li>
                        </ul>
                    </div>
                    <div class="text-center">
                        <div class="text-2xl font-bold text-white">$7.99/month</div>
                        <div class="text-sm text-gray-400">Cancel anytime</div>
                    </div>
                </div>
                <div class="flex justify-end space-x-3 mt-6">
                    <button onclick="window.roomsModals.closeUpgradeModal()" 
                            class="px-4 py-2 bg-gray-600 hover:bg-gray-500 rounded-lg transition-colors">
                        Maybe Later
                    </button>
                    <button onclick="window.location.href='/premium'" 
                            class="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors">
                        Upgrade Now
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Close on background click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeUpgradeModal();
            }
        });
    }

    closeUpgradeModal() {
        const modal = document.getElementById('upgradeModal');
        if (modal) {
            modal.remove();
        }
    }

    validateRoomName(name) {
        if (!name || name.trim() === '') {
            return { valid: false, message: 'Room name is required' };
        }
        if (name.length > 50) {
            return { valid: false, message: 'Room name must be less than 50 characters' };
        }
        if (name.length < 3) {
            return { valid: false, message: 'Room name must be at least 3 characters' };
        }
        return { valid: true };
    }

    validateDescription(description) {
        if (description && description.length > 500) {
            return { valid: false, message: 'Description must be less than 500 characters' };
        }
        return { valid: true };
    }

    validateInviteCode(code) {
        if (!code || code.trim() === '') {
            return { valid: false, message: 'Invite code is required' };
        }
        if (code.length < 3 || code.length > 20) {
            return { valid: false, message: 'Invalid invite code format' };
        }
        return { valid: true };
    }
}

// Global functions for onclick handlers
window.closeCreateRoomModal = () => window.roomsModals.closeCreateRoomModal();
window.closeJoinRoomModal = () => window.roomsModals.closeJoinRoomModal();
window.showUpgradeModal = (context) => window.roomsModals.showUpgradeModal(context);
window.closeUpgradeModal = () => window.roomsModals.closeUpgradeModal();

// Initialize global instance
window.roomsModals = new RoomsModals();