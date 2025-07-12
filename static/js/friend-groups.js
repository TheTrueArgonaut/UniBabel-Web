// Friend Groups JavaScript

// Modal functions for friend groups
function openCreateGroupModal() {
    document.getElementById('createGroupModal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('createGroupModal').style.display = 'none';
}

// Add event listener to the + button
document.addEventListener('DOMContentLoaded', () => {
    const addButton = document.querySelector('.add-group-btn');
    if (addButton) {
        addButton.addEventListener('click', openCreateGroupModal);
    }
});

// Create group function
async function createGroup() {
    const groupName = document.getElementById('groupName').value.trim();
    const groupType = document.getElementById('groupType').value;

    if (!groupName) {
        alert('Please enter a group name');
        return;
    }

    try {
        const response = await fetch('/api/friend-groups/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                group_name: groupName,
                group_type: groupType
            })
        });

        const data = await response.json();

        if (data.success) {
            alert(`Friend group "${data.group_name}" created successfully!`);
            closeModal();
            loadFriendGroups(); // Reload the groups

            // Clear form
            document.getElementById('groupName').value = '';
            document.getElementById('groupType').value = 'mixed';
        } else {
            alert(`Failed to create group: ${data.error}`);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Network error. Please try again.');
    }
}

// Load friend groups
async function loadFriendGroups() {
    try {
        const response = await fetch('/api/friend-groups/my-groups');
        const data = await response.json();

        if (data.success) {
            displayFriendGroups(data.groups);
        }
    } catch (error) {
        console.error('Error loading friend groups:', error);
    }
}

// Display friend groups
function displayFriendGroups(groups) {
    const container = document.querySelector('.sidebar-section');
    if (!container) return;

    // Clear existing groups
    const existingGroups = container.querySelectorAll('.friend-group');
    existingGroups.forEach(group => group.remove());

    if (groups.length === 0) {
        const emptyState = document.createElement('div');
        emptyState.className = 'empty-groups';
        emptyState.innerHTML = `
            <p class="text-gray-400 text-center text-xs">
                No friend groups yet.<br>
                Click + to create your first group!
            </p>
        `;
        container.appendChild(emptyState);
        return;
    }

    groups.forEach(group => {
        const groupElement = document.createElement('div');
        groupElement.className = 'friend-group';
        groupElement.innerHTML = `
            <div class="group-avatar">${group.group_name[0].toUpperCase()}</div>
            <div class="group-info">
                <div class="group-name">${group.group_name}</div>
                <div class="group-meta">${group.member_count} members • ${group.group_type}</div>
            </div>
            <div class="group-actions">
                ${group.can_babel ? '<button class="group-action" onclick="postToGroup(' + group.group_id + ')" title="Post to group">📝</button>' : ''}
                ${group.can_chat ? '<button class="group-action" onclick="openGroupChat(' + group.group_id + ')" title="Group chat">💬</button>' : ''}
            </div>
        `;

        container.appendChild(groupElement);
    });
}

// Group actions
function postToGroup(groupId) {
    alert(`Post to group ${groupId} - Feature coming soon!`);
}

function openGroupChat(groupId) {
    alert(`Open group chat ${groupId} - Feature coming soon!`);
}