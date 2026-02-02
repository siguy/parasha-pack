/**
 * Parasha Pack Review Workspace
 * Interactive card deck review interface
 */

// State
let currentDeck = null;
let currentCardId = null;
let feedbackData = null;
let currentDeckBasePath = null;  // Base path for resolving image URLs
let characterReferences = null;  // Character reference data from manifest
let currentCharacterKey = null;  // Currently selected character
let currentRefType = 'identity'; // Currently selected reference type

// Available decks (will be populated from file system in production)
const availableDecks = [
    { id: 'yitro', name: 'Parshat Yitro', path: '../decks/yitro/deck.json', feedbackPath: '../decks/yitro/feedback.json', basePath: '../decks/yitro/' },
    { id: 'beshalach', name: 'Parshat Beshalach', path: '../decks/beshalach/deck.json', feedbackPath: '../decks/beshalach/feedback.json', basePath: '../decks/beshalach/' }
];

// DOM Elements
const deckSelect = document.getElementById('deck-select');
const loadDeckBtn = document.getElementById('load-deck-btn');
const exportFeedbackBtn = document.getElementById('export-feedback-btn');
const deckInfo = document.getElementById('deck-info');
const cardGallery = document.getElementById('card-gallery');
const cardGrid = document.getElementById('card-grid');
const cardDetail = document.getElementById('card-detail');
const closeDetailBtn = document.getElementById('close-detail');
const prevCardBtn = document.getElementById('prev-card-btn');
const nextCardBtn = document.getElementById('next-card-btn');
const exportModal = document.getElementById('export-modal');
const exportJson = document.getElementById('export-json');
const copyExportBtn = document.getElementById('copy-export-btn');
const closeModalBtn = document.getElementById('close-modal-btn');
const viewTabs = document.getElementById('view-tabs');
const charactersView = document.getElementById('characters-view');
const charactersGrid = document.getElementById('characters-grid');
const characterDetail = document.getElementById('character-detail');

// Initialize
document.addEventListener('DOMContentLoaded', init);

function init() {
    populateDeckSelector();
    attachEventListeners();
}

function populateDeckSelector() {
    availableDecks.forEach(deck => {
        const option = document.createElement('option');
        option.value = deck.id;
        option.textContent = deck.name;
        deckSelect.appendChild(option);
    });
}

function attachEventListeners() {
    loadDeckBtn.addEventListener('click', loadSelectedDeck);
    closeDetailBtn.addEventListener('click', closeDetail);
    prevCardBtn.addEventListener('click', showPreviousCard);
    nextCardBtn.addEventListener('click', showNextCard);
    exportFeedbackBtn.addEventListener('click', showExportModal);
    copyExportBtn.addEventListener('click', copyExportToClipboard);
    closeModalBtn.addEventListener('click', () => exportModal.classList.add('hidden'));

    // Feedback form listeners
    document.getElementById('add-feedback-btn').addEventListener('click', addFeedback);
    document.querySelectorAll('input[name="card-status"]').forEach(radio => {
        radio.addEventListener('change', updateCardStatus);
    });

    // Copy button listeners
    document.querySelectorAll('.copy-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const targetId = e.target.dataset.target;
            const text = document.getElementById(targetId).textContent;
            navigator.clipboard.writeText(text);
            e.target.textContent = 'Copied!';
            setTimeout(() => e.target.textContent = 'Copy', 2000);
        });
    });

    // Close modal on background click
    exportModal.addEventListener('click', (e) => {
        if (e.target === exportModal) {
            exportModal.classList.add('hidden');
        }
    });

    // Collapsible section headers
    document.querySelectorAll('.collapsible .section-header').forEach(header => {
        header.addEventListener('click', () => {
            header.closest('.collapsible').classList.toggle('collapsed');
        });
    });

    // View tab listeners
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => switchView(btn.dataset.view));
    });

    // Character detail close button
    document.getElementById('close-character-detail').addEventListener('click', closeCharacterDetail);

    // Reference tab listeners
    document.querySelectorAll('.ref-tab-btn').forEach(btn => {
        btn.addEventListener('click', () => switchReferenceTab(btn.dataset.ref));
    });

    // Character feedback export button
    document.getElementById('export-char-feedback').addEventListener('click', () => {
        if (currentCharacterKey) {
            generateCharacterFeedback(currentCharacterKey);
        }
    });

    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
        // Only handle arrow keys when detail panel is visible and not typing in a text field
        if (cardDetail.classList.contains('hidden')) return;
        if (e.target.tagName === 'TEXTAREA' || e.target.tagName === 'INPUT') return;

        if (e.key === 'ArrowLeft') {
            e.preventDefault();
            showPreviousCard();
        } else if (e.key === 'ArrowRight') {
            e.preventDefault();
            showNextCard();
        } else if (e.key === 'Escape') {
            e.preventDefault();
            closeDetail();
        }
    });
}

