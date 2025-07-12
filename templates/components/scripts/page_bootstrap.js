/**
 * 🎯 PAGE BOOTSTRAP - Single Responsibility: Initialize page with microservices
 * 
 * Usage Example:
 * <script>
 *   // Initialize page with microservices
 *   const page = bootstrapPage('chat', {
 *     services: ['error', 'loading', 'accessibility'],
 *     debugMode: true
 *   });
 * </script>
 */
function bootstrapPage(pageName, options = {}) {
    const defaultOptions = {
        services: ['error', 'loading'],
        debugMode: false,
        analytics: false,
        ...options
    };
    
    // Create core orchestrator
    const orchestrator = createOrchestrator(pageName, {
        debugMode: defaultOptions.debugMode
    });
    
    // Register core services
    const services = {};
    
    if (defaultOptions.services.includes('error')) {
        services.error = new ErrorService(orchestrator);
        orchestrator.register('error', services.error);
    }
    
    if (defaultOptions.services.includes('loading')) {
        services.loading = new LoadingService(orchestrator);
        orchestrator.register('loading', services.loading);
    }
    
    if (defaultOptions.services.includes('accessibility')) {
        services.accessibility = new AccessibilityService(orchestrator);
        orchestrator.register('accessibility', services.accessibility);
    }
    
    // Set up page-specific services
    setupPageServices(orchestrator, pageName, services);
    
    // Return page controller
    return {
        orchestrator,
        services,
        
        // Helper methods
        loading: (isLoading, message) => {
            orchestrator.state.isLoading = isLoading;
            orchestrator.state.loadingMessage = message;
        },
        
        error: (message) => {
            services.error?.showError?.(message);
        },
        
        success: (message) => {
            services.error?.showSuccess?.(message);
        },
        
        track: (event, data) => {
            orchestrator.emit('analytics:track', { event, data });
        }
    };
}

/**
 * 🎯 Set up page-specific services
 */
function setupPageServices(orchestrator, pageName, services) {
    switch (pageName) {
        case 'chat':
            setupChatServices(orchestrator, services);
            break;
        case 'settings':
            setupSettingsServices(orchestrator, services);
            break;
        case 'rooms':
            setupRoomsServices(orchestrator, services);
            break;
        // Add more page-specific setups as needed
    }
}

/**
 * 🎯 Chat page services
 */
function setupChatServices(orchestrator, services) {
    // Socket service
    if (typeof SocketManager !== 'undefined') {
        services.socket = new SocketManager(orchestrator);
        orchestrator.register('socket', services.socket);
    }
    
    // Chat core service
    if (typeof ChatCoreManager !== 'undefined') {
        services.chat = new ChatCoreManager(orchestrator);
        orchestrator.register('chat', services.chat);
    }
    
    // UI state service
    if (typeof UIStateManager !== 'undefined') {
        services.ui = new UIStateManager(orchestrator);
        orchestrator.register('ui', services.ui);
    }
}

/**
 * 🎯 Settings page services
 */
function setupSettingsServices(orchestrator, services) {
    // Settings auto-save
    orchestrator.unsavedChanges = new Set();
    
    orchestrator.on('setting:changed', (e) => {
        orchestrator.unsavedChanges.add(e.detail.setting);
        
        // Auto-save after 2 seconds
        clearTimeout(orchestrator.autoSaveTimeout);
        orchestrator.autoSaveTimeout = setTimeout(() => {
            services.loading?.setGlobalLoading(true, 'Saving settings...');
            
            // Simulate API call
            setTimeout(() => {
                orchestrator.unsavedChanges.clear();
                services.loading?.setGlobalLoading(false);
                services.error?.showSuccess('Settings saved successfully');
            }, 1000);
        }, 2000);
    });
}

/**
 * 🎯 Rooms page services
 */
function setupRoomsServices(orchestrator, services) {
    // Room management
    if (typeof RoomManager !== 'undefined') {
        services.rooms = new RoomManager(orchestrator);
        orchestrator.register('rooms', services.rooms);
    }
    
    // Modal management
    if (typeof ModalManager !== 'undefined') {
        services.modal = new ModalManager(orchestrator);
        orchestrator.register('modal', services.modal);
    }
}

/**
 * 🎯 Accessibility Service (lightweight)
 */
class AccessibilityService {
    constructor(orchestrator) {
        this.orchestrator = orchestrator;
        this.initialize();
    }
    
    initialize() {
        this.setupScreenReaderAnnouncements();
        this.setupKeyboardNavigation();
        
        // Listen for announcement requests
        this.orchestrator.on('accessibility:announce', (e) => {
            this.announceToScreenReader(e.detail.message);
        });
    }
    
    setupScreenReaderAnnouncements() {
        let announcements = document.getElementById('announcements');
        if (!announcements) {
            announcements = document.createElement('div');
            announcements.id = 'announcements';
            announcements.setAttribute('aria-live', 'polite');
            announcements.setAttribute('aria-atomic', 'true');
            announcements.className = 'sr-only';
            document.body.appendChild(announcements);
        }
    }
    
    announceToScreenReader(message) {
        const announcements = document.getElementById('announcements');
        if (announcements) {
            announcements.textContent = message;
            setTimeout(() => {
                announcements.textContent = '';
            }, 1000);
        }
    }
    
    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.orchestrator.emit('keyboard:escape');
            }
            if (e.key === 'Tab') {
                this.orchestrator.emit('keyboard:tab', { shiftKey: e.shiftKey });
            }
        });
    }
}

/**
 * 🎯 Quick page initialization for common patterns
 */
window.initializePage = bootstrapPage;

// Common page configurations
window.pageConfigs = {
    chat: {
        services: ['error', 'loading', 'accessibility'],
        debugMode: false,
        analytics: true
    },
    settings: {
        services: ['error', 'loading', 'accessibility'],
        debugMode: false,
        analytics: true
    },
    rooms: {
        services: ['error', 'loading', 'accessibility'],
        debugMode: false,
        analytics: true
    },
    dashboard: {
        services: ['error', 'loading', 'accessibility'],
        debugMode: false,
        analytics: true
    }
};

// 🎯 Export for modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { 
        bootstrapPage, 
        AccessibilityService,
        setupPageServices,
        setupChatServices,
        setupSettingsServices,
        setupRoomsServices
    };
}