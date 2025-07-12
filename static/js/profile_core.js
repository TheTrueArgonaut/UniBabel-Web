// 🎯 PROFILE CORE MICROSERVICE
// SRIMI Compliant: Single Responsibility - Profile state management

class ProfileCore {
    constructor() {
        this.state = {
            user: {},
            posts: [],
            isLoading: false,
            error: null,
            privacy: { isPublic: false }
        };
        
        this.init();
    }
    
    init() {
        console.log('🎯 Profile Core initialized');
        this.attachEventListeners();
        this.loadUserData();
    }
    
    attachEventListeners() {
        // Babel post submission
        const babelBtn = document.querySelector('.babel-btn');
        if (babelBtn) {
            babelBtn.addEventListener('click', () => {
                this.handleBabelPost();
            });
        }
        
        // Room navigation
        document.querySelectorAll('.room-item').forEach(item => {
            item.addEventListener('click', () => {
                this.handleRoomNavigation(item);
            });
        });
    }
    
    async loadUserData() {
        this.setState({ isLoading: true });
        
        try {
            await Promise.all([
                this.loadUserProfile(),
                this.loadUserPosts()
            ]);
        } catch (error) {
            console.error('Error loading user data:', error);
            this.setState({ error: 'Failed to load profile data' });
        } finally {
            this.setState({ isLoading: false });
        }
    }
    
    async loadUserProfile() {
        try {
            const response = await fetch('/api/profile/me');
            const userData = await response.json();
            
            if (userData.success) {
                this.setState({ 
                    user: userData.user,
                    privacy: { isPublic: userData.user.is_discoverable }
                });
            }
        } catch (error) {
            console.error('Error loading profile:', error);
        }
    }
    
    async loadUserPosts() {
        try {
            const response = await fetch('/api/profile/posts');
            const postsData = await response.json();
            
            if (postsData.success) {
                this.setState({ posts: postsData.posts });
                this.displayPosts(postsData.posts);
            }
        } catch (error) {
            console.error('Error loading posts:', error);
        }
    }
    
    async handleBabelPost() {
        const input = document.querySelector('.babel-input');
        const content = input?.value?.trim();
        
        if (!content) return;
        
        this.setState({ isLoading: true });
        
        try {
            const response = await fetch('/babel/post', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content })
            });
            
            const result = await response.json();
            
            if (result.success) {
                input.value = '';
                await this.loadUserPosts();
                this.showSuccess('Post shared successfully!');
            } else {
                this.showError(result.error || 'Failed to post');
            }
        } catch (error) {
            console.error('Error posting babel:', error);
            this.showError('Network error. Please try again.');
        } finally {
            this.setState({ isLoading: false });
        }
    }
    
    handleRoomNavigation(roomElement) {
        const roomName = roomElement.querySelector('.room-name')?.textContent;
        const sectionTitle = roomElement.closest('.rooms-section')?.querySelector('.section-title')?.textContent;
        
        if (!roomName) return;
        
        const isPrivateChat = sectionTitle?.includes('Private');
        const targetUrl = isPrivateChat ? `/chat/${roomName}` : `/rooms/${roomName}`;
        
        roomElement.style.transform = 'scale(0.95)';
        setTimeout(() => {
            window.location.href = targetUrl;
        }, 150);
    }
    
    setState(newState) {
        this.state = { ...this.state, ...newState };
        this.updateUI();
    }
    
    updateUI() {
        const babelBtn = document.querySelector('.babel-btn');
        if (babelBtn) {
            babelBtn.disabled = this.state.isLoading;
            babelBtn.textContent = this.state.isLoading ? 'Posting...' : 'Babel It!';
        }
    }
    
    displayPosts(posts) {
        const container = document.getElementById('babelPosts');
        if (!container) return;
        
        if (posts.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📝</div>
                    <p class="empty-title">No posts yet!</p>
                    <p class="empty-subtitle">Share your first thought to get started.</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = posts.map(post => `
            <div class="babel-post">
                <div class="post-header">
                    <div class="post-avatar">${post.author[0]}</div>
                    <div class="post-name">${post.author}</div>
                    <div class="post-time">${this.formatTime(post.created_at)}</div>
                </div>
                <div class="post-content">${post.content}</div>
                <div class="post-actions">
                    <button class="post-action">👍 Like</button>
                    <button class="post-action">💬 Comment</button>
                    <button class="post-action">🔄 Share</button>
                </div>
            </div>
        `).join('');
    }
    
    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) return 'Just now';
        if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
        return date.toLocaleDateString();
    }
    
    showError(message) {
        console.error('Profile Error:', message);
    }
    
    showSuccess(message) {
        console.log('Profile Success:', message);
    }
}

// Global privacy toggle function
window.togglePrivacy = function(element) {
    element.classList.toggle('active');
    if (window.profileCore) {
        window.profileCore.handlePrivacyToggle(element);
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.profileCore = new ProfileCore();
});

window.profileCore = window.profileCore || null;