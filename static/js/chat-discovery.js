// Chat Discovery JavaScript - YouTube-style search for chat rooms

// Function to open Chat Discovery pop-out (YouTube-style search)
function openChatDiscovery() {
    console.log('🔍 Opening Chat Discovery...');
    
    // Prevent duplicate modal
    if (document.getElementById('chat-discovery-modal')) return;

    // Create chat discovery modal
    const modal = document.createElement('div');
    modal.id = 'chat-discovery-modal';
    modal.className = 'fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50';
    modal.innerHTML = createDiscoveryModalHTML();
    
    document.body.appendChild(modal);
    
    // Focus search input
    document.getElementById('chatDiscoverySearch').focus();

    // Keyboard accessibility: ESC to close
    modal.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') {
        closeChatDiscovery();
      }
    });
}

function createDiscoveryModalHTML() {
    return `
        <div class="bg-gray-800 rounded-xl max-w-6xl w-full mx-4 h-[700px] flex flex-col">
            <!-- Header -->
            <div class="flex items-center justify-between p-4 border-b border-gray-700">
                <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center border border-primary/50">
                        <i class="ri-search-2-line text-xl text-primary"></i>
                    </div>
                    <div>
                        <h3 class="text-xl font-bold text-white">🔍 Chat Discovery</h3>
                        <p class="text-sm text-gray-400">Find your perfect chat community with smart search</p>
                    </div>
                </div>
                <div class="flex items-center gap-2">
                    <button onclick="popOutChatDiscovery()" 
                            class="text-gray-400 hover:text-white transition-colors bg-gray-700 hover:bg-gray-600 px-3 py-1 rounded-lg text-sm"
                            title="Pop out to new window">
                        <i class="ri-external-link-line"></i> Pop Out
                    </button>
                    <button onclick="closeChatDiscovery()" class="text-gray-400 hover:text-white">
                        <i class="ri-close-line text-xl"></i>
                    </button>
                </div>
            </div>
            
            <!-- Search Section -->
            <div class="p-4 border-b border-gray-700 bg-gray-900/30">
                <div class="relative mb-4">
                    <i class="ri-search-line absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
                    <input
                        type="text"
                        id="chatDiscoverySearch"
                        class="w-full bg-gray-800 text-white rounded-xl pl-12 pr-4 py-3 border border-gray-700 focus:border-primary/50 focus:outline-none"
                        placeholder="Search for gaming, language exchange, music, coding, travel... anything!"
                        autocomplete="off"
                        onkeyup="performChatSearch()"
                    >
                </div>
                
                <!-- Smart Suggestions -->
                <div class="flex flex-wrap gap-2" id="chatSuggestions">
                    <button class="suggestion-tag" onclick="searchForChat('gaming')">🎮 Gaming</button>
                    <button class="suggestion-tag" onclick="searchForChat('language exchange')">🌍 Language Exchange</button>
                    <button class="suggestion-tag" onclick="searchForChat('music')">🎵 Music</button>
                    <button class="suggestion-tag" onclick="searchForChat('coding')">💻 Coding</button>
                    <button class="suggestion-tag" onclick="searchForChat('travel')">✈️ Travel</button>
                    <button class="suggestion-tag" onclick="searchForChat('art')">🎨 Art</button>
                    <button class="suggestion-tag" onclick="searchForChat('fitness')">💪 Fitness</button>
                    <button class="suggestion-tag" onclick="searchForChat('movies')">🎬 Movies</button>
                    <button class="suggestion-tag" onclick="searchForChat('books')">📚 Books</button>
                    <button class="suggestion-tag" onclick="searchForChat('food')">🍕 Food</button>
                </div>
            </div>
            
            <!-- Results Section -->
            <div class="flex-1 overflow-y-auto p-4 bg-gray-900/20">
                <!-- Welcome State -->
                <div id="discoveryWelcome" class="text-center py-12">
                    <div class="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4">
                        <i class="ri-compass-3-line text-3xl text-primary"></i>
                    </div>
                    <h3 class="text-xl font-bold text-white mb-2">Discover Your Perfect Chat!</h3>
                    <p class="text-gray-400 max-w-md mx-auto mb-6">
                        Search for any topic, hobby, or interest. We'll find the perfect chat communities for you.
                    </p>
                    
                    <!-- Popular Categories -->
                    <div class="grid grid-cols-2 md:grid-cols-3 gap-4 mt-8 max-w-3xl mx-auto">
                        <div class="discovery-category-card" onclick="searchForChat('gaming communities')">
                            <i class="ri-gamepad-line text-2xl text-green-400 mb-2"></i>
                            <h4 class="font-bold text-white">Gaming</h4>
                            <p class="text-gray-400 text-sm">Join gaming communities</p>
                        </div>
                        <div class="discovery-category-card" onclick="searchForChat('language learning')">
                            <i class="ri-global-line text-2xl text-blue-400 mb-2"></i>
                            <h4 class="font-bold text-white">Language Exchange</h4>
                            <p class="text-gray-400 text-sm">Practice with native speakers</p>
                        </div>
                        <div class="discovery-category-card" onclick="searchForChat('music discussion')">
                            <i class="ri-music-line text-2xl text-purple-400 mb-2"></i>
                            <h4 class="font-bold text-white">Music</h4>
                            <p class="text-gray-400 text-sm">Discuss your favorite artists</p>
                        </div>
                        <div class="discovery-category-card" onclick="searchForChat('programming help')">
                            <i class="ri-code-line text-2xl text-yellow-400 mb-2"></i>
                            <h4 class="font-bold text-white">Coding</h4>
                            <p class="text-gray-400 text-sm">Learn and share code</p>
                        </div>
                        <div class="discovery-category-card" onclick="searchForChat('travel stories')">
                            <i class="ri-plane-line text-2xl text-red-400 mb-2"></i>
                            <h4 class="font-bold text-white">Travel</h4>
                            <p class="text-gray-400 text-sm">Share adventures</p>
                        </div>
                        <div class="discovery-category-card" onclick="searchForChat('random chat')">
                            <i class="ri-question-mark text-2xl text-pink-400 mb-2"></i>
                            <h4 class="font-bold text-white">Random</h4>
                            <p class="text-gray-400 text-sm">Meet someone new</p>
                        </div>
                    </div>
                </div>
                
                <!-- Loading State -->
                <div id="discoveryLoading" class="text-center py-8 hidden">
                    <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                    <p class="text-gray-400 mt-2">Finding perfect matches...</p>
                </div>
                
                <!-- Search Results -->
                <div id="discoveryResults" class="hidden">
                    <div class="flex items-center justify-between mb-6">
                        <h4 class="text-lg font-bold text-white">Search Results</h4>
                        <button onclick="clearChatSearch()" class="text-gray-400 hover:text-white text-sm">
                            <i class="ri-close-line"></i> Clear
                        </button>
                    </div>
                    <div id="discoveryResultsList" class="space-y-4"></div>
                </div>
                
                <!-- No Results -->
                <div id="discoveryNoResults" class="text-center py-12 hidden">
                    <div class="w-16 h-16 rounded-full bg-gray-800 flex items-center justify-center mx-auto mb-4">
                        <i class="ri-search-line text-2xl text-gray-400"></i>
                    </div>
                    <h3 class="text-lg font-bold text-white mb-2">No matches found</h3>
                    <p class="text-gray-400 mb-4">Try different keywords or create your own room!</p>
                    <button class="bg-primary text-white px-6 py-2 rounded-lg hover:bg-red-700 transition-colors">
                        Create New Room
                    </button>
                </div>
            </div>
        </div>
    `;
}

