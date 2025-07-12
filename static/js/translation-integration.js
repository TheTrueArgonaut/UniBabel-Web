/**
 * Translation Integration - Connects chat interface with translation orchestrator
 * Integrates with your enterprise-grade translation pipeline
 */

class TranslationIntegration {
    constructor() {
        this.userPreferences = null;
        this.translationCache = new Map();
        this.pendingTranslations = new Set();
        this.translationHistory = [];
        
        console.log('🌍 Translation Integration initialized');
        this.loadUserPreferences();
    }

    async loadUserPreferences() {
        try {
            const response = await api.users.getPreferences();
            if (response.success) {
                this.userPreferences = response.preferences.language || {
                    preferred: 'en',
                    autoTranslate: true,
                    showOriginal: false
                };
                console.log('🌍 User translation preferences loaded:', this.userPreferences);
            }
        } catch (error) {
            console.error('Failed to load translation preferences:', error);
            // Default preferences
            this.userPreferences = {
                preferred: 'en',
                autoTranslate: true,
                showOriginal: false
            };
        }
    }

    async translateMessage(messageId, originalText, targetLanguage = null) {
        if (!this.userPreferences?.autoTranslate) {
            console.log('🌍 Auto-translate disabled, skipping translation');
            return null;
        }

        const target = targetLanguage || this.userPreferences.preferred || 'en';
        const cacheKey = `${originalText}:${target}`;

        // Check cache first
        if (this.translationCache.has(cacheKey)) {
            const cached = this.translationCache.get(cacheKey);
            console.log('🌍 Using cached translation');
            return cached;
        }

        // Avoid duplicate requests
        if (this.pendingTranslations.has(cacheKey)) {
            console.log('🌍 Translation already pending');
            return null;
        }

        this.pendingTranslations.add(cacheKey);

        try {
            console.log('🌍 Requesting translation:', originalText.substring(0, 50) + '...');
            
            const response = await api.translation.translateText(originalText, target);
            
            if (response.success && response.translation) {
                const translationData = {
                    original: originalText,
                    translated: response.translation,
                    targetLanguage: target,
                    confidence: response.confidence || 0.8,
                    cached: response.cached || false,
                    timestamp: new Date().toISOString()
                };

                // Cache the translation
                this.translationCache.set(cacheKey, translationData);
                
                // Add to history
                this.translationHistory.push({
                    messageId,
                    ...translationData
                });

                console.log('🌍 Translation completed:', translationData.translated.substring(0, 50) + '...');
                return translationData;
            } else {
                throw new Error(response.error || 'Translation failed');
            }

        } catch (error) {
            console.error('🌍 Translation error:', error);
            return null;
        } finally {
            this.pendingTranslations.delete(cacheKey);
        }
    }

    async translateAndUpdateMessage(messageElement, originalText) {
        const messageId = messageElement.dataset.messageId;
        const translation = await this.translateMessage(messageId, originalText);
        
        if (translation) {
            this.updateMessageWithTranslation(messageElement, translation);
        }
    }

    updateMessageWithTranslation(messageElement, translationData) {
        const contentDiv = messageElement.querySelector('.message-content');
        if (!contentDiv) return;

        const originalText = translationData.original;
        const translatedText = translationData.translated;

        // Create translation UI
        const translationContainer = document.createElement('div');
        translationContainer.className = 'translation-container mt-2';
        
        translationContainer.innerHTML = `
            <div class="translation-content bg-blue-900/20 rounded-lg p-3 border-l-4 border-blue-400">
                <div class="flex items-center justify-between mb-2">
                    <div class="flex items-center gap-2">
                        <i class="ri-translate-2 text-blue-400 text-sm"></i>
                        <span class="text-blue-400 text-xs font-medium">
                            Translated to ${this.getLanguageName(translationData.targetLanguage)}
                        </span>
                        <span class="text-gray-500 text-xs">
                            ${translationData.cached ? '(cached)' : '(live)'}
                        </span>
                    </div>
                    <div class="flex items-center gap-1">
                        <button class="toggle-original-btn text-gray-400 hover:text-white text-xs" 
                                onclick="translationIntegration.toggleOriginal(this)">
                            Show Original
                        </button>
                        <button class="translation-settings-btn text-gray-400 hover:text-white" 
                                onclick="translationIntegration.openTranslationSettings()" 
                                title="Translation settings">
                            <i class="ri-settings-3-line text-xs"></i>
                        </button>
                    </div>
                </div>
                <div class="translated-text text-gray-200">${translatedText}</div>
                <div class="original-text text-gray-400 text-sm mt-2 hidden">${originalText}</div>
            </div>
        `;

        // Remove existing translation if any
        const existingTranslation = messageElement.querySelector('.translation-container');
        if (existingTranslation) {
            existingTranslation.remove();
        }

        // Add new translation
        contentDiv.appendChild(translationContainer);

        // Add confidence indicator
        this.addConfidenceIndicator(translationContainer, translationData.confidence);
    }

