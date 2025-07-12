/**
 * Babel Frontend Microservices
 * SRIMI-compliant JavaScript services for Babel functionality
 */

// Service Registry for Frontend Dependency Injection
class FrontendServiceRegistry {
    constructor() {
        this.services = new Map();
        this.singletons = new Map();
        this.dependencies = new Map();
    }

    register(name, factory, dependencies = []) {
        this.services.set(name, factory);
        this.dependencies.set(name, dependencies);
    }

    get(name) {
        if (this.singletons.has(name)) {
            return this.singletons.get(name);
        }

        const factory = this.services.get(name);
        if (!factory) {
            throw new Error(`Service not found: ${name}`);
        }

        // Inject dependencies
        const deps = this.dependencies.get(name) || [];
        const injectedDeps = deps.map(dep => this.get(dep));
        
        const instance = new factory(...injectedDeps);
        this.singletons.set(name, instance);
        return instance;
    }

    list() {
        return {
            services: Array.from(this.services.keys()),
            singletons: Array.from(this.singletons.keys())
        };
    }
}

// Global registry
const serviceRegistry = new FrontendServiceRegistry();

// Microservice 1: API Communication Service
class ApiService {
    constructor() {
        this.baseUrl = '';
        this.defaultHeaders = {
            'Content-Type': 'application/json'
        };
    }

    async request(endpoint, options = {}) {
        const config = {
            headers: { ...this.defaultHeaders, ...options.headers },
            ...options
        };

        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, config);
            const data = await response.json();
            return { success: response.ok, data, status: response.status };
        } catch (error) {
            return { success: false, error: error.message, status: 0 };
        }
    }

    // Babel-specific API methods
    async createPost(content, postType) {
        return this.request('/api/babel/posts', {
            method: 'POST',
            body: JSON.stringify({ content, post_type: postType })
        });
    }

    async getTimeline(page = 1, perPage = 20) {
        return this.request(`/api/babel/timeline?page=${page}&per_page=${perPage}`);
    }

    async likePost(postId) {
        return this.request(`/api/babel/posts/${postId}/like`, { method: 'POST' });
    }

    async getComments(postId, page = 1) {
        return this.request(`/api/babel/posts/${postId}/comments?page=${page}`);
    }

    async addComment(postId, content) {
        return this.request(`/api/babel/posts/${postId}/comments`, {
            method: 'POST',
            body: JSON.stringify({ content })
        });
    }
}

// Microservice 2: UI State Management Service
class StateService {
    constructor() {
        this.state = {
            currentPage: 1,
            selectedPostType: 'text',
            posts: [],
            loading: false,
            error: null,
            pagination: null
        };
        this.subscribers = new Map();
    }

    subscribe(key, callback) {
        if (!this.subscribers.has(key)) {
            this.subscribers.set(key, []);
        }
        this.subscribers.get(key).push(callback);
    }

    setState(updates) {
        const oldState = { ...this.state };
        this.state = { ...this.state, ...updates };
        
        // Notify subscribers
        Object.keys(updates).forEach(key => {
            if (this.subscribers.has(key)) {
                this.subscribers.get(key).forEach(callback => {
                    callback(this.state[key], oldState[key]);
                });
            }
        });
    }

    getState(key) {
        return key ? this.state[key] : this.state;
    }
}

// Microservice 3: DOM Manipulation Service
class DomService {
    constructor() {
        this.elements = new Map();
    }

    register(name, selector) {
        const element = document.querySelector(selector);
        if (element) {
            this.elements.set(name, element);
        }
        return element;
    }

    get(name) {
        return this.elements.get(name);
    }

    show(name) {
        const element = this.get(name);
        if (element) element.style.display = 'block';
    }

    hide(name) {
        const element = this.get(name);
        if (element) element.style.display = 'none';
    }

    setText(name, text) {
        const element = this.get(name);
        if (element) element.textContent = text;
    }

    setHtml(name, html) {
        const element = this.get(name);
        if (element) element.innerHTML = html;
    }

    addClass(name, className) {
        const element = this.get(name);
        if (element) element.classList.add(className);
    }

