// Translation Review JavaScript

// Translation Review Modal Functions
function openTranslationReviewModal() {
    document.getElementById('translationReviewModal').style.display = 'flex';
    // Reset form
    document.getElementById('translationReviewForm').reset();
    hideTranslationFormMessages();
    updateCharacterCounts();
}

function closeTranslationReviewModal() {
    document.getElementById('translationReviewModal').style.display = 'none';
}

function hideTranslationFormMessages() {
    document.getElementById('translationFormError').style.display = 'none';
    document.getElementById('translationFormSuccess').style.display = 'none';
}

function showTranslationFormError(message) {
    document.getElementById('translationFormErrorMessage').textContent = message;
    document.getElementById('translationFormError').style.display = 'block';
    document.getElementById('translationFormSuccess').style.display = 'none';
}

function showTranslationFormSuccess(message) {
    document.getElementById('translationFormSuccessMessage').textContent = message;
    document.getElementById('translationFormSuccess').style.display = 'block';
    document.getElementById('translationFormError').style.display = 'none';
}

function updateCharacterCounts() {
    const inputs = [
        { id: 'originalTextInput', countId: 'originalTextCount' },
        { id: 'currentTranslationInput', countId: 'currentTranslationCount' },
        { id: 'suggestedTranslationInput', countId: 'suggestedTranslationCount' },
        { id: 'contextInput', countId: 'contextCount' }
    ];

    inputs.forEach(input => {
        const element = document.getElementById(input.id);
        const countElement = document.getElementById(input.countId);

        if (element && countElement) {
            countElement.textContent = element.value.length;

            element.addEventListener('input', function() {
                countElement.textContent = this.value.length;
            });
        }
    });
}

async function submitTranslationReview() {
    const submitBtn = document.getElementById('submitTranslationBtn');
    const originalText = document.getElementById('originalTextInput').value.trim();
    const currentTranslation = document.getElementById('currentTranslationInput').value.trim();
    const suggestedTranslation = document.getElementById('suggestedTranslationInput').value.trim();
    const targetLanguage = document.getElementById('targetLanguageSelect').value;
    const context = document.getElementById('contextInput').value.trim();

    // Validation
    if (!originalText) {
        showTranslationFormError('Please enter the original text.');
        return;
    }

    if (!suggestedTranslation) {
        showTranslationFormError('Please enter your suggested translation.');
        return;
    }

    if (!targetLanguage) {
        showTranslationFormError('Please select a target language.');
        return;
    }

    if (originalText.length > 500) {
        showTranslationFormError('Original text must be less than 500 characters.');
        return;
    }

    if (suggestedTranslation.length > 500) {
        showTranslationFormError('Suggested translation must be less than 500 characters.');
        return;
    }

    // Disable submit button
    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting...';

    try {
        const response = await fetch('/api/translations/submit-fix', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                original_text: originalText,
                current_translation: currentTranslation || null,
                suggested_translation: suggestedTranslation,
                target_language: targetLanguage,
                context: context || null
            })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showTranslationFormSuccess('Thank you! Your translation has been submitted for review. Our team will evaluate it and integrate it into the system if approved.');

            // Reset form after successful submission
            setTimeout(() => {
                document.getElementById('translationReviewForm').reset();
                updateCharacterCounts();
            }, 2000);
        } else {
            showTranslationFormError(data.error || 'Failed to submit translation. Please try again.');
        }
    } catch (error) {
        console.error('Error submitting translation:', error);
        showTranslationFormError('Network error. Please check your connection and try again.');
    } finally {
        // Re-enable submit button
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit Translation';
    }
}

// Add event listeners for character counting
document.addEventListener('DOMContentLoaded', () => {
    updateCharacterCounts();
});