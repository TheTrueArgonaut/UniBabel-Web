// Global Search JavaScript - Universal search for chats, friends, rooms, etc.

let searchTimeout;
let isSearchVisible = false;

// 1. INITIALIZATION
document.addEventListener('DOMContentLoaded', function() {
    setupGlobalSearchListeners();
    setupKeyboardShortcuts();
});

// 2. EVENT LISTENERS SETUP
function setupGlobalSearchListeners() {
    const searchInput = document.getElementById('globalSearchInput');
    const searchResults = document.getElementById('searchResults');
    
    // Click outside to close
    document.addEventListener('click', function(e) {
        if (!searchResults.contains(e.target) && !searchInput.contains(e.target)) {
            hideSearchResults();
        }
    });
    
    // Input blur handling
    searchInput.addEventListener('blur', function() {
        // Small delay to allow clicking on results
        setTimeout(() => {
            if (!document.activeElement.closest('#searchResults')) {
                hideSearchResults();
            }
        }, 150);
    });
}

// 3. KEYBOARD SHORTCUTS
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // CMD+K or CTRL+K to focus search
        if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
            e.preventDefault();
            focusSearch();
        }
        
        // ESC to close search
        if (e.key === 'Escape' && isSearchVisible) {
            hideSearchResults();
            document.getElementById('globalSearchInput').blur();
        }
    });
}

// 4. SEARCH FUNCTIONS
function focusSearch() {
    const searchInput = document.getElementById('globalSearchInput');
    searchInput.focus();
    showSearchSuggestions();
}

function showSearchSuggestions() {
    const searchResults = document.getElementById('searchResults');
    const searchSuggestions = document.getElementById('searchSuggestions');
    const searchResultsList = document.getElementById('searchResultsList');
    const searchNoResults = document.getElementById('searchNoResults');
    
    // Show suggestions, hide results
    searchSuggestions.style.display = 'block';
    searchResultsList.style.display = 'none';
    searchNoResults.style.display = 'none';
    
    searchResults.classList.remove('hidden');
    isSearchVisible = true;
}

function hideSearchResults() {
    const searchResults = document.getElementById('searchResults');
    searchResults.classList.add('hidden');
    isSearchVisible = false;
}

function performGlobalSearch() {
    clearTimeout(searchTimeout);
    const query = document.getElementById('globalSearchInput').value.trim();
    
    if (!query) {
        showSearchSuggestions();
        return;
    }
    
    // Debounce search
    searchTimeout = setTimeout(() => {
        executeSearch(query);
    }, 300);
}