    removeClass(name, className) {
        const element = this.get(name);
        if (element) element.classList.remove(className);
    }

    toggleClass(name, className, force) {
        const element = this.get(name);
        if (element) element.classList.toggle(className, force);
    }
}

// Microservice 4: Event Management Service
class EventService {
    constructor() {
        this.handlers = new Map();
    }

    on(element, event, handler) {
        const key = `${element}-${event}`;
        if (!this.handlers.has(key)) {
            this.handlers.set(key, []);
        }
        this.handlers.get(key).push(handler);
        
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        
        if (element) {
            element.addEventListener(event, handler);
        }
    }

    off(element, event, handler) {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        
        if (element) {
            element.removeEventListener(event, handler);
        }
    }

    emit(eventName, data) {
        const event = new CustomEvent(eventName, { detail: data });
        document.dispatchEvent(event);
    }

    listen(eventName, handler) {
        document.addEventListener(eventName, handler);
    }
}

// Microservice 5: Post Creation Service
class PostCreationService {
    constructor(apiService, stateService, domService, eventService) {
        this.api = apiService;
        this.state = stateService;
        this.dom = domService;
        this.events = eventService;
        this.maxLength = 500;
        this.init();
    }

    init() {
        this.setupElements();
        this.setupEventListeners();
    }

    setupElements() {
        this.dom.register('postContent', '#postContent');
        this.dom.register('charCount', '#charCount');
        this.dom.register('postBtn', '#postBtn');
        this.dom.register('errorDisplay', '#errorDisplay');
    }

    setupEventListeners() {
        // Post type selection
        this.events.on(document, 'click', (e) => {
            if (e.target.classList.contains('post-type-btn')) {
                this.selectPostType(e.target);
            }
        });

        // Character counter
        this.events.on('#postContent', 'input', (e) => {
            this.updateCharCounter(e.target.value.length);
        });

        // Post creation
        this.events.on('#postBtn', 'click', () => {
            this.createPost();
        });
    }

    selectPostType(button) {
        // Remove active class from all buttons
        document.querySelectorAll('.post-type-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        // Add active class to selected button
        button.classList.add('active');
        
        const postType = button.dataset.type;
        this.state.setState({ selectedPostType: postType });
        this.updatePlaceholder(postType);
    }

    updatePlaceholder(postType) {
        const placeholders = {
            'text': "What's happening? Share your thoughts...",
            'looking_for': "What kind of chat partner are you looking for?",
            'topic': "Start a discussion about something interesting...",
            'language': "Want to practice a language or help others?",
            'mood': "How are you feeling today?"
        };
        
        const postContent = this.dom.get('postContent');
        if (postContent) {
            postContent.placeholder = placeholders[postType] || placeholders.text;
        }
    }

    updateCharCounter(count) {
        this.dom.setText('charCount', count.toString());
        
        const isWarning = count > 450;
        this.dom.toggleClass('charCount', 'warning', isWarning);
        
        const postBtn = this.dom.get('postBtn');
        if (postBtn) {
            postBtn.disabled = count === 0 || count > this.maxLength;
        }
    }

    async createPost() {
        const content = this.dom.get('postContent')?.value.trim();
        if (!content) return;

        const postType = this.state.getState('selectedPostType');
        
        try {
            const result = await this.api.createPost(content, postType);
            
            if (result.success) {
                this.clearForm();
                this.hideError();
                this.events.emit('postCreated', result.data);
            } else {
                this.showError(result.data?.error || 'Failed to create post');
            }
        } catch (error) {
            this.showError('Network error. Please try again.');
        }
    }

    clearForm() {
        const postContent = this.dom.get('postContent');
        if (postContent) {
            postContent.value = '';
            this.updateCharCounter(0);
        }
    }

    showError(message) {
        this.dom.setText('errorDisplay', message);
        this.dom.show('errorDisplay');
        setTimeout(() => this.hideError(), 5000);
    }

    hideError() {
        this.dom.hide('errorDisplay');
    }
}

// Microservice 6: Timeline Rendering Service
class TimelineService {
    constructor(apiService, stateService, domService, eventService) {
        this.api = apiService;
        this.state = stateService;
        this.dom = domService;
        this.events = eventService;
        this.init();
    }

