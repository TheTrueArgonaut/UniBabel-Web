<script>
// 🎯 ROOM MANAGER MICROSERVICE - Single Responsibility: Room operations
// Handles: Room creation, joining, loading, display

// Toggle category function
function toggleCategory(category) {
    const categoryContent = document.getElementById(`${category}-content`);
    const categoryArrow = document.getElementById(`${category}-arrow`);
    
    if (categoryContent.classList.contains('hidden')) {
        categoryContent.classList.remove('hidden');
        categoryArrow.classList.remove('collapsed');
    } else {
        categoryContent.classList.add('hidden');
        categoryArrow.classList.add('collapsed');
    }
}

// Load all room categories
function loadRoomCategories() {
    loadFriendGroups();
    loadPrivateRooms();
    loadPublicRooms();
}

// Load friend groups
async function loadFriendGroups() {
    try {
        const response = await fetch('/api/friend-groups/my-groups');
        const data = await response.json();
        
        if (data.success) {
            displayGroups(data.groups);
            updateCategoryCount('groups', data.groups.length);
        }
    } catch (error) {
        console.error('Error loading friend groups:', error);
    }
}

// Load private rooms
async function loadPrivateRooms() {
    try {
        const response = await fetch('/api/rooms/my-rooms');
        const data = await response.json();
        
        if (data.success) {
            displayPrivateRooms(data.rooms);
            updateCategoryCount('private', data.rooms.length);
        }
    } catch (error) {
        console.error('Error loading private rooms:', error);
    }
}

// Load public rooms
async function loadPublicRooms() {
    updateCategoryCount('public', 0);
}

// Display friend groups
function displayGroups(groups) {
    const container = document.getElementById('groups-list');
    const emptyState = document.getElementById('groups-empty');
    
    container.innerHTML = '';
    
    if (groups.length === 0) {
        emptyState.style.display = 'block';
        return;
    }
    
    emptyState.style.display = 'none';
    
    groups.forEach(group => {
        const groupElement = document.createElement('div');
        groupElement.className = 'room-item';
        groupElement.onclick = () => openGroupChat(group.group_id);
        
        groupElement.innerHTML = `
            <span class="room-icon">#</span>
            <span class="room-name">${group.group_name}</span>
            <span class="room-status">${group.member_count}</span>
        `;
        
        container.appendChild(groupElement);
    });
}

// Display private rooms
function displayPrivateRooms(rooms) {
    const container = document.getElementById('private-list');
    const emptyState = document.getElementById('private-empty');
    
    container.innerHTML = '';
    
    if (rooms.length === 0) {
        emptyState.style.display = 'block';
        return;
    }
    
    emptyState.style.display = 'none';
    
    rooms.forEach(room => {
        const roomElement = document.createElement('div');
        roomElement.className = 'room-item';
        roomElement.onclick = () => joinRoom(room.room_id);
        
        const icon = room.voice_enabled ? '🔊' : '#';
        
        roomElement.innerHTML = `
            <span class="room-icon">${icon}</span>
            <span class="room-name">${room.room_name}</span>
            <span class="room-status">${room.member_count || 1}</span>
        `;
        
        container.appendChild(roomElement);
    });
}

// Update category count
function updateCategoryCount(category, count) {
    const countElement = document.getElementById(`${category}-count`);
    countElement.textContent = count;
    
    if (count === 0) {
        countElement.style.display = 'none';
    } else {
        countElement.style.display = 'block';
    }
}

// Room interaction functions
function openGroupChat(groupId) {
    alert(`Opening group chat ${groupId} - Feature coming soon!`);
}

function joinRoom(roomId) {
    alert(`Joining room ${roomId} - Feature coming soon!`);
}

