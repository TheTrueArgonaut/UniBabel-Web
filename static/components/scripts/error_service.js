/**
 * 🎯 ERROR SERVICE - Single Responsibility: Error handling & user feedback
 * 
 * SRIMI Principles:
 * - Single Responsibility: ONLY handles errors and user notifications
 * - Reactive: Listens to error events and reacts
 * - Injectable: Can be injected into any page orchestrator
 * - Micro: Focused only on error management
 * - Interfaces: Clear error handling contract
 */
class ErrorService {
    constructor(orchestrator) {
        this.orchestrator = orchestrator;
        this.errorQueue = [];
        this.isShowingError = false;
        
        this.initialize();
    }
    
    initialize() {
        // Listen for global errors
        window.addEventListener('error', (event) => {
            this.handleError(event.error, 'JavaScript Error');
        });
        
        window.addEventListener('unhandledrejection', (event) => {
            this.handleError(event.reason, 'Unhandled Promise Rejection');
        });
        
        // Listen for orchestrator error events
        this.orchestrator.on('error', (e) => {
            this.handleError(e.detail.error, e.detail.context);
        });
    }
    
    /**
     * 🚨 Handle any error
     */
    handleError(error, context = 'Unknown') {
        console.error(`🚨 ${this.orchestrator.pageName} Error [${context}]:`, error);
        
        this.orchestrator.emit('error:logged', { error, context });
        
        // Queue user-friendly message
        this.queueErrorMessage(this.getErrorMessage(error, context));
    }
    
    /**
     * 📝 Convert technical errors to user-friendly messages
     */
    getErrorMessage(error, context) {
        switch (context) {
            case 'Network Error':
                return 'Connection problem. Please check your internet and try again.';
            case 'Validation Error':
                return 'Please check your input and try again.';
            case 'Authentication Error':
                return 'Your session has expired. Please log in again.';
            case 'Permission Error':
                return 'You don\'t have permission to perform this action.';
            default:
                return 'Something went wrong. Please try again.';
        }
    }
    
    /**
     * 📊 Queue error messages to avoid spam
     */
    queueErrorMessage(message) {
        this.errorQueue.push(message);
        
        if (!this.isShowingError) {
            this.showNextError();
        }
    }
    
    /**
     * 🎨 Show error to user
     */
    showNextError() {
        if (this.errorQueue.length === 0) {
            this.isShowingError = false;
            return;
        }
        
        this.isShowingError = true;
        const message = this.errorQueue.shift();
        
        this.renderErrorMessage(message);
        
        // Auto-hide after 5 seconds, then show next
        setTimeout(() => {
            this.hideErrorMessage();
            setTimeout(() => this.showNextError(), 300);
        }, 5000);
    }
    
    /**
     * 🎨 Render error message
     */
    renderErrorMessage(message) {
        const container = this.getErrorContainer();
        
        container.innerHTML = `
            <div class="error-message bg-red-900/30 border border-red-500 rounded-lg p-4 mb-4 animate-slide-down">
                <div class="flex items-center justify-between">
                    <div class="flex items-center">
                        <i class="ri-error-warning-line text-red-400 mr-2"></i>
                        <span class="text-red-200">${message}</span>
                    </div>
                    <button class="error-dismiss text-red-400 hover:text-red-200 ml-4" 
                            onclick="this.closest('.error-message').style.display='none'">
                        <i class="ri-close-line"></i>
                    </button>
                </div>
            </div>
        `;
        
        container.style.display = 'block';
        
        // Announce to screen readers
        this.orchestrator.emit('accessibility:announce', { 
            message: `Error: ${message}` 
        });
    }
    
    /**
     * 🎨 Hide error message
     */
    hideErrorMessage() {
        const container = this.getErrorContainer();
        const errorMessage = container.querySelector('.error-message');
        
        if (errorMessage) {
            errorMessage.style.animation = 'slide-up 0.3s ease-in-out';
            setTimeout(() => {
                container.style.display = 'none';
            }, 300);
        }
    }
    
    /**
     * 🎯 Get or create error container
     */
    getErrorContainer() {
        let container = document.getElementById('error-container');
        
        if (!container) {
            container = document.createElement('div');
            container.id = 'error-container';
            container.className = 'fixed top-4 right-4 z-50 max-w-md';
            container.style.display = 'none';
            document.body.appendChild(container);
        }
        
        return container;
    }
    
    /**
     * ✨ Success message (bonus feature)
     */
    showSuccess(message) {
        const container = this.getErrorContainer();
        
        container.innerHTML = `
            <div class="success-message bg-green-900/30 border border-green-500 rounded-lg p-4 mb-4 animate-slide-down">
                <div class="flex items-center justify-between">
                    <div class="flex items-center">
                        <i class="ri-check-line text-green-400 mr-2"></i>
                        <span class="text-green-200">${message}</span>
                    </div>
                    <button class="success-dismiss text-green-400 hover:text-green-200 ml-4"
                            onclick="this.closest('.success-message').style.display='none'">
                        <i class="ri-close-line"></i>
                    </button>
                </div>
            </div>
        `;
        
        container.style.display = 'block';
        
        // Auto-hide after 3 seconds
        setTimeout(() => {
            const successMessage = container.querySelector('.success-message');
            if (successMessage) {
                successMessage.style.animation = 'slide-up 0.3s ease-in-out';
                setTimeout(() => {
                    container.style.display = 'none';
                }, 300);
            }
        }, 3000);
        
        this.orchestrator.emit('accessibility:announce', { 
            message: `Success: ${message}` 
        });
    }
    
    /**
     * 🧹 Cleanup
     */
    destroy() {
        this.errorQueue = [];
        this.isShowingError = false;
        
        // Remove error container
        const container = document.getElementById('error-container');
        if (container) {
            container.remove();
        }
    }
}

// 🎯 Export for modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ErrorService };
}