// 🎯 BABEL CORE MICROSERVICE
// SRIMI Compliant: Single Responsibility - Core state management

class BabelCore {
    constructor() {
        this.state = {
            currentPostType: 'text',
            posts: [],
            loading: false,
            error: null
        };
        this.init();
    }
    
    init() {
        console.log('🎯 Babel Core initialized');
        this.attachEventListeners();
    }
    
    attachEventListeners() {
        // Post type selection
        document.querySelectorAll('.post-type-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.handlePostTypeChange(e.target.dataset.type);
            });
        });
        
        // Character counter
        const postContent = document.getElementById('postContent');
        if (postContent) {
            postContent.addEventListener('input', () => {
                this.updateCharacterCounter();
            });
        }
        
        // Post button
        const postBtn = document.getElementById('postBtn');
        if (postBtn) {
            postBtn.addEventListener('click', () => {
                this.handlePostSubmit();
            });
        }
    }
    
    handlePostTypeChange(type) {
        document.querySelectorAll('.post-type-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-type="${type}"]`)?.classList.add('active');
        this.state.currentPostType = type;
    }
    
    updateCharacterCounter() {
        const input = document.getElementById('postContent');
        const counter = document.getElementById('charCount');
        
        if (!input || !counter) return;
        
        const length = input.value.length;
        counter.textContent = length;
        counter.parentElement.classList.toggle('warning', length > 450);
    }
    
    async handlePostSubmit() {
        const content = document.getElementById('postContent')?.value?.trim();
        if (!content) return;
        
        this.state.loading = true;
        
        try {
            console.log('Creating post:', { content, type: this.state.currentPostType });
            document.getElementById('postContent').value = '';
            this.updateCharacterCounter();
        } catch (error) {
            console.error('Error creating post:', error);
            this.state.error = 'Failed to create post. Please try again.';
        } finally {
            this.state.loading = false;
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.babelCore = new BabelCore();
});

window.babelCore = window.babelCore || null;