    init() {
        this.setupElements();
        this.setupEventListeners();
        this.loadTimeline();
    }

    setupElements() {
        this.dom.register('timelinePosts', '#timelinePosts');
        this.dom.register('loadingState', '#loadingState');
        this.dom.register('emptyState', '#emptyState');
        this.dom.register('pagination', '#pagination');
        this.dom.register('prevBtn', '#prevBtn');
        this.dom.register('nextBtn', '#nextBtn');
        this.dom.register('pageInfo', '#pageInfo');
    }

    setupEventListeners() {
        // Listen for post creation events
        this.events.listen('postCreated', () => {
            this.loadTimeline();
        });

        // Pagination
        this.events.on('#prevBtn', 'click', () => {
            const currentPage = this.state.getState('currentPage');
            if (currentPage > 1) {
                this.state.setState({ currentPage: currentPage - 1 });
                this.loadTimeline();
            }
        });

        this.events.on('#nextBtn', 'click', () => {
            const currentPage = this.state.getState('currentPage');
            this.state.setState({ currentPage: currentPage + 1 });
            this.loadTimeline();
        });
    }

    async loadTimeline() {
        this.showLoading();
        
        const page = this.state.getState('currentPage');
        const result = await this.api.getTimeline(page, 20);
        
        if (result.success) {
            this.state.setState({
                posts: result.data.posts,
                pagination: result.data.pagination,
                loading: false
            });
            this.renderTimeline();
            this.updatePagination(result.data.pagination);
        } else {
            this.state.setState({ 
                error: result.data?.error || 'Failed to load timeline',
                loading: false 
            });
        }
        
        this.hideLoading();
    }

    renderTimeline() {
        const posts = this.state.getState('posts');
        
        if (posts.length === 0) {
            this.dom.show('emptyState');
            this.dom.setHtml('timelinePosts', '');
            return;
        }

        this.dom.hide('emptyState');
        const postsHtml = posts.map(post => this.renderPost(post)).join('');
        this.dom.setHtml('timelinePosts', postsHtml);
    }

    renderPost(post) {
        const timeAgo = this.getTimeAgo(new Date(post.created_at));
        const userInitials = (post.user.display_name || post.user.username).charAt(0).toUpperCase();
        const tags = post.tags ? JSON.parse(post.tags) : [];
        const tagsHtml = tags.map(tag => `<span class="tag">#${tag}</span>`).join('');

        return `
            <div class="timeline-post" data-post-id="${post.id}">
                <div class="post-header">
                    <div class="user-avatar" onclick="babelApp.viewProfile(${post.user.id})">
                        ${userInitials}
                    </div>
                    <div class="user-info">
                        <div class="user-name" onclick="babelApp.viewProfile(${post.user.id})">
                            ${post.user.display_name || post.user.username}
                        </div>
                        <div class="post-meta">
                            @${post.user.username} • ${timeAgo}
                            <span class="post-type-badge">${this.getPostTypeLabel(post.post_type)}</span>
                        </div>
                    </div>
                </div>
                
                <div class="post-content">${this.formatContent(post.content)}</div>
                
                ${tagsHtml ? `<div class="post-tags">${tagsHtml}</div>` : ''}
                
                <div class="post-actions-bar">
                    <button class="action-btn ${post.is_liked ? 'liked' : ''}" onclick="babelApp.toggleLike(${post.id})">
                        ❤️ ${post.likes_count}
                    </button>
                    <button class="action-btn" onclick="babelApp.viewComments(${post.id})">
                        💬 ${post.comments_count}
                    </button>
                    <button class="action-btn chat" onclick="babelApp.startChat(${post.user.id})">
                        🔗 Chat
                    </button>
                    <button class="action-btn room" onclick="babelApp.createRoom(${post.user.id})">
                        📞 Room
                    </button>
                </div>
            </div>
        `;
    }

    getPostTypeLabel(type) {
        const labels = {
            'text': '💬 General',
            'looking_for': '🔍 Looking For',
            'topic': '💡 Topic',
            'language': '🌍 Language',
            'mood': '😊 Mood'
        };
        return labels[type] || '💬 General';
    }

