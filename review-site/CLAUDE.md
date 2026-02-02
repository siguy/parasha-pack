# Review Site Documentation

Web-based interface for reviewing card decks and providing feedback.

## Files

| File | Purpose |
|------|---------|
| `index.html` | Main HTML structure |
| `styles.css` | CSS styling with design system |
| `app.js` | JavaScript application logic |

## Usage

1. Open `index.html` in a web browser
2. Select a deck from the dropdown
3. Click "Load Deck"
4. Browse cards and add feedback
5. Export feedback for Claude revisions

## Features

### Card Gallery View
- Grid of card thumbnails
- Status indicators (pending, approved, needs revision)
- Card type badges
- Click to view details

### Character References View
- Grid of character identity thumbnails
- Click to view all reference sheets
- Switch between identity/expressions/turnaround/poses
- Copy feedback template for Claude

### Card Detail Panel
- Large image preview
- Metadata display
- Image prompt (with copy button)
- Teacher script
- Type-specific content
- Feedback form
- Previous/Next navigation

### Keyboard Shortcuts
- `←` / `→` - Navigate between cards
- `Escape` - Close detail panel

## Architecture

### State Variables (app.js)

```javascript
let currentDeck = null;           // Loaded deck data
let currentCardId = null;         // Selected card ID
let feedbackData = null;          // Feedback for current deck
let currentDeckBasePath = null;   // Path for resolving images
let characterReferences = null;   // Character manifest data
let currentCharacterKey = null;   // Selected character
let currentRefType = 'identity';  // Selected reference type
```

### Key Functions

**Deck Loading:**
- `loadSelectedDeck()` - Fetches deck.json and feedback.json
- `loadCharacterReferences()` - Fetches references/manifest.json
- `renderDeck()` - Renders deck info and card grid

**Card Display:**
- `createCardThumb(card)` - Creates thumbnail element
- `showCardDetail(cardId)` - Opens detail panel
- `renderMetadata(card)` - Displays card metadata
- `renderTypeSpecific(card)` - Displays type-specific content

**Navigation:**
- `showPreviousCard()` / `showNextCard()` - Navigate cards
- `switchView(viewName)` - Switch between cards/characters views
- `closeDetail()` - Close detail panel

**Character References:**
- `renderCharacters()` - Renders character grid
- `createCharacterCard(charKey, refs)` - Creates character thumbnail
- `showCharacterDetail(charKey)` - Opens character panel
- `switchReferenceTab(refType)` - Switch reference type
- `updateReferenceImage(charKey, refType)` - Update displayed image
- `renderCharacterDetails(charKey)` - Show character appearances

**Feedback:**
- `renderFeedback(cardId)` - Display feedback list
- `addFeedback()` - Add new feedback item
- `updateCardStatus(e)` - Update approved/needs_revision
- `toggleResolved(cardId, index)` - Mark feedback resolved
- `deleteFeedback(cardId, index)` - Remove feedback item
- `saveFeedback()` - Persist feedback (currently console.log)

**Export:**
- `showExportModal()` - Open export dialog
- `copyExportToClipboard()` - Copy feedback JSON
- `generateCharacterFeedback(charKey)` - Copy character feedback template

## CSS Design System

### Custom Properties

```css
/* Colors */
--primary: #5c2d91;        /* Royal purple */
--primary-light: #7b4aad;
--secondary: #c9a227;      /* Gold accent */
--background: #f5f5f5;
--surface: #ffffff;
--border: #e0e0e0;
--success: #4caf50;
--warning: #ff9800;
--error: #f44336;

/* Card Type Colors */
--type-anchor: #1e3a5f;
--type-spotlight: #d4a84b;
--type-action: #2d8a8a;
--type-thinker: #5c2d91;
--type-power-word: #a52a2a;

/* Spacing */
--spacing-xs: 4px;
--spacing-sm: 8px;
--spacing-md: 16px;
--spacing-lg: 24px;
--spacing-xl: 32px;
```

### Key CSS Classes

