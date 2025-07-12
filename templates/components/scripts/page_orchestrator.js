/**
 * 🎯 PAGE ORCHESTRATOR - Unified Microservice Management
 * 
 * SRIMI Principles:
 * - Single Responsibility: Manages page-level microservice coordination
 * - Reactive: Event-driven microservice communication
 * - Injectable: Dependency injection for microservices
 * - Micro: Focused on orchestration only
 * - Interfaces: Clear contracts for microservice interaction
 */
class PageOrchestrator {
    constructor(pageName, options = {}) {
        this.pageName = pageName;
        this.options = {
            enableAccessibility: true,
            enableAnalytics: false,
            enableErrorHandling: true,
            debugMode: false,
            ...options
        };
        
        this.microservices = new Map();
        this.eventBus = new EventTarget();
        this.state = new Proxy({}, {
            set: (target, prop, value) => {
                target[prop] = value;
                this.emit('state:change', { property: prop, value, previous: target[prop] });
                return true;
            }
        });
        
        this.initialize();
    }
    
    /**
     * 🚀 Initialize orchestrator with core services
     */
    initialize() {
        if (this.options.debugMode) {
            console.log(`🎯 Initializing ${this.pageName} orchestrator`);
        }
        
        // Initialize core services
        this.initializeErrorHandling();
        this.initializeAccessibility();
        this.initializeLoadingStates();
        
        // Page-specific initialization
        this.onPageReady();
    }
    
    /**
     * 📝 Register a microservice
     */
    registerService(name, service) {
        if (this.microservices.has(name)) {
            console.warn(`⚠️ Service '${name}' already registered, overwriting`);
        }
        
        this.microservices.set(name, service);
        
        // Inject orchestrator reference into service
        if (service && typeof service === 'object') {
            service.orchestrator = this;
        }
        
        this.emit('service:registered', { name, service });
        
        if (this.options.debugMode) {
            console.log(`✅ Service '${name}' registered`);
        }
    }
    
    /**
     * 🔍 Get a microservice
     */
    getService(name) {
        return this.microservices.get(name);
    }
    
    /**
     * 📡 Event bus for microservice communication
     */
    emit(event, data = {}) {
        this.eventBus.dispatchEvent(new CustomEvent(event, { detail: data }));
    }
    
    on(event, callback) {
        this.eventBus.addEventListener(event, callback);
    }
    
    off(event, callback) {
        this.eventBus.removeEventListener(event, callback);
    }
    
    /**
     * 🎨 Loading state management
     */
    initializeLoadingStates() {
        this.state.isLoading = false;
        this.state.loadingMessage = '';
        
        this.on('state:change', (e) => {
            if (e.detail.property === 'isLoading') {
                this.updateLoadingUI(e.detail.value, this.state.loadingMessage);
            }
        });
    }
    
    setLoading(isLoading, message = '') {
        this.state.isLoading = isLoading;
        this.state.loadingMessage = message;
    }
    
    updateLoadingUI(isLoading, message) {
        const loadingIndicator = document.querySelector('.loading-indicator');
        if (loadingIndicator) {
            loadingIndicator.style.display = isLoading ? 'block' : 'none';
            const messageEl = loadingIndicator.querySelector('.loading-message');
            if (messageEl) {
                messageEl.textContent = message;
            }
        }
    }
    
    /**
     * 🛡️ Error handling system
     */
    initializeErrorHandling() {
        if (!this.options.enableErrorHandling) return;
        
        window.addEventListener('error', (event) => {
            this.handleError(event.error, 'JavaScript Error');
        });
        
        window.addEventListener('unhandledrejection', (event) => {
            this.handleError(event.reason, 'Unhandled Promise Rejection');
        });
    }
    
    handleError(error, context = 'Unknown') {
        console.error(`🚨 ${this.pageName} Error [${context}]:`, error);
        
        this.emit('error', { error, context });
        
        // Show user-friendly error message
        this.showErrorMessage(`Something went wrong. Please try again.`);
    }
    
