/**
 * 🎯 LOADING SERVICE - Single Responsibility: Loading states & user feedback
 * 
 * SRIMI Principles:
 * - Single Responsibility: ONLY handles loading states and spinners
 * - Reactive: Listens to loading events and updates UI
 * - Injectable: Can be injected into any page orchestrator
 * - Micro: Focused only on loading management
 * - Interfaces: Clear loading state contract
 */
class LoadingService {
    constructor(orchestrator) {
        this.orchestrator = orchestrator;
        this.loadingStates = new Map();
        this.globalLoading = false;
        this.loadingMessage = '';
        
        this.initialize();
    }
    
    initialize() {
        // Listen for orchestrator state changes
        this.orchestrator.on('state:change', (e) => {
            if (e.detail.property === 'isLoading') {
                this.setGlobalLoading(e.detail.value, this.orchestrator.state.loadingMessage);
            }
        });
        
        // Listen for loading events
        this.orchestrator.on('loading:start', (e) => {
            this.startLoading(e.detail.id, e.detail.message);
        });
        
        this.orchestrator.on('loading:stop', (e) => {
            this.stopLoading(e.detail.id);
        });
    }
    
    /**
     * 🚀 Start loading for a specific component
     */
    startLoading(id, message = 'Loading...') {
        this.loadingStates.set(id, { message, startTime: Date.now() });
        
        // Update UI
        this.updateLoadingUI(id, true, message);
        
        // Announce to screen readers
        this.orchestrator.emit('accessibility:announce', { 
            message: `Loading: ${message}` 
        });
    }
    
    /**
     * 🛑 Stop loading for a specific component
     */
    stopLoading(id) {
        const loadingState = this.loadingStates.get(id);
        
        if (loadingState) {
            const duration = Date.now() - loadingState.startTime;
            this.loadingStates.delete(id);
            
            // Update UI
            this.updateLoadingUI(id, false);
            
            // Announce completion
            this.orchestrator.emit('accessibility:announce', { 
                message: `Loading complete` 
            });
            
            // Emit loading completed event
            this.orchestrator.emit('loading:completed', { id, duration });
        }
    }
    
    /**
     * 🌐 Global loading state
     */
    setGlobalLoading(isLoading, message = 'Loading...') {
        this.globalLoading = isLoading;
        this.loadingMessage = message;
        
        this.updateGlobalLoadingUI(isLoading, message);
    }
    
    /**
     * 🎨 Update loading UI for specific component
     */
    updateLoadingUI(id, isLoading, message = '') {
        const element = document.getElementById(id);
        
        if (element) {
            if (isLoading) {
                this.showComponentLoading(element, message);
            } else {
                this.hideComponentLoading(element);
            }
        }
    }
    
    /**
     * 🎨 Show loading state for component
     */
    showComponentLoading(element, message) {
        // Add loading class
        element.classList.add('loading');
        
        // Create or update loading overlay
        let overlay = element.querySelector('.loading-overlay');
        
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.className = 'loading-overlay absolute inset-0 bg-black/50 flex items-center justify-center z-10';
            overlay.innerHTML = `
                <div class="loading-content bg-secondary rounded-lg p-4 flex items-center space-x-3">
                    <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
                    <span class="loading-text text-white text-sm">${message}</span>
                </div>
            `;
            
            // Make parent relative if needed
            if (getComputedStyle(element).position === 'static') {
                element.style.position = 'relative';
            }
            
            element.appendChild(overlay);
        } else {
            overlay.querySelector('.loading-text').textContent = message;
        }
    }
    
    /**
     * 🎨 Hide loading state for component
     */
    hideComponentLoading(element) {
        element.classList.remove('loading');
        
        const overlay = element.querySelector('.loading-overlay');
        if (overlay) {
            overlay.remove();
        }
    }
    
    /**
     * 🌐 Update global loading UI
     */
    updateGlobalLoadingUI(isLoading, message) {
        const indicator = this.getGlobalLoadingIndicator();
        
        if (isLoading) {
            indicator.querySelector('.loading-message').textContent = message;
            indicator.style.display = 'flex';
            
            // Prevent scrolling
            document.body.style.overflow = 'hidden';
        } else {
            indicator.style.display = 'none';
            
            // Restore scrolling
            document.body.style.overflow = '';
        }
    }
    
    /**
     * 🎯 Get or create global loading indicator
     */
    getGlobalLoadingIndicator() {
        let indicator = document.querySelector('.loading-indicator');
        
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.className = 'loading-indicator fixed inset-0 bg-black/50 flex items-center justify-center z-50';
            indicator.style.display = 'none';
            
            indicator.innerHTML = `
                <div class="bg-secondary rounded-lg p-6 flex items-center space-x-4">
                    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                    <div class="text-white">
                        <div class="font-semibold">Loading...</div>
                        <div class="loading-message text-sm text-gray-400"></div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(indicator);
        }
        
        return indicator;
    }
    
    /**
     * 📊 Get loading statistics
     */
    getLoadingStats() {
        return {
            activeLoading: this.loadingStates.size,
            globalLoading: this.globalLoading,
            loadingComponents: Array.from(this.loadingStates.keys())
        };
    }
    
    /**
     * 🎨 Show skeleton loading for lists
     */
    showSkeletonLoading(container, count = 3) {
        container.innerHTML = '';
        
        for (let i = 0; i < count; i++) {
            const skeleton = document.createElement('div');
            skeleton.className = 'skeleton-item bg-gray-800 rounded-lg p-4 mb-4 animate-pulse';
            skeleton.innerHTML = `
                <div class="flex items-center space-x-4">
                    <div class="skeleton-avatar w-12 h-12 bg-gray-700 rounded-full"></div>
                    <div class="flex-1 space-y-2">
                        <div class="skeleton-line h-4 bg-gray-700 rounded w-3/4"></div>
                        <div class="skeleton-line h-3 bg-gray-700 rounded w-1/2"></div>
                    </div>
                </div>
            `;
            
            container.appendChild(skeleton);
        }
    }
    
    /**
     * 🎨 Show progress loading
     */
    showProgressLoading(elementId, progress = 0) {
        const element = document.getElementById(elementId);
        
        if (element) {
            let progressBar = element.querySelector('.progress-bar');
            
            if (!progressBar) {
                progressBar = document.createElement('div');
                progressBar.className = 'progress-bar w-full bg-gray-700 rounded-full h-2';
                progressBar.innerHTML = `
                    <div class="progress-fill bg-primary rounded-full h-2 transition-all duration-300"
                         style="width: ${progress}%"></div>
                `;
                
                element.appendChild(progressBar);
            } else {
                progressBar.querySelector('.progress-fill').style.width = `${progress}%`;
            }
        }
    }
    
    /**
     * 🧹 Cleanup
     */
    destroy() {
        this.loadingStates.clear();
        this.globalLoading = false;
        
        // Remove global loading indicator
        const indicator = document.querySelector('.loading-indicator');
        if (indicator) {
            indicator.remove();
        }
        
        // Restore scrolling
        document.body.style.overflow = '';
    }
}

// 🎯 Export for modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { LoadingService };
}