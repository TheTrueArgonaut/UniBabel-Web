// Profile Management JavaScript

// Modal functions for profile picture
function openProfilePictureModal() {
    document.getElementById('profilePictureModal').style.display = 'flex';
}

function closeProfilePictureModal() {
    document.getElementById('profilePictureModal').style.display = 'none';
}

// Add event listener to the profile picture button
document.addEventListener('DOMContentLoaded', () => {
    const profilePictureButton = document.querySelector('#profilePictureContainer');
    if (profilePictureButton) {
        profilePictureButton.addEventListener('click', openProfilePictureModal);
    }
});

// Preview profile picture function
function previewProfilePicture(input) {
    const file = input.files[0];
    const preview = document.getElementById('modalProfileImage');

    if (file) {
        const reader = new FileReader();
        reader.onload = function(event) {
            preview.src = event.target.result;
            preview.style.display = 'block';
            document.getElementById('modalProfilePlaceholder').style.display = 'none';
            document.getElementById('uploadProfileBtn').disabled = false;
        };
        reader.readAsDataURL(file);
    }
}

// Upload profile picture function
async function uploadProfilePicture() {
    const fileInput = document.getElementById('profilePictureInput');
    const file = fileInput.files[0];

    if (!file) {
        alert('Please select a profile picture');
        return;
    }

    try {
        const formData = new FormData();
        formData.append('profile_picture', file);

        const response = await fetch('/api/profile-picture/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            alert('Profile picture updated successfully!');
            closeProfilePictureModal();
            // Update the profile picture display
            const profilePictureDisplay = document.getElementById('profilePictureImage');
            profilePictureDisplay.src = data.profile_picture_url;
            profilePictureDisplay.style.display = 'block';
            document.getElementById('profilePicturePlaceholder').style.display = 'none';
        } else {
            alert(`Failed to update profile picture: ${data.error}`);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Network error. Please try again.');
    }
}