// Settings Premium JavaScript - Premium Subscription Management
class SettingsPremium {
    constructor() {
        this.premiumStatus = {
            isPremium: false,
            subscriptionStatus: null,
            nextBilling: null,
            features: {}
        };
    }

    async loadPremiumStatus() {
        try {
            const response = await fetch('/api/premium/features');
            const data = await response.json();
            
            if (response.ok) {
                this.premiumStatus.isPremium = data.subscription.is_premium;
                this.premiumStatus.subscriptionStatus = data.subscription;
                this.premiumStatus.features = data;
                
                if (this.premiumStatus.isPremium) {
                    this.showPremiumSection(data);
                } else {
                    this.showUpgradeSection(data);
                }
            } else {
                // Default to free user
                this.showUpgradeSection({});
            }
        } catch (error) {
            console.error('Error loading premium status:', error);
            // Default to free user on error
            this.showUpgradeSection({});
        }
    }

    showPremiumSection(data) {
        const premiumSection = document.getElementById('premiumSection');
        const upgradeSection = document.getElementById('upgradeSection');
        
        if (premiumSection) premiumSection.classList.remove('hidden');
        if (upgradeSection) upgradeSection.classList.add('hidden');
        
        // Update subscription status
        if (data.subscription && data.subscription.status) {
            this.updateSubscriptionDetails(data.subscription.status);
        }

        // Bind premium management functions
        this.bindPremiumEvents();
    }

    showUpgradeSection(data) {
        const upgradeSection = document.getElementById('upgradeSection');
        const premiumSection = document.getElementById('premiumSection');
        
        if (upgradeSection) upgradeSection.classList.remove('hidden');
        if (premiumSection) premiumSection.classList.add('hidden');
        
        // Bind upgrade events
        this.bindUpgradeEvents();
    }

    updateSubscriptionDetails(status) {
        const subscriptionStatus = document.getElementById('subscriptionStatus');
        const nextBilling = document.getElementById('nextBilling');
        
        if (subscriptionStatus) {
            subscriptionStatus.textContent = 
                `Premium Active - Next billing: ${status.next_billing_date || 'Loading...'}`;
        }
        
        if (nextBilling && status.next_billing_date) {
            nextBilling.textContent = status.next_billing_date;
        }
    }

    bindPremiumEvents() {
        // Bind global functions for premium management
        window.manageBilling = () => this.manageBilling();
        window.cancelSubscription = () => this.cancelSubscription();
    }

    bindUpgradeEvents() {
        // Upgrade button should already be bound via onclick in HTML
        // Additional upgrade tracking can be added here
        this.trackUpgradeView();
    }

    manageBilling() {
        window.settingsCore.announceToScreenReader('Redirecting to billing management...');
        
        // For now, show placeholder
        alert('Billing management will be available when Stripe integration is complete.');
        
        // When Stripe is implemented, this will redirect to:
        // window.location.href = '/api/billing/manage';
    }

    cancelSubscription() {
        const confirmed = confirm(
            'Are you sure you want to cancel your premium subscription?\n\n' +
            '• Data collection will resume immediately\n' +
            '• Premium star badge will be removed\n' +
            '• Room priority will be lost\n' +
            '• You can resubscribe anytime'
        );
        
        if (confirmed) {
            this.processCancellation();
        }
    }

    async processCancellation() {
        window.settingsCore.announceToScreenReader('Canceling subscription...');
        
        // Show processing state
        const cancelBtn = event.target;
        const originalText = cancelBtn.textContent;
        cancelBtn.textContent = 'Canceling...';
        cancelBtn.disabled = true;
        
        try {
            // For now, show placeholder
            setTimeout(() => {
                alert('Subscription cancellation will be available when Stripe integration is complete.');
                cancelBtn.textContent = originalText;
                cancelBtn.disabled = false;
            }, 1000);
            
            // When Stripe is implemented, this will call:
            // const response = await fetch('/api/subscription/cancel', { method: 'POST' });
            // const data = await response.json();
            // if (data.success) {
            //     window.settingsCore.announceToScreenReader('Subscription canceled successfully');
            //     this.loadPremiumStatus(); // Refresh to show free user section
            // }
        } catch (error) {
            console.error('Error canceling subscription:', error);
            cancelBtn.textContent = originalText;
            cancelBtn.disabled = false;
            window.settingsCore.announceToScreenReader('Error canceling subscription');
        }
    }