// Chat discovery search functionality
function searchForChat(query) {
    document.getElementById('chatDiscoverySearch').value = query;
    performChatSearch();
}

let searchTimeout;
function performChatSearch() {
    clearTimeout(searchTimeout);
    const query = document.getElementById('chatDiscoverySearch').value.trim();
    
    if (!query) {
        showDiscoveryState('welcome');
        return;
    }
    
    // Show loading
    showDiscoveryState('loading');
    
    // Debounce search
    searchTimeout = setTimeout(() => {
        // Mock search results based on query
        const mockResults = generateChatSearchResults(query);
        
        if (mockResults.length === 0) {
            showDiscoveryState('no-results');
        } else {
            displayChatSearchResults(mockResults);
            showDiscoveryState('results');
        }
    }, 300);
}

function generateChatSearchResults(query) {
    const mockChats = [
        { id: 1, name: 'Gaming Central Hub', topic: 'gaming', participants: 1247, tags: ['gaming', 'pc', 'console', 'mobile'], description: 'The ultimate gaming community for all platforms! Discuss latest releases, share tips, and find gaming buddies.', language: 'EN', activity: 'Very Active', preview: 'Join us for the latest gaming discussions...' },
        { id: 2, name: 'Language Exchange Lounge', topic: 'language exchange', participants: 892, tags: ['language', 'learning', 'practice', 'culture'], description: 'Practice languages with native speakers from around the world. All levels welcome!', language: 'Multi', activity: 'Active', preview: 'Hola! Want to practice Spanish with me?' },
        { id: 3, name: 'Music Discovery Zone', topic: 'music', participants: 634, tags: ['music', 'artists', 'genres', 'discovery'], description: 'Discover new music, share your favorite tracks, and discuss artists with fellow music lovers.', language: 'EN', activity: 'Active', preview: 'Check out this amazing indie band I found...' },
        { id: 4, name: 'Travel Adventures', topic: 'travel', participants: 456, tags: ['travel', 'adventure', 'culture', 'tips'], description: 'Share travel stories, get recommendations, and plan your next adventure with fellow travelers.', language: 'Multi', activity: 'Moderate', preview: 'Just got back from Japan, AMA!' },
        { id: 5, name: 'Coding Bootcamp', topic: 'coding', participants: 789, tags: ['programming', 'coding', 'development', 'help'], description: 'Learn to code, share projects, and get help with programming challenges. All languages welcome!', language: 'EN', activity: 'Very Active', preview: 'Need help with this React component...' }
    ];
    
    return mockChats.filter(chat =>
        chat.name.toLowerCase().includes(query.toLowerCase()) ||
        chat.topic.toLowerCase().includes(query.toLowerCase()) ||
        chat.tags.some(tag => tag.toLowerCase().includes(query.toLowerCase())) ||
        chat.description.toLowerCase().includes(query.toLowerCase())
    );
}

