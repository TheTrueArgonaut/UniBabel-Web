<script>
// 🎯 MODAL MANAGER MICROSERVICE - Single Responsibility: Modal workflow management
// Handles: Modal state, multi-step workflow, form management

let currentStep = 'initial';
let selectedRoomIcon = '🏠';

function showCreateRoomModal() {
    document.getElementById('createRoomModal').classList.remove('hidden');
    resetModalState();
}

function hideCreateRoomModal() {
    document.getElementById('createRoomModal').classList.add('hidden');
    resetModalState();
}

function resetModalState() {
    currentStep = 'initial';
    selectedRoomIcon = '🏠';
    
    // Show initial choice, hide steps
    document.getElementById('initialChoice').classList.remove('hidden');
    document.getElementById('step1').classList.add('hidden');
    document.getElementById('step2').classList.add('hidden');
    document.getElementById('step3').classList.add('hidden');
    document.getElementById('progressIndicator').style.display = 'none';
    
    // Reset form
    document.getElementById('roomNameInput').value = '';
    document.getElementById('roomDescriptionInput').value = '';
    document.getElementById('welcomeMessage').value = '';
    document.getElementById('voiceChatEnabled').checked = false;
    document.getElementById('contentModeration').checked = true;
    document.getElementById('anyoneCanInvite').checked = false;
    document.getElementById('fileUploads').checked = true;
    
    // Reset counters
    updateCharacterCounters();
    
    // Reset modal title
    document.getElementById('modalTitle').textContent = 'Create or Join Room';
    document.getElementById('modalSubtitle').textContent = 'Choose how you want to connect';
}

function showModalTab(tabName) {
    const joinTab = document.getElementById('joinTab');
    const createTab = document.getElementById('createTab');
    const joinRoomContent = document.getElementById('joinRoomContent');
    const createRoomContent = document.getElementById('createRoomContent');
    
    if (tabName === 'join') {
        joinTab.classList.add('border-primary', 'text-primary', 'bg-primary/10');
        joinTab.classList.remove('border-transparent', 'text-gray-400');
        createTab.classList.remove('border-primary', 'text-primary', 'bg-primary/10');
        createTab.classList.add('border-transparent', 'text-gray-400');
        joinRoomContent.classList.remove('hidden');
        createRoomContent.classList.add('hidden');
    } else if (tabName === 'create') {
        createTab.classList.add('border-primary', 'text-primary', 'bg-primary/10');
        createTab.classList.remove('border-transparent', 'text-gray-400');
        joinTab.classList.remove('border-primary', 'text-primary', 'bg-primary/10');
        joinTab.classList.add('border-transparent', 'text-gray-400');
        createRoomContent.classList.remove('hidden');
        joinRoomContent.classList.add('hidden');
    }
}

function startRoomCreation() {
    currentStep = 'step1';
    showStep('step1');
    updateProgressIndicator(1);
    
    document.getElementById('modalTitle').textContent = 'Create Your Room';
    document.getElementById('modalSubtitle').textContent = 'Step 1 of 3 - Basic Information';
}

function goToStep1() {
    currentStep = 'step1';
    showStep('step1');
    updateProgressIndicator(1);
    document.getElementById('modalSubtitle').textContent = 'Step 1 of 3 - Basic Information';
}

function goToStep2() {
    // Validate step 1
    const roomName = document.getElementById('roomNameInput').value.trim();
    if (!roomName) {
        alert('Please enter a room name');
        return;
    }
    
    currentStep = 'step2';
    showStep('step2');
    updateProgressIndicator(2);
    document.getElementById('modalSubtitle').textContent = 'Step 2 of 3 - Room Settings';
}

function goToStep3() {
    currentStep = 'step3';
    showStep('step3');
    updateProgressIndicator(3);
    document.getElementById('modalSubtitle').textContent = 'Step 3 of 3 - Customize (Optional)';
}

function showStep(stepId) {
    // Hide all content
    document.getElementById('initialChoice').classList.add('hidden');
    document.getElementById('step1').classList.add('hidden');
    document.getElementById('step2').classList.add('hidden');
    document.getElementById('step3').classList.add('hidden');
    
    // Show target step
    document.getElementById(stepId).classList.remove('hidden');
    document.getElementById('progressIndicator').style.display = 'block';
}

function updateProgressIndicator(step) {
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const step1Label = document.getElementById('step1Label');
    const step2Label = document.getElementById('step2Label');
    const step3Label = document.getElementById('step3Label');
    
    // Update progress bar
    const percentage = (step / 3) * 100;
    progressBar.style.width = percentage + '%';
    progressText.textContent = `Step ${step} of 3`;
    
    // Update step labels
    step1Label.className = step >= 1 ? 'text-primary font-medium' : 'text-gray-500';
    step2Label.className = step >= 2 ? 'text-primary font-medium' : 'text-gray-500';
    step3Label.className = step >= 3 ? 'text-primary font-medium' : 'text-gray-500';
}

function selectRoomIcon(icon) {
    selectedRoomIcon = icon;
    
    // Update button styles
    document.querySelectorAll('.roomIconBtn').forEach(btn => {
        btn.classList.remove('border-primary');
        btn.classList.add('border-transparent');
    });
    
    event.target.classList.add('border-primary');
    event.target.classList.remove('border-transparent');
}

// Initialize modal event handlers
document.addEventListener('DOMContentLoaded', function() {
    updateCharacterCounters();
    handleRoomTypeSelection();
    handleThemeSelection();
});

// Click outside modal to close
document.getElementById('createRoomModal').addEventListener('click', function(e) {
    if (e.target === this) {
        hideCreateRoomModal();
    }
});

// Escape key to close modal
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        hideCreateRoomModal();
    }
});
</script>