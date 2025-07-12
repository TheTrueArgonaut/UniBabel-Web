// Rooms API JavaScript - Backend Communication & API Calls
class RoomsAPI {
    constructor() {
        this.baseUrl = '/api/rooms';
    }

    async joinRoom(roomId) {
        try {
            const response = await fetch(`${this.baseUrl}/${roomId}/join`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (response.ok) {
                window.location.href = `/chat?room=${roomId}`;
            } else {
                console.error('Error joining room:', data.error);
                this.showNotification('Error joining room: ' + data.error, 'error');
            }
        } catch (error) {
            console.error('Error joining room:', error);
            this.showNotification('Failed to join room', 'error');
        }
    }

    async joinDiscoverableRoom(roomId) {
        try {
            const response = await fetch(`${this.baseUrl}/${roomId}/join-discoverable`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (response.ok && data.success) {
                window.location.reload();
            } else {
                console.error('Error joining room:', data.error);
                this.showNotification('Error joining room: ' + data.error, 'error');
            }
        } catch (error) {
            console.error('Error joining room:', error);
            this.showNotification('Failed to join room', 'error');
        }
    }

    async createRoom(roomData) {
        try {
            const response = await fetch(this.baseUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(roomData)
            });

            const data = await response.json();

            if (response.ok) {
                window.roomsModals.closeCreateRoomModal();
                window.roomsCore.refreshRooms();
                window.location.href = `/chat?room=${data.room_id}`;
            } else {
                console.error('Error creating room:', data.error);
                this.showNotification('Error creating room: ' + data.error, 'error');
            }
        } catch (error) {
            console.error('Error creating room:', error);
            this.showNotification('Failed to create room', 'error');
        }
    }

    async joinRoomWithCode(inviteCode) {
        try {
            const response = await fetch(`${this.baseUrl}/join`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ invite_code: inviteCode })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                window.roomsModals.closeJoinRoomModal();
                window.roomsCore.refreshRooms();
                window.location.href = `/chat?room=${data.room_id}`;
            } else {
                console.error('Error joining room:', data.error);
                this.showNotification('Error joining room: ' + data.error, 'error');
            }
        } catch (error) {
            console.error('Error joining room:', error);
            this.showNotification('Failed to join room', 'error');
        }
    }

    async acceptInvite(roomId) {
        try {
            const response = await fetch(`${this.baseUrl}/${roomId}/join`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (response.ok) {
                window.roomsCore.loadPendingInvites();
                window.roomsCore.loadMyRooms();
                this.showNotification('Successfully joined the room!', 'success');
            } else {
                console.error('Error accepting invite:', data.error);
                this.showNotification('Error accepting invite: ' + data.error, 'error');
            }
        } catch (error) {
            console.error('Error accepting invite:', error);
            this.showNotification('Failed to accept invite', 'error');
        }
    }

    async declineInvite(roomId) {
        try {
            const response = await fetch(`${this.baseUrl}/${roomId}/decline-invite`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (response.ok) {
                window.roomsCore.loadPendingInvites();
                this.showNotification('Invite declined', 'info');
            } else {
                console.error('Error declining invite:', data.error);
                this.showNotification('Error declining invite: ' + data.error, 'error');
            }
        } catch (error) {
            console.error('Error declining invite:', error);
            this.showNotification('Failed to decline invite', 'error');
        }
    }

    async updateRoom(roomId, updates) {
        try {
            const response = await fetch(`${this.baseUrl}/${roomId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(updates)
            });

            const data = await response.json();

            if (response.ok) {
                this.showNotification('Room updated successfully!', 'success');
                window.roomsCore.refreshRooms();
                return data;
            } else {
                console.error('Error updating room:', data.error);
                this.showNotification('Error updating room: ' + data.error, 'error');
                return null;
            }
        } catch (error) {
            console.error('Error updating room:', error);
            this.showNotification('Failed to update room', 'error');
            return null;
        }
    }

    async deleteRoom(roomId) {
        try {
            const response = await fetch(`${this.baseUrl}/${roomId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (response.ok) {
                this.showNotification('Room deleted successfully', 'success');
                window.roomsCore.refreshRooms();
                window.roomsSettings.closeRoomSettings();
                return true;
            } else {
                console.error('Error deleting room:', data.error);
                this.showNotification('Error deleting room: ' + data.error, 'error');
                return false;
            }
        } catch (error) {
            console.error('Error deleting room:', error);
            this.showNotification('Failed to delete room', 'error');
            return false;
        }
    }

    async getRoomSettings(roomId) {
        try {
            const response = await fetch(`${this.baseUrl}/${roomId}/settings`);
            const data = await response.json();

            if (response.ok) {
                return data;
            } else {
                console.error('Error getting room settings:', data.error);
                this.showNotification('Error loading room settings', 'error');
                return null;
            }
        } catch (error) {
            console.error('Error getting room settings:', error);
            this.showNotification('Failed to load room settings', 'error');
            return null;
        }
    }

    async updateRoomSettings(roomId, settings) {
        try {
            const response = await fetch(`${this.baseUrl}/${roomId}/settings`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(settings)
            });

            const data = await response.json();

            if (response.ok) {
                this.showNotification('Settings saved successfully!', 'success');
                return data;
            } else {
                console.error('Error updating settings:', data.error);
                this.showNotification('Error saving settings: ' + data.error, 'error');
                return null;
            }
        } catch (error) {
            console.error('Error updating settings:', error);
            this.showNotification('Failed to save settings', 'error');
            return null;
        }
    }

    async getRoomMembers(roomId) {
        try {
            const response = await fetch(`${this.baseUrl}/${roomId}/members`);
            const data = await response.json();

            if (response.ok) {
                return data.members || [];
            } else {
                console.error('Error getting room members:', data.error);
                return [];
            }
        } catch (error) {
            console.error('Error getting room members:', error);
            return [];
        }
    }

    async updateMemberRole(roomId, userId, role) {
        try {
            const response = await fetch(`${this.baseUrl}/${roomId}/members/${userId}/role`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ role })
            });

            const data = await response.json();

            if (response.ok) {
                this.showNotification('Member role updated', 'success');
                return true;
            } else {
                console.error('Error updating member role:', data.error);
                this.showNotification('Error updating role: ' + data.error, 'error');
                return false;
            }
        } catch (error) {
            console.error('Error updating member role:', error);
            this.showNotification('Failed to update member role', 'error');
            return false;
        }
    }

    async kickMember(roomId, userId) {
        try {
            const response = await fetch(`${this.baseUrl}/${roomId}/members/${userId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (response.ok) {
                this.showNotification('Member removed from room', 'success');
                return true;
            } else {
                console.error('Error kicking member:', data.error);
                this.showNotification('Error removing member: ' + data.error, 'error');
                return false;
            }
        } catch (error) {
            console.error('Error kicking member:', error);
            this.showNotification('Failed to remove member', 'error');
            return false;
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg transition-all duration-300 ${
            type === 'success' ? 'bg-green-600 text-white' :
            type === 'error' ? 'bg-red-600 text-white' :
            type === 'warning' ? 'bg-yellow-600 text-white' :
            'bg-blue-600 text-white'
        }`;
        notification.textContent = message;

        // Add to DOM
        document.body.appendChild(notification);

        // Remove after 5 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 5000);
    }
}

// Initialize global instance
window.roomsApi = new RoomsAPI();