// Helper to resolve image paths relative to deck location
function resolveImagePath(imagePath) {
    if (!imagePath || !currentDeckBasePath) return null;
    return currentDeckBasePath + imagePath;
}

async function loadSelectedDeck() {
    const selectedId = deckSelect.value;
    if (!selectedId) return;

    const deckInfo = availableDecks.find(d => d.id === selectedId);
    if (!deckInfo) return;

    // Store the base path for image resolution
    currentDeckBasePath = deckInfo.basePath;

    try {
        // Load deck data
        const deckResponse = await fetch(deckInfo.path);
        currentDeck = await deckResponse.json();

        // Load feedback data
        try {
            const feedbackResponse = await fetch(deckInfo.feedbackPath);
            feedbackData = await feedbackResponse.json();
        } catch {
            // Initialize empty feedback if none exists
            feedbackData = {
                parasha: currentDeck.parasha_en,
                deck_version: currentDeck.version,
                review_date: null,
                cards: [],
                global_feedback: ''
            };
        }

        // Load character references
        await loadCharacterReferences();

        renderDeck();
        exportFeedbackBtn.disabled = false;
    } catch (error) {
        console.error('Error loading deck:', error);
        alert('Error loading deck. Check console for details.');
    }
}

function renderDeck() {
    // Show deck info
    document.getElementById('deck-title').textContent = `${currentDeck.parasha_en} (${currentDeck.parasha_he})`;
    document.getElementById('deck-ref').textContent = currentDeck.ref;
    document.getElementById('deck-card-count').textContent = `${currentDeck.card_count} cards`;
    document.getElementById('deck-theme').textContent = currentDeck.theme;
    document.getElementById('border-color-preview').style.backgroundColor = currentDeck.border_color;

    deckInfo.classList.remove('hidden');

    // Show view tabs
    viewTabs.classList.remove('hidden');

    // Render card grid
    cardGrid.innerHTML = '';
    currentDeck.cards.forEach(card => {
        const thumb = createCardThumb(card);
        cardGrid.appendChild(thumb);
    });

    cardGallery.classList.remove('hidden');
    cardDetail.classList.add('hidden');
}

function createCardThumb(card) {
    const thumb = document.createElement('div');
    thumb.className = 'card-thumb';
    thumb.dataset.cardId = card.card_id;

    // Get feedback status for this card
    const cardFeedback = feedbackData.cards.find(c => c.card_id === card.card_id);
    const status = cardFeedback?.status || 'pending';

    const imageSrc = resolveImagePath(card.image_path);
    thumb.innerHTML = `
        <div class="card-thumb-status ${status}"></div>
        <span class="card-thumb-type ${card.card_type}">${formatCardType(card.card_type)}</span>
        <div class="card-thumb-image">
            ${imageSrc
                ? `<img src="${imageSrc}" alt="${card.title_en}">`
                : `<span class="placeholder-icon">🎨</span>`
            }
        </div>
        <div class="card-thumb-title">${card.title_en}</div>
        <div class="card-thumb-title-he">${card.title_he}</div>
    `;

    thumb.addEventListener('click', () => showCardDetail(card.card_id));
    return thumb;
}

function formatCardType(type) {
    return type.replace('_', ' ');
}