    formatContent(content) {
        return content
            .replace(/#(\w+)/g, '<span class="tag">#$1</span>')
            .replace(/\n/g, '<br>');
    }

    getTimeAgo(date) {
        const now = new Date();
        const diff = now - date;
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (days > 0) return `${days}d`;
        if (hours > 0) return `${hours}h`;
        if (minutes > 0) return `${minutes}m`;
        return 'now';
    }

    updatePagination(pagination) {
        if (pagination.total > pagination.per_page) {
            this.dom.show('pagination');
            
            const prevBtn = this.dom.get('prevBtn');
            const nextBtn = this.dom.get('nextBtn');
            
            if (prevBtn) prevBtn.disabled = !pagination.has_prev;
            if (nextBtn) nextBtn.disabled = !pagination.has_next;
            
            const totalPages = Math.ceil(pagination.total / pagination.per_page);
            this.dom.setText('pageInfo', `Page ${pagination.page} of ${totalPages}`);
        } else {
            this.dom.hide('pagination');
        }
    }

    showLoading() {
        this.dom.show('loadingState');
        this.dom.hide('timelinePosts');
    }

    hideLoading() {
        this.dom.hide('loadingState');
        this.dom.show('timelinePosts');
    }
}

// Microservice 7: Interaction Service
class InteractionService {
    constructor(apiService, stateService, eventService) {
        this.api = apiService;
        this.state = stateService;
        this.events = eventService;
    }

    async toggleLike(postId) {
        try {
            const result = await this.api.likePost(postId);
            
            if (result.success) {
                // Update UI immediately
                const postElement = document.querySelector(`[data-post-id="${postId}"]`);
                if (postElement) {
                    const likeBtn = postElement.querySelector('.action-btn');
                    likeBtn.innerHTML = `❤️ ${result.data.likes_count}`;
                    likeBtn.classList.toggle('liked', result.data.action === 'liked');
                }
            }
        } catch (error) {
            console.error('Failed to toggle like:', error);
        }
    }

    viewProfile(userId) {
        window.location.href = `/api/profile/${userId}`;
    }

    startChat(userId) {
        window.location.href = `/chat?user=${userId}`;
    }

    createRoom(userId) {
        alert('Room creation feature coming soon!');
    }

    viewComments(postId) {
        alert('Comments feature coming soon!');
    }
}

// Main Application Service (Orchestrator)
class BabelApplication {
    constructor() {
        this.services = {};
        this.init();
    }

    init() {
        // Register all microservices
        serviceRegistry.register('apiService', ApiService);
        serviceRegistry.register('stateService', StateService);
        serviceRegistry.register('domService', DomService);
        serviceRegistry.register('eventService', EventService);
        serviceRegistry.register('postCreationService', PostCreationService, 
            ['apiService', 'stateService', 'domService', 'eventService']);
        serviceRegistry.register('timelineService', TimelineService,
            ['apiService', 'stateService', 'domService', 'eventService']);
        serviceRegistry.register('interactionService', InteractionService,
            ['apiService', 'stateService', 'eventService']);

        // Get service instances
        this.services.api = serviceRegistry.get('apiService');
        this.services.state = serviceRegistry.get('stateService');
        this.services.dom = serviceRegistry.get('domService');
        this.services.events = serviceRegistry.get('eventService');
        this.services.postCreation = serviceRegistry.get('postCreationService');
        this.services.timeline = serviceRegistry.get('timelineService');
        this.services.interaction = serviceRegistry.get('interactionService');

        console.log('Babel microservices initialized:', serviceRegistry.list());
    }

    // Delegate methods to appropriate services
    toggleLike(postId) {
        return this.services.interaction.toggleLike(postId);
    }

    viewProfile(userId) {
        return this.services.interaction.viewProfile(userId);
    }

    startChat(userId) {
        return this.services.interaction.startChat(userId);
    }

    createRoom(userId) {
        return this.services.interaction.createRoom(userId);
    }

    viewComments(postId) {
        return this.services.interaction.viewComments(postId);
    }
}

// Global application instance
window.babelApp = new BabelApplication();