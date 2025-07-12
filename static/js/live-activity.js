// Live Activity JavaScript - Real-time updating stats

let activityData = {
    onlineUsers: 0,
    translations: 0,
    activeRooms: 0,
    newConnections: 0
};

// 1. INITIALIZATION
document.addEventListener('DOMContentLoaded', function() {
    loadRealActivityData();
    startLiveUpdates();
    updateActivityTicker();
});

// 2. LOAD REAL ACTIVITY DATA
async function loadRealActivityData() {
    try {
        // Fetch real data from your APIs
        const [usersResponse, translationsResponse, roomsResponse, connectionsResponse] = await Promise.all([
            fetch('/api/stats/online-users'),
            fetch('/api/stats/translations-today'), 
            fetch('/api/stats/active-rooms'),
            fetch('/api/stats/new-connections')
        ]);

        // Parse responses
        const usersData = await usersResponse.json();
        const translationsData = await translationsResponse.json();
        const roomsData = await roomsResponse.json();
        const connectionsData = await connectionsResponse.json();

        // Update with real data
        if (usersData.success) {
            activityData.onlineUsers = usersData.count;
            updateStatElement('onlineCount', activityData.onlineUsers.toLocaleString());
        }

        if (translationsData.success) {
            activityData.translations = translationsData.count;
            updateStatElement('translationCount', activityData.translations.toLocaleString());
        }

        if (roomsData.success) {
            activityData.activeRooms = roomsData.count;
            updateStatElement('activeRooms', activityData.activeRooms);
        }

        if (connectionsData.success) {
            activityData.newConnections = connectionsData.count;
            updateStatElement('newConnections', `+${activityData.newConnections}`);
        }

        // Load real activity messages
        loadRealActivityMessages();

    } catch (error) {
        console.log('Could not load live data - APIs not ready yet');
        // Hide the live activity component until APIs are ready
        const liveActivityContainer = document.querySelector('.live-activity-container');
        if (liveActivityContainer) {
            liveActivityContainer.style.display = 'none';
        }
    }
}

// 3. LOAD REAL ACTIVITY MESSAGES
async function loadRealActivityMessages() {
    try {
        const response = await api.activity.getRecentActivity();
        
        if (response.success && response.messages) {
            displayActivityMessages(response.messages);
        } else {
            displayActivityMessages(getMockActivityMessages());
        }
    } catch (error) {
        // API not ready yet - silently use mock data
        displayActivityMessages(getMockActivityMessages());
    }
}

// 4. START LIVE UPDATES WITH REAL DATA
function startLiveUpdates() {
    // Refresh real data every 30 seconds
    setInterval(loadRealActivityData, 30000);
    
    // Update activity ticker every 10 seconds
    setInterval(loadRealActivityMessages, 10000);
}

// 5. UPDATE STAT ELEMENT WITH ANIMATION
function updateStatElement(elementId, newValue) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    // Add update flash effect
    element.style.transform = 'scale(1.1)';
    element.style.transition = 'transform 0.2s ease';
    
    // Update value
    setTimeout(() => {
        element.textContent = newValue;
        element.style.transform = 'scale(1)';
    }, 100);
}

// 6. UPDATE ACTIVITY TICKER WITH REAL DATA
function updateActivityTicker(activities = null) {
    const ticker = document.getElementById('activityTicker');
    if (!ticker) return;
    
    let tickerText = '';
    
    if (activities && activities.length > 0) {
        // Use real activity data
        tickerText = activities.slice(0, 3).map(activity => activity.message).join(' • ') + ' • ';
    } else {
        // Fallback: show "Loading activity..." until real data arrives
        tickerText = 'Loading live activity... • ';
    }
    
    // Smooth transition
    ticker.style.opacity = '0.5';
    ticker.style.transition = 'opacity 0.3s ease';
    
    setTimeout(() => {
        ticker.textContent = tickerText;
        ticker.style.opacity = '1';
        
        // Reset animation
        ticker.style.animation = 'none';
        ticker.offsetHeight; // Trigger reflow
        ticker.style.animation = 'marquee 20s linear infinite';
    }, 300);
}

// 7. WEBSOCKET CONNECTION FOR REAL-TIME UPDATES
function connectWebSocket() {
    try {
        const ws = new WebSocket(`ws://${window.location.host}/ws/activity`);
        
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            
            // Handle real-time updates
            switch(data.type) {
                case 'user_online':
                    activityData.onlineUsers = data.count;
                    updateStatElement('onlineCount', activityData.onlineUsers.toLocaleString());
                    break;
                    
                case 'new_translation':
                    activityData.translations = data.count;
                    updateStatElement('translationCount', activityData.translations.toLocaleString());
                    break;
                    
                case 'room_activity':
                    activityData.activeRooms = data.count;
                    updateStatElement('activeRooms', activityData.activeRooms);
                    break;
                    
                case 'new_connection':
                    activityData.newConnections = data.count;
                    updateStatElement('newConnections', `+${activityData.newConnections}`);
                    break;
                    
                case 'activity_message':
                    updateActivityTicker([data]);
                    break;
            }
        };
        
        ws.onclose = function() {
            // Reconnect after 5 seconds
            setTimeout(connectWebSocket, 5000);
        };
        
    } catch (error) {
        console.log('WebSocket not available - using polling instead');
    }
}

// 8. EXPORT FUNCTIONS FOR OTHER COMPONENTS
window.liveActivity = {
    refresh: loadRealActivityData,
    getCurrentStats: () => activityData,
    connectWebSocket: connectWebSocket
};