    showErrorMessage(message) {
        const errorContainer = document.getElementById('error-container');
        if (errorContainer) {
            errorContainer.innerHTML = `
                <div class="bg-red-900/30 border border-red-500 rounded-lg p-4 mb-4">
                    <div class="flex items-center">
                        <i class="ri-error-warning-line text-red-400 mr-2"></i>
                        <span class="text-red-200">${message}</span>
                    </div>
                </div>
            `;
            errorContainer.style.display = 'block';
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                errorContainer.style.display = 'none';
            }, 5000);
        }
    }
    
    /**
     * ♿ Accessibility features
     */
    initializeAccessibility() {
        if (!this.options.enableAccessibility) return;
        
        this.setupScreenReaderAnnouncements();
        this.setupKeyboardNavigation();
        this.setupFocusManagement();
    }
    
    setupScreenReaderAnnouncements() {
        const announcements = document.getElementById('announcements');
        if (!announcements) {
            const div = document.createElement('div');
            div.id = 'announcements';
            div.setAttribute('aria-live', 'polite');
            div.setAttribute('aria-atomic', 'true');
            div.className = 'sr-only';
            document.body.appendChild(div);
        }
    }
    
    announceToScreenReader(message) {
        const announcements = document.getElementById('announcements');
        if (announcements) {
            announcements.textContent = message;
            
            // Clear after announcement
            setTimeout(() => {
                announcements.textContent = '';
            }, 1000);
        }
    }
    
    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            // Escape key handling
            if (e.key === 'Escape') {
                this.emit('keyboard:escape');
            }
            
            // Tab key handling for modal focus trapping
            if (e.key === 'Tab') {
                this.emit('keyboard:tab', { shiftKey: e.shiftKey });
            }
        });
    }
    
    setupFocusManagement() {
        this.focusHistory = [];
        
        this.on('focus:save', () => {
            this.focusHistory.push(document.activeElement);
        });
        
        this.on('focus:restore', () => {
            if (this.focusHistory.length > 0) {
                const lastFocus = this.focusHistory.pop();
                if (lastFocus && lastFocus.focus) {
                    lastFocus.focus();
                }
            }
        });
    }
    
    /**
     * 📊 Analytics integration
     */
    trackEvent(event, data = {}) {
        if (!this.options.enableAnalytics) return;
        
        this.emit('analytics:track', { event, data, page: this.pageName });
        
        // Integration with analytics providers would go here
        if (this.options.debugMode) {
            console.log(`📊 Analytics: ${event}`, data);
        }
    }
    
    /**
     * 🔄 Lifecycle hooks for pages to override
     */
    onPageReady() {
        // Override in subclasses
    }
    
    onBeforeUnload() {
        // Override in subclasses
    }
    
    onVisibilityChange(isVisible) {
        // Override in subclasses
    }
    
    /**
     * 🧹 Cleanup
     */
    destroy() {
        this.microservices.clear();
        this.eventBus.removeEventListener();
        
        if (this.options.debugMode) {
            console.log(`🧹 ${this.pageName} orchestrator destroyed`);
        }
    }
}

/**
 * 🎯 CHAT PAGE ORCHESTRATOR - Specialized for chat functionality
 */
class ChatOrchestrator extends PageOrchestrator {
    constructor(options = {}) {
        super('Chat', {
            enableAccessibility: true,
            enableAnalytics: true,
            ...options
        });
        
        this.currentChatId = null;
        this.messageQueue = [];
        this.connectionStatus = 'disconnected';
    }
    
    onPageReady() {
        this.initializeChatServices();
        this.setupSocketConnection();
        this.setupMessageHandling();
    }
    