    addConfidenceIndicator(container, confidence) {
        const indicator = document.createElement('div');
        indicator.className = 'confidence-indicator flex items-center gap-1 mt-1';
        
        const color = confidence > 0.9 ? 'green' : confidence > 0.7 ? 'yellow' : 'red';
        const dots = Math.round(confidence * 5);
        
        indicator.innerHTML = `
            <span class="text-xs text-gray-500">Quality:</span>
            ${Array(5).fill(0).map((_, i) => 
                `<div class="w-1 h-1 rounded-full ${i < dots ? `bg-${color}-400` : 'bg-gray-600'}"></div>`
            ).join('')}
        `;
        
        container.appendChild(indicator);
    }

    toggleOriginal(button) {
        const container = button.closest('.translation-container');
        const originalDiv = container.querySelector('.original-text');
        const isVisible = !originalDiv.classList.contains('hidden');
        
        if (isVisible) {
            originalDiv.classList.add('hidden');
            button.textContent = 'Show Original';
        } else {
            originalDiv.classList.remove('hidden');
            button.textContent = 'Hide Original';
        }
    }

    async openTranslationSettings() {
        // Create translation settings modal
        const modal = document.createElement('div');
        modal.id = 'translation-settings-modal';
        modal.className = 'fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50';
        modal.innerHTML = this.createTranslationSettingsHTML();
        
        document.body.appendChild(modal);
        
        // Load current settings
        this.populateSettingsForm();
    }

