<script>
// 🎯 UI STATE MICROSERVICE - Single Responsibility: UI state management
// Handles: Form validation, character counters, UI updates

function updateCharacterCounters() {
    const roomNameInput = document.getElementById('roomNameInput');
    const roomDescInput = document.getElementById('roomDescriptionInput');
    const welcomeInput = document.getElementById('welcomeMessage');
    
    if (roomNameInput) {
        roomNameInput.addEventListener('input', function() {
            const counter = document.getElementById('nameCounter');
            if (counter) {
                counter.textContent = `${this.value.length}/100`;
            }
        });
    }
    
    if (roomDescInput) {
        roomDescInput.addEventListener('input', function() {
            const counter = document.getElementById('descCounter');
            if (counter) {
                counter.textContent = `${this.value.length}/300`;
            }
        });
    }
    
    if (welcomeInput) {
        welcomeInput.addEventListener('input', function() {
            const counter = document.getElementById('welcomeCounter');
            if (counter) {
                counter.textContent = `${this.value.length}/200`;
            }
        });
    }
}

function handleRoomTypeSelection() {
    document.querySelectorAll('input[name="roomType"]').forEach(radio => {
        radio.addEventListener('change', function() {
            // Update card styles
            document.querySelectorAll('.roomTypeCard').forEach(card => {
                card.classList.remove('border-primary', 'border-blue-500');
                card.classList.add('border-transparent');
            });
            
            const card = this.parentElement.querySelector('.roomTypeCard');
            if (this.value === 'private') {
                card.classList.add('border-primary');
            } else {
                card.classList.add('border-blue-500');
            }
        });
    });
}

function handleThemeSelection() {
    document.querySelectorAll('input[name="roomTheme"]').forEach(radio => {
        radio.addEventListener('change', function() {
            // Update card styles
            document.querySelectorAll('.themeCard').forEach(card => {
                card.classList.remove('border-primary', 'border-blue-500', 'border-purple-500');
                card.classList.add('border-transparent');
            });
            
            const card = this.parentElement.querySelector('.themeCard');
            if (this.value === 'default') {
                card.classList.add('border-primary');
            } else if (this.value === 'blue') {
                card.classList.add('border-blue-500');
            } else if (this.value === 'purple') {
                card.classList.add('border-purple-500');
            }
        });
    });
}
</script>