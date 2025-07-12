// Settings Accessibility JavaScript - Accessibility Features Management
class SettingsAccessibility {
    constructor() {
        this.features = {
            screenReader: false,
            highContrast: false,
            reduceMotion: false,
            largeText: false,
            keyboardHelp: false
        };
        this.init();
    }

    init() {
        this.setupAccessibilityFeatures();
        this.bindEvents();
        this.detectSystemPreferences();
    }

    setupAccessibilityFeatures() {
        // Screen reader enhancements
        this.setupScreenReaderFeatures();
        
        // Keyboard navigation
        this.setupKeyboardNavigation();
        
        // Focus management
        this.setupFocusManagement();
    }

    setupScreenReaderFeatures() {
        // Add ARIA live regions for dynamic content
        if (!document.getElementById('aria-live-region')) {
            const liveRegion = document.createElement('div');
            liveRegion.id = 'aria-live-region';
            liveRegion.setAttribute('aria-live', 'polite');
            liveRegion.setAttribute('aria-atomic', 'true');
            liveRegion.className = 'sr-only';
            document.body.appendChild(liveRegion);
        }

        // Enhance form labels and descriptions
        this.enhanceFormAccessibility();
    }

    enhanceFormAccessibility() {
        // Ensure all form elements have proper labels
        const formElements = document.querySelectorAll('input, select, textarea');
        formElements.forEach(element => {
            if (!element.getAttribute('aria-label') && !element.getAttribute('aria-labelledby')) {
                const label = document.querySelector(`label[for="${element.id}"]`);
                if (label) {
                    element.setAttribute('aria-labelledby', label.id || element.id + '-label');
                }
            }
        });
    }