    trackUpgradeView() {
        // Track when user views upgrade section for analytics
        try {
            if (window.gtag) {
                window.gtag('event', 'upgrade_section_viewed', {
                    event_category: 'premium',
                    event_label: 'settings_page'
                });
            }
        } catch (error) {
            console.debug('Analytics tracking failed:', error);
        }
    }

    trackUpgradeClick() {
        // Track when user clicks upgrade button
        try {
            if (window.gtag) {
                window.gtag('event', 'upgrade_button_clicked', {
                    event_category: 'premium',
                    event_label: 'settings_page'
                });
            }
        } catch (error) {
            console.debug('Analytics tracking failed:', error);
        }
    }

    // Premium feature checks
    isPremiumUser() {
        return this.premiumStatus.isPremium;
    }

    hasFeature(featureName) {
        return this.premiumStatus.features[featureName] || false;
    }

    getSubscriptionStatus() {
        return this.premiumStatus.subscriptionStatus;
    }

    // Premium-specific settings management
    updatePremiumSettings(settings) {
        if (!this.isPremiumUser()) {
            console.warn('Attempted to update premium settings for free user');
            return false;
        }

        // Apply premium-specific settings
        this.applyPremiumFeatures(settings);
        return true;
    }

    applyPremiumFeatures(settings) {
        // Data collection protection
        if (this.hasFeature('data_protection')) {
            this.enableDataProtection();
        }

        // Premium badge
        if (this.hasFeature('premium_badge')) {
            this.enablePremiumBadge();
        }

        // Room priority
        if (this.hasFeature('room_priority')) {
            this.enableRoomPriority();
        }
    }

    enableDataProtection() {
        // Disable data collection and tracking
        if (window.gtag) {
            window.gtag('config', 'GA_MEASUREMENT_ID', {
                anonymize_ip: true,
                allow_google_signals: false,
                allow_ad_personalization_signals: false
            });
        }

        // Set data protection indicator
        const dataProtection = document.getElementById('dataProtection');
        if (dataProtection) {
            dataProtection.checked = true;
            dataProtection.disabled = true;
        }
    }

    enablePremiumBadge() {
        // Enable premium badge display
        const premiumBadgeToggle = document.getElementById('premiumBadgeToggle');
        if (premiumBadgeToggle) {
            premiumBadgeToggle.checked = true;
            premiumBadgeToggle.disabled = true;
        }
    }

    enableRoomPriority() {
        // Enable room priority boost
        const roomPriority = document.getElementById('roomPriority');
        if (roomPriority) {
            roomPriority.checked = true;
            roomPriority.disabled = true;
        }
    }

    // Subscription management
    async refreshSubscriptionStatus() {
        await this.loadPremiumStatus();
        window.settingsCore.announceToScreenReader('Subscription status refreshed');
    }

    showUpgradeSuccess() {
        window.settingsCore.announceToScreenReader('Welcome to Premium! All features are now unlocked!');
        this.refreshSubscriptionStatus();
    }

    // Export/Import premium settings
    exportPremiumSettings() {
        if (!this.isPremiumUser()) {
            return null;
        }

        return {
            premium: true,
            subscription: this.premiumStatus.subscriptionStatus,
            features: this.premiumStatus.features,
            settings: {
                dataProtection: true,
                premiumBadge: true,
                roomPriority: true
            }
        };
    }

    importPremiumSettings(premiumData) {
        if (!this.isPremiumUser() || !premiumData.premium) {
            return false;
        }

        // Apply imported premium settings
        this.applyPremiumFeatures(premiumData.settings);
        return true;
    }
}

// Initialize global instance
window.settingsPremium = new SettingsPremium();