function showCardDetail(cardId) {
    const card = currentDeck.cards.find(c => c.card_id === cardId);
    if (!card) return;

    currentCardId = cardId;

    // Reset collapsed sections to default state
    document.querySelectorAll('.info-section.metadata-compact, .info-section.feedback-section, .info-section.image-prompt-section').forEach(section => {
        section.classList.add('collapsed');
    });

    // Update selection in grid
    document.querySelectorAll('.card-thumb').forEach(t => t.classList.remove('selected'));
    document.querySelector(`[data-card-id="${cardId}"]`)?.classList.add('selected');

    // Populate detail panel
    document.getElementById('detail-title').textContent = `${card.card_id}: ${card.title_en} (${card.title_he})`;
    document.getElementById('detail-type').textContent = formatCardType(card.card_type);
    document.getElementById('detail-type').className = `type-badge ${card.card_type}`;

    // Preview
    const preview = document.getElementById('card-preview');
    const detailImageSrc = resolveImagePath(card.image_path);
    if (detailImageSrc) {
        preview.innerHTML = `<img src="${detailImageSrc}" alt="${card.title_en}">`;
    } else {
        preview.innerHTML = `
            <div class="preview-placeholder">
                <span>🎨</span>
                <p>No image generated yet</p>
            </div>
        `;
    }
    preview.style.borderColor = currentDeck.border_color;

    // Metadata
    renderMetadata(card);

    // Image prompt
    document.getElementById('image-prompt').textContent = card.image_prompt || 'No prompt available';

    // Teacher script
    document.getElementById('teacher-script').textContent = card.teacher_script || 'No script available';

    // Type-specific content
    renderTypeSpecific(card);

    // Feedback
    renderFeedback(cardId);

    // Update navigation button states
    updateNavigationButtons();

    cardDetail.classList.remove('hidden');
}

function getCurrentCardIndex() {
    if (!currentDeck || !currentCardId) return -1;
    return currentDeck.cards.findIndex(c => c.card_id === currentCardId);
}

function updateNavigationButtons() {
    const currentIndex = getCurrentCardIndex();
    const totalCards = currentDeck?.cards?.length || 0;

    prevCardBtn.disabled = currentIndex <= 0;
    nextCardBtn.disabled = currentIndex >= totalCards - 1;
}

function showPreviousCard() {
    const currentIndex = getCurrentCardIndex();
    if (currentIndex > 0) {
        const prevCard = currentDeck.cards[currentIndex - 1];
        showCardDetail(prevCard.card_id);
    }
}

function showNextCard() {
    const currentIndex = getCurrentCardIndex();
    if (currentIndex < currentDeck.cards.length - 1) {
        const nextCard = currentDeck.cards[currentIndex + 1];
        showCardDetail(nextCard.card_id);
    }
}

function renderMetadata(card) {
    const container = document.getElementById('metadata-content');
    let html = '';

    // Common metadata
    html += `
        <div class="metadata-item">
            <span class="metadata-label">Card ID</span>
            <span class="metadata-value">${card.card_id}</span>
        </div>
        <div class="metadata-item">
            <span class="metadata-label">Type</span>
            <span class="metadata-value">${formatCardType(card.card_type)}</span>
        </div>
    `;

    // Type-specific metadata
    switch (card.card_type) {
        case 'anchor':
            html += `
                <div class="metadata-item">
                    <span class="metadata-label">Emotional Hook</span>
                    <span class="metadata-value">${card.emotional_hook_en}</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">Border Color</span>
                    <span class="metadata-value">${card.border_color}</span>
                </div>
            `;
            break;
        case 'spotlight':
            html += `
                <div class="metadata-item">
                    <span class="metadata-label">Character</span>
                    <span class="metadata-value">${card.character_name_en}</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">Emotion Label</span>
                    <span class="metadata-value">${card.emotion_label}</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">Character Trait</span>
                    <span class="metadata-value">${card.character_trait}</span>
                </div>
            `;
            break;
        case 'action':
            html += `
                <div class="metadata-item">
                    <span class="metadata-label">Sequence #</span>
                    <span class="metadata-value"><span class="sequence-badge">${card.sequence_number}</span></span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">Hebrew Key Word</span>
                    <span class="metadata-value hebrew">${card.hebrew_key_word_nikud}</span>
                </div>
            `;
            break;
        case 'power_word':
            html += `
                <div class="metadata-item">
                    <span class="metadata-label">Hebrew Word</span>
                    <span class="metadata-value hebrew">${card.hebrew_word_nikud}</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">Transliteration</span>
                    <span class="metadata-value">${card.transliteration}</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">Meaning</span>
                    <span class="metadata-value">${card.english_meaning}</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">Is Emotion Word</span>
                    <span class="metadata-value">${card.is_emotion_word ? 'Yes' : 'No'}</span>
                </div>
            `;
            break;
    }

    container.innerHTML = html;
}