    createTranslationSettingsHTML() {
        return `
            <div class="bg-gray-800 rounded-xl max-w-md w-full mx-4 border border-gray-700">
                <div class="flex items-center justify-between p-4 border-b border-gray-700">
                    <h3 class="text-lg font-bold text-white">Translation Settings</h3>
                    <button onclick="translationIntegration.closeTranslationSettings()" 
                            class="text-gray-400 hover:text-white">
                        <i class="ri-close-line text-xl"></i>
                    </button>
                </div>
                
                <div class="p-4 space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-300 mb-2">
                            Preferred Language
                        </label>
                        <select id="preferred-language" 
                                class="w-full bg-gray-900 text-white rounded-lg px-3 py-2 border border-gray-600 focus:border-blue-500/50 focus:outline-none">
                            <option value="en">English</option>
                            <option value="es">Spanish</option>
                            <option value="fr">French</option>
                            <option value="de">German</option>
                            <option value="it">Italian</option>
                            <option value="pt">Portuguese</option>
                            <option value="ru">Russian</option>
                            <option value="zh">Chinese</option>
                            <option value="ja">Japanese</option>
                            <option value="ko">Korean</option>
                            <option value="ar">Arabic</option>
                        </select>
                    </div>
                    
                    <div class="space-y-3">
                        <label class="flex items-center gap-3">
                            <input type="checkbox" id="auto-translate" 
                                   class="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500">
                            <div>
                                <div class="text-white font-medium">Auto-translate messages</div>
                                <div class="text-gray-400 text-sm">Automatically translate incoming messages</div>
                            </div>
                        </label>
                        
                        <label class="flex items-center gap-3">
                            <input type="checkbox" id="show-original" 
                                   class="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500">
                            <div>
                                <div class="text-white font-medium">Show original text</div>
                                <div class="text-gray-400 text-sm">Display original message alongside translation</div>
                            </div>
                        </label>
                    </div>
                    
                    <div class="flex gap-3 pt-4 border-t border-gray-700">
                        <button onclick="translationIntegration.closeTranslationSettings()" 
                                class="flex-1 bg-gray-700 text-white py-2 rounded-lg hover:bg-gray-600 transition-colors">
                            Cancel
                        </button>
                        <button onclick="translationIntegration.saveTranslationSettings()" 
                                class="flex-1 bg-blue-500 text-white py-2 rounded-lg hover:bg-blue-600 transition-colors">
                            Save Settings
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    populateSettingsForm() {
        if (!this.userPreferences) return;

        const preferredLang = document.getElementById('preferred-language');
        const autoTranslate = document.getElementById('auto-translate');
        const showOriginal = document.getElementById('show-original');

        if (preferredLang) preferredLang.value = this.userPreferences.preferred || 'en';
        if (autoTranslate) autoTranslate.checked = this.userPreferences.autoTranslate !== false;
        if (showOriginal) showOriginal.checked = this.userPreferences.showOriginal === true;
    }

    async saveTranslationSettings() {
        const preferredLang = document.getElementById('preferred-language')?.value;
        const autoTranslate = document.getElementById('auto-translate')?.checked;
        const showOriginal = document.getElementById('show-original')?.checked;

        const newPreferences = {
            ...this.userPreferences,
            preferred: preferredLang,
            autoTranslate: autoTranslate,
            showOriginal: showOriginal
        };

        try {
            const response = await api.users.updatePreferences({
                language: newPreferences
            });

            if (response.success) {
                this.userPreferences = newPreferences;
                this.closeTranslationSettings();
                
                // Show success message
                this.showNotification('Translation settings saved!', 'success');
                
                // Clear cache to force retranslation with new settings
                this.translationCache.clear();
            } else {
                throw new Error(response.error || 'Failed to save settings');
            }
        } catch (error) {
            console.error('Failed to save translation settings:', error);
            this.showNotification('Failed to save settings', 'error');
        }
    }

    closeTranslationSettings() {
        const modal = document.getElementById('translation-settings-modal');
        if (modal) {
            modal.remove();
        }
    }

    getLanguageName(code) {
        const languages = {
            'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German',
            'it': 'Italian', 'pt': 'Portuguese', 'ru': 'Russian', 'zh': 'Chinese',
            'ja': 'Japanese', 'ko': 'Korean', 'ar': 'Arabic'
        };
        return languages[code] || code.toUpperCase();
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg transition-all duration-300 ${
            type === 'success' ? 'bg-green-600' : 
            type === 'error' ? 'bg-red-600' : 'bg-blue-600'
        } text-white`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    // Integration with chat interface
    async processIncomingMessage(messageElement, messageData) {
        if (!this.userPreferences?.autoTranslate) return;
        
        const messageContent = messageData.content;
        const senderId = messageData.sender.id;
        
        // Don't translate own messages
        if (senderId === window.currentUserId) return;
        
        // Add message content class for easier selection
        const contentDiv = messageElement.querySelector('.text-gray-300');
        if (contentDiv) {
            contentDiv.classList.add('message-content');
            
            // Translate the message
            await this.translateAndUpdateMessage(messageElement, messageContent);
        }
    }

    // Get translation statistics
    getTranslationStats() {
        return {
            totalTranslations: this.translationHistory.length,
            cacheHitRate: this.translationCache.size > 0 ? 
                (this.translationHistory.filter(t => t.cached).length / this.translationHistory.length) * 100 : 0,
            averageConfidence: this.translationHistory.length > 0 ?
                this.translationHistory.reduce((sum, t) => sum + t.confidence, 0) / this.translationHistory.length : 0,
            languagesUsed: [...new Set(this.translationHistory.map(t => t.targetLanguage))]
        };
    }
}

// Global translation integration instance
const translationIntegration = new TranslationIntegration();

// Export for global access
window.translationIntegration = translationIntegration;