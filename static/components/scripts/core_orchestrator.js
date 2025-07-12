/**
 * 🎯 CORE ORCHESTRATOR - Single Responsibility: Service registration & communication
 * 
 * SRIMI Principles:
 * - Single Responsibility: ONLY manages service registry and event bus
 * - Reactive: Event-driven communication between services
 * - Injectable: Dependency injection for services
 * - Micro: Minimal - just a service bus
 * - Interfaces: Clear contracts for service interaction
 */
class CoreOrchestrator {
    constructor(pageName, options = {}) {
        this.pageName = pageName;
        this.options = {
            debugMode: false,
            ...options
        };
        
        this.services = new Map();
        this.eventBus = new EventTarget();
        this.state = new Proxy({}, {
            set: (target, prop, value) => {
                this.emit('state:change', { property: prop, value, previous: target[prop] });
                return true;
            }
        });
        
        if (this.options.debugMode) {
            console.log(`🎯 Core orchestrator initialized for ${this.pageName}`);
        }
    }
    
    /**
     * 📝 Register a service
     */
    register(name, service) {
        if (this.services.has(name)) {
            console.warn(`⚠️ Service '${name}' already registered, overwriting`);
        }
        
        this.services.set(name, service);
        
        // Inject orchestrator reference
        if (service && typeof service === 'object') {
            service.orchestrator = this;
        }
        
        this.emit('service:registered', { name, service });
        
        if (this.options.debugMode) {
            console.log(`✅ Service '${name}' registered`);
        }
    }
    
    /**
     * 🔍 Get a service
     */
    get(name) {
        return this.services.get(name);
    }
    
    /**
     * 📡 Event communication
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
     * 🧹 Cleanup
     */
    destroy() {
        this.services.clear();
        this.eventBus.removeEventListener();
        
        if (this.options.debugMode) {
            console.log(`🧹 ${this.pageName} orchestrator destroyed`);
        }
    }
}

// 🚀 Global factory
window.createOrchestrator = function(pageName, options = {}) {
    return new CoreOrchestrator(pageName, options);
};

// 🎯 Export for modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CoreOrchestrator };
}