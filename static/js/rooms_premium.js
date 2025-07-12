// Rooms Premium JavaScript - Premium Features & Upgrade Handling
class RoomsPremium {
    constructor() {
        this.premiumFeatures = null;
        this.userPremiumStatus = false;
        this.featureLimits = {};
        this.init();
    }

    async init() {
        await this.loadPremiumStatus();
        this.setupPremiumUI();
    }

    async loadPremiumStatus() {
        try {
            const response = await fetch('/api/premium/status');
            const data = await response.json();
            
            if (response.ok) {
                this.userPremiumStatus = data.is_premium;
                this.featureLimits = data.limits || {};
                this.premiumFeatures = data.features || {};
            }
        } catch (error) {
            console.error('Error loading premium status:', error);
            // Default to free tier
            this.userPremiumStatus = false;
            this.featureLimits = {
                max_rooms: 5,
                voice_rooms: false,
                discoverable_rooms: false
            };
        }
    }

    setupPremiumUI() {
        // No restrictions needed - everyone gets all features for this implementation
        this.updateCreateRoomButton(true);
        this.updateFeatureVisibility(true);
    }

    updateCreateRoomButton(canCreate) {
        const createBtn = document.getElementById('createRoomBtn');
        if (!createBtn) return;

        if (canCreate) {
            createBtn.disabled = false;
            createBtn.classList.remove('opacity-50', 'cursor-not-allowed');
            createBtn.title = 'Create a new room';
        } else {
            createBtn.disabled = true;
            createBtn.classList.add('opacity-50', 'cursor-not-allowed');
            createBtn.title = 'Room limit reached - Upgrade to Premium';
            createBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.showUpgradeModal('room_limit');
            });
        }
    }

    updateFeatureVisibility(hasAccess) {
        // Voice chat feature
        const voiceCheckbox = document.getElementById('voiceEnabled');
        if (voiceCheckbox) {
            voiceCheckbox.disabled = !hasAccess;
            if (!hasAccess) {
                voiceCheckbox.parentElement.classList.add('opacity-50');
                voiceCheckbox.addEventListener('change', (e) => {
                    if (e.target.checked && !hasAccess) {
                        e.preventDefault();
                        e.target.checked = false;
                        this.showUpgradeModal('voice_feature');
                    }
                });
            }
        }

        // Discoverable feature
        const discoverableCheckbox = document.getElementById('discoverable');
        if (discoverableCheckbox) {
            discoverableCheckbox.disabled = !hasAccess;
            if (!hasAccess) {
                discoverableCheckbox.parentElement.classList.add('opacity-50');
                discoverableCheckbox.addEventListener('change', (e) => {
                    if (e.target.checked && !hasAccess) {
                        e.preventDefault();
                        e.target.checked = false;
                        this.showUpgradeModal('discoverable_feature');
                    }
                });
            }
        }
    }

    showUpgradeModal(context) {
        const contextMessages = {
            room_limit: 'You\'ve reached the free room limit. Upgrade to create unlimited rooms!',
            voice_feature: 'Voice chat is a premium feature. Upgrade to enable voice rooms!',
            discoverable_feature: 'Making rooms discoverable is a premium feature. Upgrade now!',
            default: 'Upgrade to Premium to unlock all features!'
        };

        const message = contextMessages[context] || contextMessages.default;

        // Create modal
        const modal = document.createElement('div');
        modal.id = 'premiumUpgradeModal';
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        modal.innerHTML = `
            <div class="bg-secondary p-6 rounded-xl max-w-md w-full mx-4">
                <div class="text-center mb-6">
                    <div class="w-16 h-16 bg-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
                        <i class="ri-vip-crown-line text-2xl text-white"></i>
                    </div>
                    <h3 class="text-xl font-bold text-white mb-2">Upgrade to Premium</h3>
                    <p class="text-gray-300">${message}</p>
                </div>
                
                <div class="space-y-4 mb-6">
                    <div class="bg-gray-700 p-4 rounded-lg">
                        <h4 class="font-semibold text-white mb-3">Premium Features:</h4>
                        <div class="space-y-2">
                            <div class="flex items-center space-x-2">
                                <i class="ri-check-line text-green-400"></i>
                                <span class="text-sm text-gray-300">Unlimited rooms (up to 50)</span>
                            </div>
                            <div class="flex items-center space-x-2">
                                <i class="ri-check-line text-green-400"></i>
                                <span class="text-sm text-gray-300">Voice-enabled rooms</span>
                            </div>
                            <div class="flex items-center space-x-2">
                                <i class="ri-check-line text-green-400"></i>
                                <span class="text-sm text-gray-300">Make rooms discoverable</span>
                            </div>
                            <div class="flex items-center space-x-2">
                                <i class="ri-check-line text-green-400"></i>
                                <span class="text-sm text-gray-300">Priority support</span>
                            </div>
                            <div class="flex items-center space-x-2">
                                <i class="ri-check-line text-green-400"></i>
                                <span class="text-sm text-gray-300">Advanced room settings</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="text-center bg-gradient-to-r from-purple-600 to-pink-600 p-4 rounded-lg">
                        <div class="text-2xl font-bold text-white">$7.99/month</div>
                        <div class="text-sm text-purple-100">Cancel anytime • 7-day free trial</div>
                    </div>
                </div>
                
                <div class="flex justify-end space-x-3">
                    <button onclick="window.roomsPremium.closeUpgradeModal()" 
                            class="px-4 py-2 bg-gray-600 hover:bg-gray-500 rounded-lg transition-colors">
                        Maybe Later
                    </button>
                    <button onclick="window.location.href='/premium'" 
                            class="px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 rounded-lg transition-colors text-white font-semibold">
                        Start Free Trial
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

        // Track upgrade modal view
        this.trackEvent('upgrade_modal_shown', { context });
    }

    closeUpgradeModal() {
        const modal = document.getElementById('premiumUpgradeModal');
        if (modal) {
            modal.remove();
        }
    }

    checkRoomLimit() {
        // For this implementation, always return true (no limits)
        return { canCreate: true, limit: Infinity, current: 0 };
    }

    checkVoiceFeature() {
        // For this implementation, always return true (no restrictions)
        return { hasAccess: true };
    }

    checkDiscoverableFeature() {
        // For this implementation, always return true (no restrictions)
        return { hasAccess: true };
    }

    showFeatureTooltip(feature, element) {
        const tooltips = {
            voice: 'Voice chat allows real-time audio communication in your rooms',
            discoverable: 'Discoverable rooms can be found and joined by other users',
            unlimited_rooms: 'Create as many rooms as you need for different topics'
        };

        const tooltip = document.createElement('div');
        tooltip.className = 'absolute z-50 bg-gray-800 text-white text-sm p-2 rounded shadow-lg';
        tooltip.textContent = tooltips[feature] || 'Premium feature';
        
        document.body.appendChild(tooltip);
        
        // Position tooltip
        const rect = element.getBoundingClientRect();
        tooltip.style.left = rect.left + 'px';
        tooltip.style.top = (rect.top - tooltip.offsetHeight - 5) + 'px';
        
        // Remove after 3 seconds
        setTimeout(() => {
            if (tooltip.parentNode) {
                tooltip.remove();
            }
        }, 3000);
    }

    trackEvent(eventName, data = {}) {
        // Track premium-related events for analytics
        try {
            if (window.gtag) {
                window.gtag('event', eventName, {
                    event_category: 'premium',
                    ...data
                });
            }
        } catch (error) {
            console.debug('Analytics tracking failed:', error);
        }
    }

    async refreshPremiumStatus() {
        await this.loadPremiumStatus();
        this.setupPremiumUI();
        
        // Refresh room data to show updated features
        if (window.roomsCore) {
            window.roomsCore.refreshRooms();
        }
    }

    isPremium() {
        return this.userPremiumStatus;
    }

    getFeatureLimits() {
        return { ...this.featureLimits };
    }

    showSuccessUpgrade() {
        window.roomsApi.showNotification(
            'Welcome to Premium! All features are now unlocked!',
            'success'
        );
        this.refreshPremiumStatus();
    }

    handleFeatureClick(feature, callback) {
        const hasAccess = this.checkFeatureAccess(feature);
        
        if (hasAccess) {
            callback();
        } else {
            this.showUpgradeModal(feature);
        }
    }

    checkFeatureAccess(feature) {
        // For this implementation, always return true (all features available)
        return true;
    }
}

// Initialize global instance
window.roomsPremium = new RoomsPremium();