function renderTypeSpecific(card) {
    const container = document.getElementById('type-specific');
    let title = '';
    let content = '';

    switch (card.card_type) {
        case 'action':
            title = 'Action Details';
            content = `
                <p><strong>Description:</strong> ${card.english_description}</p>
                <div class="roleplay-box">${card.roleplay_prompt}</div>
            `;
            break;

        case 'thinker':
            title = 'Discussion Questions';
            content = `
                <div class="questions-list">
                    ${card.questions.map(q => `
                        <div class="question-item">
                            <div class="question-type">${q.question_type.replace('_', ' ')}</div>
                            <div class="question-text">${q.question_en}</div>
                            <div class="question-hebrew">${q.question_he}</div>
                        </div>
                    `).join('')}
                </div>
                <h4 style="margin-top: var(--spacing-md);">Feeling Faces</h4>
                <div class="feeling-faces">
                    ${card.feeling_faces.map(f => `
                        <div class="feeling-face">
                            <span class="emoji">${f.emoji}</span>
                            <span class="label">${f.label_en}</span>
                        </div>
                    `).join('')}
                </div>
            `;
            break;

        case 'power_word':
            title = 'Power Word';
            content = `
                <div class="power-word-display">
                    <div class="power-word-hebrew">${card.hebrew_word_nikud}</div>
                    <div class="power-word-transliteration">${card.transliteration}</div>
                    <div class="power-word-meaning">${card.english_meaning}</div>
                </div>
                <p style="margin-top: var(--spacing-md);"><strong>Example:</strong> ${card.example_sentence_en}</p>
                <p class="hebrew" style="direction: rtl;">${card.example_sentence_he}</p>
            `;
            break;

        case 'spotlight':
            title = 'Character Info';
            content = `
                <p>${card.character_description_en}</p>
                <p class="hebrew" style="direction: rtl; margin-top: var(--spacing-sm);">${card.character_description_he}</p>
            `;
            break;

        case 'anchor':
            title = 'Emotional Hook';
            content = `
                <p style="font-size: 1.25rem; font-weight: bold; color: var(--primary);">${card.emotional_hook_en}</p>
                <p class="hebrew" style="direction: rtl; margin-top: var(--spacing-sm);">${card.emotional_hook_he}</p>
                <p style="margin-top: var(--spacing-md);"><strong>Symbol:</strong> ${card.symbol_description}</p>
            `;
            break;
    }

    if (title) {
        container.innerHTML = `
            <h4 class="section-header">${title} <span class="collapse-icon"></span></h4>
            <div class="section-content">${content}</div>
        `;
        // Re-attach click handler for dynamically created header
        container.querySelector('.section-header').addEventListener('click', () => {
            container.classList.toggle('collapsed');
        });
    } else {
        container.innerHTML = '';
    }
}

function renderFeedback(cardId) {
    const cardFeedback = feedbackData.cards.find(c => c.card_id === cardId);

    // Set status radio
    const status = cardFeedback?.status || '';
    document.querySelectorAll('input[name="card-status"]').forEach(radio => {
        radio.checked = radio.value === status;
    });

    // Clear form
    document.getElementById('feedback-comment').value = '';

    // Render feedback list
    const feedbackList = document.getElementById('feedback-list');
    if (cardFeedback?.feedback?.length) {
        feedbackList.innerHTML = cardFeedback.feedback.map((f, index) => `
            <div class="feedback-item ${f.resolved ? 'resolved' : ''}">
                <div class="feedback-item-content">
                    <span class="feedback-category">${f.category}</span>
                    <span class="feedback-priority ${f.priority}">${f.priority}</span>
                    <p class="feedback-comment">${f.comment}</p>
                </div>
                <div class="feedback-actions">
                    <button onclick="toggleResolved('${cardId}', ${index})">${f.resolved ? 'Unresolve' : 'Resolve'}</button>
                    <button onclick="deleteFeedback('${cardId}', ${index})">Delete</button>
                </div>
            </div>
        `).join('');
    } else {
        feedbackList.innerHTML = '<p style="color: var(--text-light); font-style: italic;">No feedback yet</p>';
    }
}

function updateCardStatus(e) {
    if (!currentCardId) return;

    let cardFeedback = feedbackData.cards.find(c => c.card_id === currentCardId);
    if (!cardFeedback) {
        cardFeedback = { card_id: currentCardId, status: '', feedback: [] };
        feedbackData.cards.push(cardFeedback);
    }

    cardFeedback.status = e.target.value;
    feedbackData.review_date = new Date().toISOString().split('T')[0];

    // Update thumbnail status indicator
    const thumb = document.querySelector(`[data-card-id="${currentCardId}"] .card-thumb-status`);
    if (thumb) {
        thumb.className = `card-thumb-status ${cardFeedback.status}`;
    }

    saveFeedback();
}