**Layout:**
- `.main-content` - Max-width container
- `.deck-selector` - Top toolbar
- `.view-tabs` - Cards/Characters tabs
- `.deck-info` - Deck metadata bar

**Card Gallery:**
- `.card-gallery` - Gallery container
- `.card-grid` - CSS Grid for thumbnails
- `.card-thumb` - Individual card thumbnail
- `.card-thumb-status` - Status indicator dot
- `.card-thumb-type` - Type badge

**Card Detail:**
- `.card-detail` - Detail panel container
- `.detail-header` - Title and navigation
- `.detail-content` - Two-column layout
- `.info-column` - Left column with metadata
- `.preview-column` - Right column with image
- `.info-section` - Content sections

**Characters:**
- `.characters-view` - Characters section
- `.characters-grid` - CSS Grid for characters
- `.character-card` - Character thumbnail
- `.character-detail` - Character panel
- `.ref-tabs` - Reference type tabs
- `.ref-image-container` - Reference image display

**Feedback:**
- `.feedback-section` - Feedback form area
- `.feedback-status` - Approve/Revise radios
- `.feedback-form` - Category, comment, priority
- `.feedback-list` - List of feedback items
- `.feedback-item` - Individual feedback

## HTML Structure

```html
<body>
  <header class="header">...</header>

  <main class="main-content">
    <!-- Deck Selector toolbar -->
    <section class="deck-selector">...</section>

    <!-- View Tabs (Cards | Characters) -->
    <nav class="view-tabs">...</nav>

    <!-- Deck Info Bar -->
    <section id="deck-info">...</section>

    <!-- Card Detail Panel -->
    <section id="card-detail">...</section>

    <!-- Card Gallery -->
    <section id="card-gallery">...</section>

    <!-- Characters View -->
    <section id="characters-view">...</section>

    <!-- Character Detail Panel -->
    <section id="character-detail">...</section>

    <!-- Export Modal -->
    <div id="export-modal">...</div>
  </main>

  <footer class="footer">...</footer>
</body>
```

## Adding New Features

### Add a New View Tab

1. Add button to `.view-tabs` in index.html:
   ```html
   <button class="tab-btn" data-view="newview">New View</button>
   ```

2. Add section in index.html:
   ```html
   <section id="newview-view" class="newview-view hidden">...</section>
   ```

3. Add CSS styles in styles.css

4. Update `switchView()` in app.js to handle the new view

### Add New Card Metadata

1. Update `renderMetadata(card)` in app.js to display new field
2. Add styling if needed in styles.css

### Add New Feedback Category

1. Add option to feedback-category select in index.html:
   ```html
   <option value="newcategory">New Category</option>
   ```

## Available Decks

Configured in `availableDecks` array in app.js:

```javascript
const availableDecks = [
    {
        id: 'yitro',
        name: 'Parshat Yitro',
        path: '../decks/yitro/deck.json',
        feedbackPath: '../decks/yitro/feedback.json',
        basePath: '../decks/yitro/'
    }
];
```

To add a new deck, add an entry to this array.

## Export Format

The exported feedback JSON for Claude:

```json
{
  "parasha": "Yitro",
  "deck_version": "2.0",
  "review_date": "2024-01-15",
  "cards": [
    {
      "card_id": "spotlight_1",
      "status": "needs_revision",
      "feedback": [
        {
          "category": "visual",
          "comment": "Moses's beard should be grayer",
          "priority": "medium",
          "resolved": false
        }
      ]
    }
  ],
  "global_feedback": ""
}
```

## Character Feedback Template

When "Copy Feedback for Claude" is clicked:

```markdown
## Character Feedback: Moses

**Deck:** Yitro

**Reference Images:**
- Identity: decks/yitro/references/moses_identity.png
- Expressions: decks/yitro/references/moses_expressions.png
- Turnaround: decks/yitro/references/moses_turnaround.png
- Poses: decks/yitro/references/moses_poses.png

**Feedback:**
[Enter your feedback here]

---
*Copy this to Claude for character revisions*
```
