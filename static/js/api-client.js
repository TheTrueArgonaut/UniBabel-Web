/**
 * UniBabel API Client - Microservice Architecture
 * Unified client for all backend services
 */

class UniBabelAPI {
    constructor() {
        this.baseURL = '/api/v1';
        this.authToken = this.getAuthToken();
        
        // Initialize service clients
        this.users = new UserService(this);
        this.chats = new ChatService(this);
        this.friends = new FriendsService(this);
        this.translation = new TranslationService(this);
        this.activity = new ActivityService(this);
        
        console.log('🚀 UniBabel API Client initialized');
    }

    // Core HTTP methods
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...this.getAuthHeaders(),
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new APIError(response.status, await response.text());
            }
            
            return await response.json();
        } catch (error) {
            console.error(`API Request failed: ${endpoint}`, error);
            throw error;
        }
    }

    async get(endpoint, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;
        return this.request(url, { method: 'GET' });
    }

    async post(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async put(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }

    // Authentication helpers
    getAuthToken() {
        return localStorage.getItem('unibabel_token') || null;
    }

    setAuthToken(token) {
        this.authToken = token;
        localStorage.setItem('unibabel_token', token);
    }

    getAuthHeaders() {
        return this.authToken ? { 'Authorization': `Bearer ${this.authToken}` } : {};
    }

    clearAuth() {
        this.authToken = null;
        localStorage.removeItem('unibabel_token');
    }
}

// Friends Service
class FriendsService {
    constructor(apiClient) {
        this.api = apiClient;
    }

    async getFriends() {
        return this.api.get('/friends');
    }

    async addFriend(username) {
        return this.api.post('/friends/add', { username });
    }

    async removeFriend(friendId) {
        return this.api.delete(`/friends/${friendId}`);
    }

    async searchUsers(query) {
        return this.api.get('/friends/search', { q: query });
    }

    async getFriendStatus(friendId) {
        return this.api.get(`/friends/${friendId}/status`);
    }

    async updateFriendStatus(status) {
        return this.api.post('/friends/status', { status });
    }
}

// Chat Service
class ChatService {
    constructor(apiClient) {
        this.api = apiClient;
    }

    async getActiveChats() {
        return this.api.get('/chats/active');
    }

    async joinChat(chatId) {
        return this.api.post(`/chats/${chatId}/join`);
    }

    async leaveChat(chatId) {
        return this.api.post(`/chats/${chatId}/leave`);
    }

    async getChatHistory(chatId, limit = 50) {
        return this.api.get(`/chats/${chatId}/messages`, { limit });
    }

    async sendMessage(chatId, message) {
        return this.api.post(`/chats/${chatId}/messages`, { message });
    }

    async createChat(name, participants = []) {
        return this.api.post('/chats', { name, participants });
    }
}

// User Service
class UserService {
    constructor(apiClient) {
        this.api = apiClient;
    }

    async getProfile() {
        return this.api.get('/users/profile');
    }

    async updateProfile(data) {
        return this.api.put('/users/profile', data);
    }

    async getPreferences() {
        return this.api.get('/users/preferences');
    }

    async updatePreferences(preferences) {
        return this.api.put('/users/preferences', preferences);
    }

    async uploadAvatar(file) {
        const formData = new FormData();
        formData.append('avatar', file);
        
        return this.api.request('/users/avatar', {
            method: 'POST',
            body: formData,
            headers: {} // Let browser set Content-Type for FormData
        });
    }
}

// Translation Service
class TranslationService {
    constructor(apiClient) {
        this.api = apiClient;
    }

    async translateText(text, targetLanguage, sourceLanguage = 'auto') {
        return this.api.post('/translation/translate', {
            text,
            target_language: targetLanguage,
            source_language: sourceLanguage
        });
    }

    async getLanguages() {
        return this.api.get('/translation/languages');
    }

    async submitTranslationFix(originalText, suggestedTranslation, targetLanguage) {
        return this.api.post('/translation/submit-fix', {
            original_text: originalText,
            suggested_translation: suggestedTranslation,
            target_language: targetLanguage
        });
    }
}

// Activity Service
class ActivityService {
    constructor(apiClient) {
        this.api = apiClient;
    }

    async getRecentActivity() {
        return this.api.get('/activity/recent');
    }

    async getUserActivity(userId) {
        return this.api.get(`/activity/user/${userId}`);
    }

    async markActivityRead(activityId) {
        return this.api.post(`/activity/${activityId}/read`);
    }
}

// Custom Error Class
class APIError extends Error {
    constructor(status, message) {
        super(message);
        this.name = 'APIError';
        this.status = status;
    }
}

// Global API client instance
const api = new UniBabelAPI();

// Export for modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { UniBabelAPI, api };
}

// Global access
window.UniBabelAPI = UniBabelAPI;
window.api = api;