function addFeedback() {
    if (!currentCardId) return;

    const category = document.getElementById('feedback-category').value;
    const comment = document.getElementById('feedback-comment').value.trim();
    const priority = document.getElementById('feedback-priority').value;

    if (!comment) {
        alert('Please enter a comment');
        return;
    }

    let cardFeedback = feedbackData.cards.find(c => c.card_id === currentCardId);
    if (!cardFeedback) {
        cardFeedback = { card_id: currentCardId, status: 'needs_revision', feedback: [] };
        feedbackData.cards.push(cardFeedback);
    }

    cardFeedback.feedback.push({ category, comment, priority, resolved: false });
    feedbackData.review_date = new Date().toISOString().split('T')[0];

    // Auto-set status to needs_revision if adding feedback
    if (!cardFeedback.status) {
        cardFeedback.status = 'needs_revision';
        document.querySelector('input[name="card-status"][value="needs_revision"]').checked = true;
    }

    saveFeedback();
    renderFeedback(currentCardId);
    document.getElementById('feedback-comment').value = '';
}

function toggleResolved(cardId, feedbackIndex) {
    const cardFeedback = feedbackData.cards.find(c => c.card_id === cardId);
    if (cardFeedback?.feedback?.[feedbackIndex]) {
        cardFeedback.feedback[feedbackIndex].resolved = !cardFeedback.feedback[feedbackIndex].resolved;
        saveFeedback();
        renderFeedback(cardId);
    }
}

function deleteFeedback(cardId, feedbackIndex) {
    const cardFeedback = feedbackData.cards.find(c => c.card_id === cardId);
    if (cardFeedback?.feedback) {
        cardFeedback.feedback.splice(feedbackIndex, 1);
        saveFeedback();
        renderFeedback(cardId);
    }
}

function saveFeedback() {
    // In a real app, this would save to the server/file
    // For now, we just update the in-memory data
    console.log('Feedback saved:', feedbackData);
}

function closeDetail() {
    cardDetail.classList.add('hidden');
    document.querySelectorAll('.card-thumb').forEach(t => t.classList.remove('selected'));
    currentCardId = null;
}

function showExportModal() {
    // Generate export JSON
    const exportData = {
        parasha: feedbackData.parasha,
        deck_version: feedbackData.deck_version,
        review_date: feedbackData.review_date || new Date().toISOString().split('T')[0],
        cards: feedbackData.cards.filter(c => c.status || c.feedback?.length),
        global_feedback: feedbackData.global_feedback
    };

    exportJson.textContent = JSON.stringify(exportData, null, 2);
    exportModal.classList.remove('hidden');
}

function copyExportToClipboard() {
    navigator.clipboard.writeText(exportJson.textContent);
    copyExportBtn.textContent = 'Copied!';
    setTimeout(() => copyExportBtn.textContent = 'Copy to Clipboard', 2000);
}

// ==========================================
// Character Reference Functions
// ==========================================

async function loadCharacterReferences() {
    const manifestPath = currentDeckBasePath + 'references/manifest.json';
    try {
        const response = await fetch(manifestPath);
        characterReferences = await response.json();
    } catch (error) {
        console.log('No character references found:', error);
        characterReferences = null;
    }
}

function switchView(viewName) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn =>
        btn.classList.toggle('active', btn.dataset.view === viewName));

    // Toggle views
    cardGallery.classList.toggle('hidden', viewName !== 'cards');
    charactersView.classList.toggle('hidden', viewName !== 'characters');

    // Hide detail panels when switching views
    cardDetail.classList.add('hidden');
    characterDetail.classList.add('hidden');

    // Render characters if switching to that view
    if (viewName === 'characters') {
        renderCharacters();
    }
}

function renderCharacters() {
    if (!characterReferences) {
        charactersGrid.innerHTML = '<p style="color: var(--text-light); font-style: italic;">No character references available for this deck.</p>';
        return;
    }

    charactersGrid.innerHTML = '';

    for (const [charKey, refs] of Object.entries(characterReferences)) {
        const card = createCharacterCard(charKey, refs);
        charactersGrid.appendChild(card);
    }
}

function createCharacterCard(charKey, refs) {
    const card = document.createElement('div');
    card.className = 'character-card';
    card.dataset.character = charKey;

    // Resolve the identity image path (need to go up one level from review-site)
    const identityPath = '../' + refs.identity;

    card.innerHTML = `
        <img src="${identityPath}" alt="${charKey} identity" onerror="this.style.display='none'">
        <div class="character-card-name">${charKey}</div>
    `;

    card.addEventListener('click', () => showCharacterDetail(charKey));
    return card;
}