    initializeChatServices() {
        // Register core chat services
        this.registerService('socket', new SocketManager(this));
        this.registerService('ui', new UIStateManager(this));
        this.registerService('modal', new ModalManager(this));
        this.registerService('accessibility', new AccessibilityManager(this));
        this.registerService('rooms', new RoomManager(this));
        this.registerService('chat', new ChatCoreManager(this));
    }
    
    setupSocketConnection() {
        this.on('socket:connected', () => {
            this.connectionStatus = 'connected';
            this.announceToScreenReader('Connected to chat server');
            this.processMessageQueue();
        });
        
        this.on('socket:disconnected', () => {
            this.connectionStatus = 'disconnected';
            this.announceToScreenReader('Disconnected from chat server');
        });
    }
    
    setupMessageHandling() {
        this.on('message:send', (e) => {
            const { message, chatId } = e.detail;
            
            if (this.connectionStatus === 'connected') {
                this.getService('socket').sendMessage(message, chatId);
            } else {
                this.messageQueue.push({ message, chatId });
                this.showErrorMessage('Message queued - reconnecting...');
            }
        });
        
        this.on('message:received', (e) => {
            const { message, sender, metadata } = e.detail;
            this.getService('chat').addMessage(message, sender, metadata);
            this.trackEvent('message_received', { sender, hasTranslation: !!metadata.originalText });
        });
    }
    
    processMessageQueue() {
        while (this.messageQueue.length > 0) {
            const queuedMessage = this.messageQueue.shift();
            this.getService('socket').sendMessage(queuedMessage.message, queuedMessage.chatId);
        }
    }
}

/**
 * 🎯 SETTINGS PAGE ORCHESTRATOR - Specialized for settings functionality
 */
class SettingsOrchestrator extends PageOrchestrator {
    constructor(options = {}) {
        super('Settings', {
            enableAccessibility: true,
            enableAnalytics: true,
            ...options
        });
        
        this.unsavedChanges = new Set();
        this.autoSaveTimeout = null;
    }
    
    onPageReady() {
        this.initializeSettingsServices();
        this.setupAutoSave();
        this.setupUnsavedChangesWarning();
    }
    
    initializeSettingsServices() {
        this.registerService('accessibility', new AccessibilityManager(this));
        this.registerService('language', new LanguageManager(this));
        this.registerService('privacy', new PrivacyManager(this));
        this.registerService('notifications', new NotificationManager(this));
        this.registerService('premium', new PremiumManager(this));
    }
    
    setupAutoSave() {
        this.on('setting:changed', (e) => {
            const { setting, value } = e.detail;
            this.unsavedChanges.add(setting);
            
            // Auto-save after 2 seconds of no changes
            clearTimeout(this.autoSaveTimeout);
            this.autoSaveTimeout = setTimeout(() => {
                this.saveSettings();
            }, 2000);
        });
    }
    
    setupUnsavedChangesWarning() {
        window.addEventListener('beforeunload', (e) => {
            if (this.unsavedChanges.size > 0) {
                e.preventDefault();
                e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
                return e.returnValue;
            }
        });
    }
    
    saveSettings() {
        if (this.unsavedChanges.size === 0) return;
        
        this.setLoading(true, 'Saving settings...');
        
        // Simulate API call
        setTimeout(() => {
            this.unsavedChanges.clear();
            this.setLoading(false);
            this.announceToScreenReader('Settings saved successfully');
            this.trackEvent('settings_saved', { 
                changedSettings: Array.from(this.unsavedChanges) 
            });
        }, 1000);
    }
}

// 🚀 Global orchestrator factory
window.createOrchestrator = function(type, options = {}) {
    switch (type) {
        case 'chat':
            return new ChatOrchestrator(options);
        case 'settings':
            return new SettingsOrchestrator(options);
        default:
            return new PageOrchestrator(type, options);
    }
};

// 🎯 Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { 
        PageOrchestrator, 
        ChatOrchestrator, 
        SettingsOrchestrator 
    };
}