    setupKeyboardNavigation() {
        // Tab trap for modals (if any)
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                this.handleTabNavigation(e);
            }
        });

        // Skip links
        this.setupSkipLinks();
    }

    setupSkipLinks() {
        const skipLink = document.querySelector('.skip-link');
        if (skipLink) {
            skipLink.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(skipLink.getAttribute('href'));
                if (target) {
                    target.focus();
                    target.scrollIntoView();
                }
            });
        }
    }

    handleTabNavigation(e) {
        const focusableElements = this.getFocusableElements();
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        if (e.shiftKey && document.activeElement === firstElement) {
            e.preventDefault();
            lastElement.focus();
        } else if (!e.shiftKey && document.activeElement === lastElement) {
            e.preventDefault();
            firstElement.focus();
        }
    }

    getFocusableElements() {
        return Array.from(document.querySelectorAll(
            'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
        )).filter(el => this.isVisible(el));
    }

    isVisible(element) {
        return !!(element.offsetWidth || element.offsetHeight || element.getClientRects().length);
    }

    setupFocusManagement() {
        // Enhance focus indicators
        this.enhanceFocusIndicators();
        
        // Focus restoration for dynamic content
        this.setupFocusRestoration();
    }

    enhanceFocusIndicators() {
        const style = document.createElement('style');
        style.textContent = `
            /* Enhanced focus indicators for accessibility */
            *:focus {
                outline: 2px solid #dc2626 !important;
                outline-offset: 2px !important;
            }
            
            .switch input:focus + .slider {
                outline: 2px solid #dc2626 !important;
                outline-offset: 2px !important;
            }
        `;
        document.head.appendChild(style);
    }

    setupFocusRestoration() {
        // Store focus before settings operations
        this.lastFocusedElement = null;
        
        document.addEventListener('focusin', (e) => {
            this.lastFocusedElement = e.target;
        });
    }

    bindEvents() {
        // Listen for accessibility setting changes
        const accessibilityCheckboxes = [
            'screenReaderMode',
            'highContrast', 
            'reduceMotion',
            'largeText',
            'keyboardHelp'
        ];

        accessibilityCheckboxes.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.addEventListener('change', (e) => {
                    this.handleAccessibilityChange(id, e.target.checked);
                });
            }
        });
    }

    handleAccessibilityChange(feature, isEnabled) {
        this.features[this.camelCase(feature)] = isEnabled;

        switch (feature) {
            case 'screenReaderMode':
                this.toggleScreenReaderMode(isEnabled);
                break;
            case 'highContrast':
                this.toggleHighContrast(isEnabled);
                break;
            case 'reduceMotion':
                this.toggleReduceMotion(isEnabled);
                break;
            case 'largeText':
                this.toggleLargeText(isEnabled);
                break;
            case 'keyboardHelp':
                this.toggleKeyboardHelp(isEnabled);
                break;
        }

        this.announceChange(feature, isEnabled);
    }

    toggleScreenReaderMode(enabled) {
        if (enabled) {
            // Add enhanced ARIA descriptions
            this.addEnhancedDescriptions();
            
            // Enable live region announcements
            this.enableLiveAnnouncements();
        } else {
            // Remove enhanced descriptions
            this.removeEnhancedDescriptions();
            
            // Disable live region announcements
            this.disableLiveAnnouncements();
        }
    }

    addEnhancedDescriptions() {
        // Add detailed descriptions for complex UI elements
        const complexElements = document.querySelectorAll('.settings-card, .switch, .btn');
        complexElements.forEach(element => {
            if (!element.getAttribute('aria-describedby')) {
                const description = this.generateDescription(element);
                if (description) {
                    const descId = 'desc-' + Math.random().toString(36).substr(2, 9);
                    const descElement = document.createElement('div');
                    descElement.id = descId;
                    descElement.className = 'sr-only';
                    descElement.textContent = description;
                    element.appendChild(descElement);
                    element.setAttribute('aria-describedby', descId);
                }
            }
        });
    }

    generateDescription(element) {
        if (element.classList.contains('settings-card')) {
            return 'Settings group with multiple options. Use Tab to navigate between settings.';
        }
        if (element.classList.contains('switch')) {
            return 'Toggle switch. Use Space or Enter to change setting.';
        }
        if (element.classList.contains('btn')) {
            return 'Button. Press Enter or Space to activate.';
        }
        return null;
    }

    removeEnhancedDescriptions() {
        const enhancedDescs = document.querySelectorAll('[id^="desc-"]');
        enhancedDescs.forEach(desc => {
            const element = desc.parentElement;
            if (element) {
                element.removeAttribute('aria-describedby');
            }
            desc.remove();
        });
    }

    toggleHighContrast(enabled) {
        if (enabled) {
            document.body.classList.add('high-contrast');
        } else {
            document.body.classList.remove('high-contrast');
        }
    }

    toggleReduceMotion(enabled) {
        if (enabled) {
            document.body.classList.add('reduce-motion');
            // Disable CSS animations and transitions
            const style = document.createElement('style');
            style.id = 'reduce-motion-style';
            style.textContent = `
                *, *::before, *::after {
                    animation-duration: 0.01ms !important;
                    animation-iteration-count: 1 !important;
                    transition-duration: 0.01ms !important;
                }
            `;
            document.head.appendChild(style);
        } else {
            document.body.classList.remove('reduce-motion');
            const existingStyle = document.getElementById('reduce-motion-style');
            if (existingStyle) {
                existingStyle.remove();
            }
        }
    }

    toggleLargeText(enabled) {
        if (enabled) {
            document.body.classList.add('large-text');
        } else {
            document.body.classList.remove('large-text');
        }
    }

    toggleKeyboardHelp(enabled) {
        if (enabled) {
            this.showKeyboardHelp();
        } else {
            this.hideKeyboardHelp();
        }
    }

    showKeyboardHelp() {
        // Add keyboard shortcut hints
        const helpText = document.createElement('div');
        helpText.id = 'keyboard-help';
        helpText.className = 'fixed bottom-4 right-4 bg-gray-800 text-white p-4 rounded-lg shadow-lg z-50';
        helpText.innerHTML = `
            <h4 class="font-bold mb-2">Keyboard Shortcuts</h4>
            <ul class="text-sm space-y-1">
                <li><kbd>Ctrl+S</kbd> - Save settings</li>
                <li><kbd>Tab</kbd> - Navigate forward</li>
                <li><kbd>Shift+Tab</kbd> - Navigate backward</li>
                <li><kbd>Space</kbd> - Toggle switches</li>
                <li><kbd>Esc</kbd> - Focus back button</li>
            </ul>
        `;
        document.body.appendChild(helpText);
    }

    hideKeyboardHelp() {
        const helpElement = document.getElementById('keyboard-help');
        if (helpElement) {
            helpElement.remove();
        }
    }

    detectSystemPreferences() {
        // Detect and apply system accessibility preferences
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            this.handleAccessibilityChange('reduceMotion', true);
            const element = document.getElementById('reduceMotion');
            if (element) element.checked = true;
        }

        if (window.matchMedia('(prefers-contrast: high)').matches) {
            this.handleAccessibilityChange('highContrast', true);
            const element = document.getElementById('highContrast');
            if (element) element.checked = true;
        }
    }

    enableLiveAnnouncements() {
        this.liveAnnouncementsEnabled = true;
    }

    disableLiveAnnouncements() {
        this.liveAnnouncementsEnabled = false;
    }

    announceChange(feature, isEnabled) {
        if (this.liveAnnouncementsEnabled || this.features.screenReader) {
            const messages = {
                screenReaderMode: `Screen reader mode ${isEnabled ? 'enabled' : 'disabled'}`,
                highContrast: `High contrast mode ${isEnabled ? 'enabled' : 'disabled'}`,
                reduceMotion: `Reduced motion ${isEnabled ? 'enabled' : 'disabled'}`,
                largeText: `Large text ${isEnabled ? 'enabled' : 'disabled'}`,
                keyboardHelp: `Keyboard help ${isEnabled ? 'shown' : 'hidden'}`
            };

            const announcement = messages[feature];
            if (announcement) {
                this.announceToScreenReader(announcement);
            }
        }
    }

    announceToScreenReader(message) {
        const liveRegion = document.getElementById('aria-live-region') || document.getElementById('announcements');
        if (liveRegion) {
            liveRegion.textContent = message;
            setTimeout(() => liveRegion.textContent = '', 3000);
        }
    }

    camelCase(str) {
        return str.replace(/-([a-z])/g, (g) => g[1].toUpperCase());
    }

    // Public API
    isFeatureEnabled(feature) {
        return this.features[feature] || false;
    }

    enableFeature(feature) {
        const element = document.getElementById(feature + 'Mode' || feature);
        if (element && element.type === 'checkbox') {
            element.checked = true;
            element.dispatchEvent(new Event('change'));
        }
    }

    disableFeature(feature) {
        const element = document.getElementById(feature + 'Mode' || feature);
        if (element && element.type === 'checkbox') {
            element.checked = false;
            element.dispatchEvent(new Event('change'));
        }
    }
}

// Initialize global instance
window.settingsAccessibility = new SettingsAccessibility();