// 5. SEARCH EXECUTION
async function executeSearch(query) {
    showSearchLoading();
    
    try {
        // Try real API first
        const response = await fetch(`/api/search/global?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        if (data.success) {
            displaySearchResults(data.results);
        } else {
            throw new Error('API search failed');
        }
    } catch (error) {
        console.log('Using mock search data for:', query);
        // Use mock data for demo
        const mockResults = generateMockSearchResults(query);
        displaySearchResults(mockResults);
    }
}

// 6. MOCK DATA GENERATOR
function generateMockSearchResults(query) {
    const allResults = [
        // Friends
        { type: 'friend', id: 1, name: 'Sarah Chen', username: '@sarahc', status: 'online', avatar: '👩‍💻', lastSeen: 'now' },
        { type: 'friend', id: 2, name: 'Alex Rodriguez', username: '@alexr', status: 'offline', avatar: '👨‍🎨', lastSeen: '2h ago' },
        { type: 'friend', id: 3, name: 'Emily Johnson', username: '@emilyj', status: 'online', avatar: '👩‍🔬', lastSeen: 'now' },
        
        // Chats/Rooms
        { type: 'room', id: 101, name: 'Gaming Central', category: 'gaming', participants: 1247, activity: 'Very Active', description: 'Ultimate gaming community' },
        { type: 'room', id: 102, name: 'Language Exchange', category: 'language', participants: 892, activity: 'Active', description: 'Practice languages with natives' },
        { type: 'room', id: 103, name: 'Code & Coffee', category: 'tech', participants: 456, activity: 'Moderate', description: 'Programming discussions' },
        
        // Topics/Tags
        { type: 'topic', id: 201, name: 'JavaScript', category: 'programming', posts: 1543, trending: true },
        { type: 'topic', id: 202, name: 'Spanish Learning', category: 'language', posts: 987, trending: false },
        { type: 'topic', id: 203, name: 'Gaming News', category: 'gaming', posts: 2156, trending: true },
        
        // Recent Chats
        { type: 'chat', id: 301, name: 'Sarah Chen', type: 'direct', lastMessage: 'Hey! How\'s the project going?', time: '5m ago' },
        { type: 'chat', id: 302, name: 'Study Group', type: 'group', lastMessage: 'Meeting at 3pm today', time: '1h ago' }
    ];
    
    // Filter based on query
    return allResults.filter(item => 
        item.name.toLowerCase().includes(query.toLowerCase()) ||
        item.category?.toLowerCase().includes(query.toLowerCase()) ||
        item.description?.toLowerCase().includes(query.toLowerCase()) ||
        item.username?.toLowerCase().includes(query.toLowerCase())
    );
}

// 7. DISPLAY RESULTS
function displaySearchResults(results) {
    const searchSuggestions = document.getElementById('searchSuggestions');
    const searchResultsList = document.getElementById('searchResultsList');
    const searchNoResults = document.getElementById('searchNoResults');
    
    if (results.length === 0) {
        searchSuggestions.style.display = 'none';
        searchResultsList.style.display = 'none';
        searchNoResults.style.display = 'block';
        return;
    }
    
    // Group results by type
    const groupedResults = groupResultsByType(results);
    
    // Hide suggestions, show results
    searchSuggestions.style.display = 'none';
    searchNoResults.style.display = 'none';
    searchResultsList.style.display = 'block';
    
    // Generate HTML
    searchResultsList.innerHTML = generateResultsHTML(groupedResults);
}

function groupResultsByType(results) {
    const groups = {
        friend: [],
        room: [],
        topic: [],
        chat: []
    };
    
    results.forEach(result => {
        if (groups[result.type]) {
            groups[result.type].push(result);
        }
    });
    
    return groups;
}

function generateResultsHTML(groupedResults) {
    let html = '';
    
    // Friends
    if (groupedResults.friend.length > 0) {
        html += `
            <div class="p-3 border-b border-gray-700">
                <p class="text-xs font-semibold text-gray-400 mb-2">FRIENDS</p>
                ${groupedResults.friend.map(friend => `
                    <div class="search-result-item flex items-center gap-3 p-2 rounded-lg hover:bg-gray-700 cursor-pointer" onclick="openFriendProfile(${friend.id})">
                        <div class="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-lg">
                            ${friend.avatar}
                        </div>
                        <div class="flex-1">
                            <div class="flex items-center gap-2">
                                <span class="font-medium text-white">${friend.name}</span>
                                <span class="w-2 h-2 rounded-full ${friend.status === 'online' ? 'bg-green-400' : 'bg-gray-500'}"></span>
                            </div>
                            <p class="text-xs text-gray-400">${friend.username} • ${friend.lastSeen}</p>
                        </div>
                        <button class="text-primary hover:bg-primary/10 px-2 py-1 rounded text-sm">
                            <i class="ri-message-3-line"></i>
                        </button>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    // Rooms
    if (groupedResults.room.length > 0) {
        html += `
            <div class="p-3 border-b border-gray-700">
                <p class="text-xs font-semibold text-gray-400 mb-2">CHAT ROOMS</p>
                ${groupedResults.room.map(room => `
                    <div class="search-result-item flex items-center gap-3 p-2 rounded-lg hover:bg-gray-700 cursor-pointer" onclick="joinRoom(${room.id})">
                        <div class="w-8 h-8 rounded-full bg-blue-500/10 flex items-center justify-center">
                            <i class="ri-group-line text-blue-400"></i>
                        </div>
                        <div class="flex-1">
                            <div class="flex items-center gap-2">
                                <span class="font-medium text-white">${room.name}</span>
                                <span class="text-xs px-2 py-1 rounded-full bg-green-500/20 text-green-400">${room.activity}</span>
                            </div>
                            <p class="text-xs text-gray-400">${room.participants.toLocaleString()} members • ${room.description}</p>
                        </div>
                        <button class="bg-primary text-white px-3 py-1 rounded text-sm hover:bg-red-700">
                            Join
                        </button>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    // Topics
    if (groupedResults.topic.length > 0) {
        html += `
            <div class="p-3 border-b border-gray-700">
                <p class="text-xs font-semibold text-gray-400 mb-2">TOPICS</p>
                ${groupedResults.topic.map(topic => `
                    <div class="search-result-item flex items-center gap-3 p-2 rounded-lg hover:bg-gray-700 cursor-pointer" onclick="searchTopic('${topic.name}')">
                        <div class="w-8 h-8 rounded-full bg-yellow-500/10 flex items-center justify-center">
                            <i class="ri-hashtag text-yellow-400"></i>
                        </div>
                        <div class="flex-1">
                            <div class="flex items-center gap-2">
                                <span class="font-medium text-white">#${topic.name}</span>
                                ${topic.trending ? '<span class="text-xs px-2 py-1 rounded-full bg-orange-500/20 text-orange-400">🔥 Trending</span>' : ''}
                            </div>
                            <p class="text-xs text-gray-400">${topic.posts.toLocaleString()} posts • ${topic.category}</p>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    // Recent Chats
    if (groupedResults.chat.length > 0) {
        html += `
            <div class="p-3">
                <p class="text-xs font-semibold text-gray-400 mb-2">RECENT CHATS</p>
                ${groupedResults.chat.map(chat => `
                    <div class="search-result-item flex items-center gap-3 p-2 rounded-lg hover:bg-gray-700 cursor-pointer" onclick="openChat(${chat.id})">
                        <div class="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                            <i class="ri-${chat.type === 'direct' ? 'user' : 'group'}-line text-primary"></i>
                        </div>
                        <div class="flex-1">
                            <span class="font-medium text-white">${chat.name}</span>
                            <p class="text-xs text-gray-400 truncate">${chat.lastMessage}</p>
                        </div>
                        <span class="text-xs text-gray-500">${chat.time}</span>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    return html;
}

// 8. LOADING STATE
function showSearchLoading() {
    const searchSuggestions = document.getElementById('searchSuggestions');
    const searchResultsList = document.getElementById('searchResultsList');
    const searchNoResults = document.getElementById('searchNoResults');
    
    searchSuggestions.style.display = 'none';
    searchNoResults.style.display = 'none';
    searchResultsList.style.display = 'block';
    searchResultsList.innerHTML = `
        <div class="p-4 text-center">
            <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
            <p class="text-gray-400 mt-2 text-sm">Searching...</p>
        </div>
    `;
}

// 9. ACTION HANDLERS
function searchFor(query) {
    document.getElementById('globalSearchInput').value = query;
    performGlobalSearch();
}

function openFriendProfile(friendId) {
    hideSearchResults();
    // Implement friend profile logic
    console.log('Opening friend profile:', friendId);
}

function joinRoom(roomId) {
    hideSearchResults();
    window.open(`/chat?room=${roomId}`, '_blank');
}

function searchTopic(topicName) {
    hideSearchResults();
    // Open chat discovery with this topic
    openChatDiscovery();
    setTimeout(() => {
        const chatSearch = document.getElementById('chatDiscoverySearch');
        if (chatSearch) {
            chatSearch.value = topicName;
            performChatSearch();
        }
    }, 100);
}

function openChat(chatId) {
    hideSearchResults();
    window.open(`/chat?id=${chatId}`, '_blank');
}