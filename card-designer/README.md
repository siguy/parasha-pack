# Parasha Pack Card Designer

The **Card Designer** is a Next.js application that programmatically assembles high-resolution card images using React components. It serves as "Agent 09" in the deck creation pipeline.

## 🚀 Getting Started

1.  **Run the Designer:**
    ```bash
    npm run dev
    ```
2.  **Open the Visualizer:**
    - Go to [http://localhost:3000/purim](http://localhost:3000/purim) to see the Purim deck.
    - Go to [http://localhost:3000/noah](http://localhost:3000/noah) (etc.) for other decks if configured.

## 📂 Project Structure

### content/ (The Data)

This is where the card data lives.

- `content/[deck_name]/deck.json`: **Crucial.** Defines every card, its text, stats, and image path.
- `content/[deck_name]/images/`: Logic-free image storage. The app serves these files via API.

### components/cards/ (The Templates)

The React components that define the look of each card type.

- `StoryCard.tsx`: Standard narrative cards.
- `SpotlightCard.tsx`: Character focus cards.
- `ConnectionCard.tsx`: Discussion/Emoji cards.
- `CardFrame.tsx`: The shared border/container logic.

### app/[deck]/ (The Page)

- `page.tsx`: The logic that reads the JSON and renders the list of cards.

## 🛠 making Changes

- **To change text:** Edit `content/[deck]/deck.json`.
- **To change layout:** Edit `components/cards/[CardType].tsx`.
- **To add a new deck:** Create a folder in `content/` and add a `deck.json`.

## 🎨 Styles & Vibe

- **Tailwind CSS:** Used for all styling.
- **Fonts:** Configured in `app/layout.tsx` (Outfit, Frank Ruhl Libre).
- **Design System:** Glassmorphism, Rounded Corners (24px), dynamic gradients.
