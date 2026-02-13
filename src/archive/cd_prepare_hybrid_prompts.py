
import json
import re
import sys
from pathlib import Path

def clean_prompt(prompt, card=None):
    """
    Removes specific sections from the prompt that contain text rendering instructions.
    """
    if not prompt:
        return ""
    
    # Sections to remove entirely (including the header)
    sections_to_remove = [
        r"=== EXACT TEXT TO RENDER ===[\s\S]*?(?=\n===|$)",
        r"=== COMPOSITION ===[\s\S]*?(?=\n===|$)",
        r"=== FRAME ===[\s\S]*?(?=\n===|$)",
        r"=== CARD TYPE:.*?===[\s\S]*?(?=\n===|$)" # Often contains layout info
    ]
    
    cleaned = prompt
    for pattern in sections_to_remove:
        cleaned = re.sub(pattern, "", cleaned, flags=re.MULTILINE)
        
    # Extra cleanup: Remove specific lines calling for borders or text if they missed the regex
    cleaned = re.sub(r"Border:.*", "", cleaned)
    cleaned = re.sub(r"Title Bar:.*", "", cleaned)
    
    # Remove multiple newlines left behind
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    
    # Inject "No Text" instruction AND Composition Rules
    title_info = ""
    if card:
        title_info = f"Title Context: {card.get('title_en', '')} ({card.get('title_he', '')})\n\n"

    cleaned = (
        "=== INSTRUCTION ===\n"
        "GENERATE A CLEAN ILLUSTRATION ONLY. DO NOT INCLUDE ANY TEXT, TITLES, BORDERS, OR BADGES IN THE IMAGE.\n\n"
        f"{title_info}"
        "=== COMPOSITION RULES (CRITICAL) ===\n"
        "1. VERTICAL LAYOUT: This image aspect ratio is 5:7 (Vertical).\n"
        "2. SAFE ZONE: The Top 20% and Bottom 35% of the image will be covered by text overlays.\n"
        "3. ACTION CENTER: You MUST place all faces, main characters, and key details in the CENTER 45% of the vertical space.\n"
        "4. BACKGROUND: The top and bottom edges should be sky, ground, or scenery that can be covered without losing the story.\n\n"
        "=== STYLE ===\n"
        "Vivid, high-contrast cartoon style suitable for ages 4-6.\n"
        "- Characters: Rounded, friendly shapes. Large expressive features.\n"
        "- Lines: Thick, clean black outlines (2-3px equivalent).\n"
        "- Coloring: Flat, vibrant colors with subtle shading.\n\n"
        + cleaned
    )
    
    return cleaned.strip()

def main():
    deck_path = Path("content/terumah/deck.json")
    if not deck_path.exists():
        print(f"Error: {deck_path} not found")
        return

    with open(deck_path, "r", encoding="utf-8") as f:
        deck = json.load(f)
        
    print(f"Processing deck: {deck.get('parasha_en', 'Unknown')}")
    
    count = 0
    for card in deck.get("cards", []):
        original = card.get("image_prompt", "")
        if original:
            cleaned = clean_prompt(original, card)
            card["image_prompt_clean"] = cleaned
            print(f"  Processed {card['card_id']}")
            count += 1
            
    with open(deck_path, "w", encoding="utf-8") as f:
        json.dump(deck, f, indent=2, ensure_ascii=False)
        
    print(f"Updated {count} cards in {deck_path}")

if __name__ == "__main__":
    main()