function displayChatSearchResults(results) {
    const resultsContainer = document.getElementById('discoveryResultsList');
    resultsContainer.innerHTML = '';
    
    results.forEach(chat => {
        const chatElement = document.createElement('div');
        chatElement.className = 'chat-result-card';
        chatElement.innerHTML = `
            <div class="flex items-start gap-4">
                <div class="w-16 h-16 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
                    <i class="ri-chat-3-line text-primary text-2xl"></i>
                </div>
                <div class="flex-1">
                    <div class="flex items-center gap-2 mb-2">
                        <h5 class="font-bold text-white text-lg">${chat.name}</h5>
                        <span class="text-xs px-2 py-1 rounded-full bg-green-500/20 text-green-400">${chat.activity}</span>
                    </div>
                    <p class="text-gray-300 text-sm mb-3">${chat.description}</p>
                    <div class="flex flex-wrap gap-1 mb-3">
                        ${chat.tags.map(tag => `<span class="chat-tag">${tag}</span>`).join('')}
                    </div>
                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-4 text-sm text-gray-400">
                            <span><i class="ri-user-line mr-1"></i>${chat.participants} members</span>
                            <span><i class="ri-global-line mr-1"></i>${chat.language}</span>
                        </div>
                        <div class="flex gap-2">
                            <button onclick="previewChat(${chat.id})" 
                                    class="bg-gray-700 text-white px-4 py-2 rounded-lg hover:bg-gray-600 transition-colors text-sm">
                                <i class="ri-eye-line mr-1"></i>Preview
                            </button>
                            <button onclick="joinChat(${chat.id})" 
                                    class="bg-primary text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors text-sm font-medium">
                                <i class="ri-chat-3-line mr-1"></i>Join Chat
                            </button>
                        </div>
                    </div>
                    <div class="mt-3 p-3 bg-gray-900/50 rounded-lg border-l-4 border-primary/30">
                        <p class="text-sm text-gray-300 italic">"${chat.preview}"</p>
                    </div>
                </div>
            </div>
        `;
        resultsContainer.appendChild(chatElement);
    });
}

function showDiscoveryState(state) {
    const welcome = document.getElementById('discoveryWelcome');
    const loading = document.getElementById('discoveryLoading');
    const results = document.getElementById('discoveryResults');
    const noResults = document.getElementById('discoveryNoResults');
    
    // Hide all
    welcome.style.display = 'none';
    loading.style.display = 'none';
    results.style.display = 'none';
    noResults.style.display = 'none';
    
    // Show selected
    switch(state) {
        case 'welcome':
            welcome.style.display = 'block';
            break;
        case 'loading':
            loading.style.display = 'block';
            break;
        case 'results':
            results.style.display = 'block';
            break;
        case 'no-results':
            noResults.style.display = 'block';
            break;
    }
}

function clearChatSearch() {
    document.getElementById('chatDiscoverySearch').value = '';
    showDiscoveryState('welcome');
}

function previewChat(chatId) {
    alert(`Preview for chat ${chatId} - Feature coming soon!`);
}

function joinChat(chatId) {
    window.open(`/chat?room=${chatId}`, '_blank');
    closeChatDiscovery();
}

function popOutChatDiscovery() {
    const popupWindow = window.open('', 'UniBabelChatDiscovery', 'width=1200,height=800,scrollbars=yes,resizable=yes');
    if (popupWindow) {
        const html = `<!DOCTYPE html><html><head><title>UniBabel - Chat Discovery</title><script src="https://cdn.tailwindcss.com"></script><link href="https://cdnjs.cloudflare.com/ajax/libs/remixicon/4.6.0/remixicon.min.css" rel="stylesheet"></head><body class="bg-gray-900 text-white"><div class="p-6"><h1 class="text-2xl font-bold mb-4">🔍 Chat Discovery</h1><p>This is your dedicated chat discovery window!</p><p class="text-gray-400 mt-2">Full functionality coming soon...</p></div></body></html>`;
        popupWindow.document.write(html);
        popupWindow.document.close();
    }
}

function closeChatDiscovery() {
    const modal = document.getElementById('chat-discovery-modal');
    if (modal) {
        modal.remove();
    }
}

// Function to open Browse Chats pop-out (Twitch + Discord trending rooms)
function openBrowseChats() {
    console.log('🔥 Opening Browse Chats...');
    alert('Browse Chats - Twitch-style trending rooms coming soon! 🔥');
}

// Listen for Esc key or click outside to close modal
document.addEventListener('keydown', function(e) {
    const modal = document.getElementById('chat-discovery-modal');
    if (modal && e.key === 'Escape') {
        closeChatDiscovery();
    }
});

window.addEventListener('click', function(e) {
    const modal = document.getElementById('chat-discovery-modal');
    if (modal && e.target === modal) {
        closeChatDiscovery();
    }
});