// Load pending invites count
async function loadPendingInvitesCount() {
    try {
        const response = await fetch('/api/rooms/pending-invites');
        const data = await response.json();
        
        if (data.success) {
            const count = data.invites.length;
            const inviteCountElement = document.getElementById('inviteCount');
            if (inviteCountElement) {
                inviteCountElement.textContent = count === 0 ? 'No pending invites' : `${count} pending`;
            }
        }
    } catch (error) {
        console.error('Error loading invite count:', error);
    }
}

// Create room API call
async function createRoomNow() {
    const roomName = document.getElementById('roomNameInput').value.trim();
    const roomDescription = document.getElementById('roomDescriptionInput').value.trim();
    const roomType = document.querySelector('input[name="roomType"]:checked').value;
    const voiceEnabled = document.getElementById('voiceChatEnabled').checked;
    const contentModeration = document.getElementById('contentModeration').checked;
    const anyoneCanInvite = document.getElementById('anyoneCanInvite').checked;
    const fileUploads = document.getElementById('fileUploads').checked;
    const welcomeMessage = document.getElementById('welcomeMessage').value.trim();
    const roomTheme = document.querySelector('input[name="roomTheme"]:checked')?.value || 'default';
    
    if (!roomName) {
        alert('Please enter a room name');
        return;
    }
    
    const roomData = {
        room_name: roomName,
        description: roomDescription,
        room_type: roomType,
        voice_enabled: voiceEnabled,
        is_discoverable: roomType === 'public',
        settings: {
            content_moderation: contentModeration,
            anyone_can_invite: anyoneCanInvite,
            file_uploads: fileUploads,
            welcome_message: welcomeMessage,
            theme: roomTheme,
            icon: selectedRoomIcon
        }
    };
    
    try {
        const response = await fetch('/api/rooms/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(roomData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            const typeText = roomType === 'public' ? 'public' : 'private';
            const voiceText = voiceEnabled ? ' with voice chat' : '';
            const inviteText = roomType === 'private' ? `\n\nInvite Code: ${data.invite_code}\n\nShare this code with friends to invite them!` : '';
            
            alert(`${typeText.charAt(0).toUpperCase() + typeText.slice(1)} room "${data.room_name}" created successfully${voiceText}!${inviteText}`);
            
            hideCreateRoomModal();
            loadRoomCategories();
        } else {
            if (data.upgrade_required) {
                if (confirm(`${data.error}\n\nWould you like to upgrade to Premium now?`)) {
                    window.location.href = '/premium';
                }
            } else {
                alert(`Failed to create room: ${data.error}`);
            }
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Network error. Please try again.');
    }
}

// Join room by code
function joinRoomByCode() {
    const inviteCodeInput = document.getElementById('inviteCodeInput');
    const inviteCode = inviteCodeInput.value.trim();
    
    if (!inviteCode) {
        alert('Please enter an invite code');
        return;
    }
    
    fetch('/api/rooms/join', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ invite_code: inviteCode })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`Successfully joined room: ${data.room_name}!`);
            hideCreateRoomModal();
            loadRoomCategories();
        } else {
            alert(`Failed to join room: ${data.error}`);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Network error. Please try again.');
    });
}

// Show pending invites
async function showPendingInvites() {
    try {
        const response = await fetch('/api/rooms/pending-invites');
        const data = await response.json();
        
        if (data.success && data.invites.length > 0) {
            let inviteList = 'Pending Invitations:\n\n';
            data.invites.forEach((invite, index) => {
                inviteList += `${index + 1}. ${invite.room_name}\n`;
                inviteList += `   Invited by: ${invite.invited_by}\n`;
                inviteList += `   Type: ${invite.room_type}\n\n`;
            });
            
            if (confirm(inviteList + '\nWould you like to view and manage your invitations?')) {
                alert('Invitation management coming soon!');
            }
        } else {
            alert('You have no pending room invitations.');
        }
    } catch (error) {
        console.error('Error fetching invites:', error);
        alert('Could not load invitations. Please try again.');
    }
}

// Initialize room management
document.addEventListener('DOMContentLoaded', function() {
    loadPendingInvitesCount();
    loadRoomCategories();
});
</script>