function showCharacterDetail(charKey) {
    if (!characterReferences || !characterReferences[charKey]) return;

    currentCharacterKey = charKey;
    currentRefType = 'identity';

    // Update character name
    document.getElementById('character-name').textContent = charKey.charAt(0).toUpperCase() + charKey.slice(1);

    // Reset reference tabs
    document.querySelectorAll('.ref-tab-btn').forEach(btn =>
        btn.classList.toggle('active', btn.dataset.ref === 'identity'));

    // Show identity image by default
    updateReferenceImage(charKey, 'identity');

    // Load character details from deck
    renderCharacterDetails(charKey);

    characterDetail.classList.remove('hidden');
}

function switchReferenceTab(refType) {
    if (!currentCharacterKey) return;

    currentRefType = refType;

    // Update tab buttons
    document.querySelectorAll('.ref-tab-btn').forEach(btn =>
        btn.classList.toggle('active', btn.dataset.ref === refType));

    // Update image
    updateReferenceImage(currentCharacterKey, refType);
}

function updateReferenceImage(charKey, refType) {
    const container = document.getElementById('character-ref-image');
    const refs = characterReferences[charKey];

    if (!refs || !refs[refType]) {
        container.innerHTML = '<div class="ref-image-placeholder"><p>No image available</p></div>';
        return;
    }

    // Resolve path (go up one level from review-site)
    const imagePath = '../' + refs[refType];

    container.innerHTML = `<img src="${imagePath}" alt="${charKey} ${refType}" onerror="this.parentElement.innerHTML='<div class=\\'ref-image-placeholder\\'><p>Image not found</p></div>'">`;
}

function renderCharacterDetails(charKey) {
    const container = document.getElementById('character-details');

    if (!currentDeck) {
        container.innerHTML = '';
        return;
    }

    // Find cards featuring this character
    const characterCards = currentDeck.cards.filter(card => {
        // Check spotlight cards
        if (card.card_type === 'spotlight' && card.character_name_en?.toLowerCase() === charKey.toLowerCase()) {
            return true;
        }
        // Check action cards that might feature the character
        if (card.card_type === 'action' && card.image_prompt?.toLowerCase().includes(charKey.toLowerCase())) {
            return true;
        }
        return false;
    });

    let html = '<h4>Character in Deck</h4>';

    if (characterCards.length === 0) {
        html += '<p style="color: var(--text-light);">No cards found featuring this character.</p>';
    } else {
        html += '<div class="character-appearances">';

        // Show character trait from spotlight card if available
        const spotlightCard = characterCards.find(c => c.card_type === 'spotlight');
        if (spotlightCard) {
            html += `
                <div class="appearance-item">
                    <span class="card-type">Trait</span>
                    <span class="card-title">${spotlightCard.character_trait || spotlightCard.character_description_en}</span>
                </div>
            `;
        }

        // List all appearances
        characterCards.forEach(card => {
            html += `
                <div class="appearance-item">
                    <span class="card-type">${formatCardType(card.card_type)}</span>
                    <span class="card-title">${card.title_en}</span>
                </div>
            `;
        });

        html += '</div>';
    }

    container.innerHTML = html;
}

function closeCharacterDetail() {
    characterDetail.classList.add('hidden');
    currentCharacterKey = null;
}

function generateCharacterFeedback(charKey) {
    if (!characterReferences || !characterReferences[charKey]) return;

    const refs = characterReferences[charKey];
    const charName = charKey.charAt(0).toUpperCase() + charKey.slice(1);

    const text = `## Character Feedback: ${charName}

**Deck:** ${currentDeck?.parasha_en || 'Unknown'}

**Reference Images:**
- Identity: ${refs.identity}
- Expressions: ${refs.expressions}
- Turnaround: ${refs.turnaround}
- Poses: ${refs.poses}

**Feedback:**
[Enter your feedback here]

---
*Copy this to Claude for character revisions*`;

    navigator.clipboard.writeText(text).then(() => {
        const btn = document.getElementById('export-char-feedback');
        btn.textContent = 'Copied!';
        setTimeout(() => btn.textContent = 'Copy Feedback for Claude', 2000);
    });
}

// Make functions available globally for inline event handlers
window.toggleResolved = toggleResolved;
window.deleteFeedback = deleteFeedback;
