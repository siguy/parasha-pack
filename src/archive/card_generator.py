"""
Card Generator for Parasha Pack
Generates print-ready card layouts from deck data.
"""

import json
import os
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

# Try to import PIL for image generation
try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("Note: PIL not installed. Install with: pip install Pillow")


@dataclass
class PrintSpec:
    """Print specifications for cards."""
    width_inches: float = 5.0
    height_inches: float = 7.0
    dpi: int = 300
    bleed_inches: float = 0.125
    safe_zone_inches: float = 0.25

    @property
    def width_px(self) -> int:
        return int((self.width_inches + 2 * self.bleed_inches) * self.dpi)

    @property
    def height_px(self) -> int:
        return int((self.height_inches + 2 * self.bleed_inches) * self.dpi)

    @property
    def bleed_px(self) -> int:
        return int(self.bleed_inches * self.dpi)

    @property
    def safe_zone_px(self) -> int:
        return int(self.safe_zone_inches * self.dpi)


# Layout zones as percentages
LAYOUT_ZONES = {
    "image": {"top": 0, "height": 70},
    "text": {"top": 70, "height": 20},
    "footer": {"top": 90, "height": 10},
}


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


class CardLayout:
    """
    Generates card layouts for print.
    """

    def __init__(self, spec: Optional[PrintSpec] = None):
        self.spec = spec or PrintSpec()

    def create_card_template(
        self,
        border_color: str,
        card_type: str,
    ) -> Image.Image:
        """
        Create a blank card template with border.

        Args:
            border_color: Hex color for the thematic border
            card_type: Type of card (for any type-specific styling)

        Returns:
            PIL Image with the card template
        """
        if not HAS_PIL:
            raise RuntimeError("PIL is required for card generation")

        # Create image with bleed
        width = self.spec.width_px
        height = self.spec.height_px
        img = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(img)

        # Draw border (outside safe zone)
        border_rgb = hex_to_rgb(border_color)
        border_width = self.spec.safe_zone_px

        # Draw colored border rectangle
        draw.rectangle(
            [0, 0, width, height],
            fill=border_rgb
        )

        # Draw white interior
        interior_margin = border_width
        draw.rectangle(
            [
                interior_margin,
                interior_margin,
                width - interior_margin,
                height - interior_margin
            ],
            fill='white'
        )

        return img

    def add_image_zone(
        self,
        card_img: Image.Image,
        content_image: Optional[Image.Image] = None,
    ) -> Image.Image:
        """
        Add the image zone to a card (70% of card height).

        Args:
            card_img: The card template image
            content_image: Optional image to place in the zone

        Returns:
            Card image with image zone
        """
        if not HAS_PIL:
            raise RuntimeError("PIL is required")

        draw = ImageDraw.Draw(card_img)
        width, height = card_img.size
        safe = self.spec.safe_zone_px

        # Calculate image zone dimensions
        zone_height = int((height - 2 * safe) * LAYOUT_ZONES["image"]["height"] / 100)
        zone_top = safe
        zone_width = width - 2 * safe

        if content_image:
            # Resize and paste content image
            content_image = content_image.resize(
                (zone_width, zone_height),
                Image.Resampling.LANCZOS
            )
            card_img.paste(content_image, (safe, zone_top))
        else:
            # Draw placeholder
            draw.rectangle(
                [safe, zone_top, safe + zone_width, zone_top + zone_height],
                fill='#f0f0f0',
                outline='#cccccc'
            )
            # Add placeholder text
            placeholder_y = zone_top + zone_height // 2
            draw.text(
                (width // 2, placeholder_y),
                "Image Area",
                fill='#999999',
                anchor='mm'
            )

        return card_img

    def add_text_zone(
        self,
        card_img: Image.Image,
        hebrew_text: str,
        english_text: str,
        font_path: Optional[str] = None,
    ) -> Image.Image:
        """
        Add the text zone to a card (20% of card height).

        Args:
            card_img: The card image
            hebrew_text: Hebrew text with nikud
            english_text: English text
            font_path: Optional path to font file

        Returns:
            Card image with text zone
        """
        if not HAS_PIL:
            raise RuntimeError("PIL is required")

        draw = ImageDraw.Draw(card_img)
        width, height = card_img.size
        safe = self.spec.safe_zone_px

        # Calculate text zone dimensions
        zone_start = int((height - 2 * safe) * LAYOUT_ZONES["text"]["top"] / 100) + safe
        zone_height = int((height - 2 * safe) * LAYOUT_ZONES["text"]["height"] / 100)

        # Try to load fonts
        try:
            if font_path:
                font_large = ImageFont.truetype(font_path, 48)
                font_medium = ImageFont.truetype(font_path, 32)
            else:
                # Use default font
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
        except Exception:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()

        # Draw Hebrew text (centered, larger)
        hebrew_y = zone_start + zone_height // 3
        draw.text(
            (width // 2, hebrew_y),
            hebrew_text,
            fill='#333333',
            font=font_large,
            anchor='mm'
        )

        # Draw English text (centered, smaller)
        english_y = zone_start + 2 * zone_height // 3
        draw.text(
            (width // 2, english_y),
            english_text,
            fill='#666666',
            font=font_medium,
            anchor='mm'
        )

        return card_img

    def add_footer(
        self,
        card_img: Image.Image,
        card_number: str,
        card_type: str,
        action_hint: str = "",
    ) -> Image.Image:
        """
        Add the footer zone to a card (10% of card height).

        Args:
            card_img: The card image
            card_number: Card number/ID
            card_type: Type of card
            action_hint: Optional action hint (e.g., roleplay prompt indicator)

        Returns:
            Card image with footer
        """
        if not HAS_PIL:
            raise RuntimeError("PIL is required")

        draw = ImageDraw.Draw(card_img)
        width, height = card_img.size
        safe = self.spec.safe_zone_px

        # Calculate footer zone
        zone_start = int((height - 2 * safe) * LAYOUT_ZONES["footer"]["top"] / 100) + safe
        zone_height = int((height - 2 * safe) * LAYOUT_ZONES["footer"]["height"] / 100)

        # Draw divider line
        draw.line(
            [(safe, zone_start), (width - safe, zone_start)],
            fill='#cccccc',
            width=2
        )

        # Draw footer text
        footer_y = zone_start + zone_height // 2
        footer_text = f"{card_number} | {card_type.replace('_', ' ').title()}"
        if action_hint:
            footer_text += f" | {action_hint}"

        draw.text(
            (width // 2, footer_y),
            footer_text,
            fill='#999999',
            anchor='mm'
        )

        return card_img


def generate_deck_layouts(
    deck_path: str,
    output_dir: str,
    images_dir: Optional[str] = None,
) -> list:
    """
    Generate print-ready layouts for all cards in a deck.

    Args:
        deck_path: Path to deck.json file
        output_dir: Directory to save generated layouts
        images_dir: Optional directory containing card images

    Returns:
        List of generated file paths
    """
    if not HAS_PIL:
        print("PIL is required for layout generation. Install with: pip install Pillow")
        return []

    # Load deck
    with open(deck_path, 'r', encoding='utf-8') as f:
        deck = json.load(f)

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    layout = CardLayout()
    generated_files = []

    for card in deck['cards']:
        # Create template with border
        card_img = layout.create_card_template(
            border_color=deck['border_color'],
            card_type=card['card_type'],
        )

        # Load content image if available
        content_image = None
        if images_dir and card.get('image_path'):
            image_path = os.path.join(images_dir, card['image_path'])
            if os.path.exists(image_path):
                content_image = Image.open(image_path)

        # Add zones
        card_img = layout.add_image_zone(card_img, content_image)

        # Get text based on card type
        hebrew_text = card.get('title_he', '')
        english_text = card.get('title_en', '')

        if card['card_type'] == 'power_word':
            hebrew_text = card.get('hebrew_word_nikud', hebrew_text)
            english_text = card.get('english_meaning', english_text)
        elif card['card_type'] == 'action':
            english_text = card.get('english_description', english_text)[:50] + "..."

        card_img = layout.add_text_zone(card_img, hebrew_text, english_text)

        # Add footer
        action_hint = ""
        if card['card_type'] == 'action':
            action_hint = f"#{card.get('sequence_number', '')}"

        card_img = layout.add_footer(
            card_img,
            card['card_id'],
            card['card_type'],
            action_hint,
        )

        # Save
        output_path = os.path.join(output_dir, f"{card['card_id']}.png")
        card_img.save(output_path, 'PNG', dpi=(300, 300))
        generated_files.append(output_path)
        print(f"Generated: {output_path}")

    return generated_files


def generate_print_pdf(
    layout_dir: str,
    output_path: str,
    cards_per_page: int = 2,
) -> str:
    """
    Combine card layouts into a print-ready PDF.

    Args:
        layout_dir: Directory containing card PNG files
        output_path: Path for output PDF
        cards_per_page: Number of cards per page

    Returns:
        Path to generated PDF
    """
    if not HAS_PIL:
        print("PIL is required for PDF generation")
        return ""

    # Get all PNG files
    png_files = sorted(Path(layout_dir).glob("*.png"))
    if not png_files:
        print(f"No PNG files found in {layout_dir}")
        return ""

    # Load images and convert to RGB
    images = []
    for png_path in png_files:
        img = Image.open(png_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        images.append(img)

    # Save as PDF
    if images:
        images[0].save(
            output_path,
            'PDF',
            resolution=300,
            save_all=True,
            append_images=images[1:] if len(images) > 1 else []
        )
        print(f"Generated PDF: {output_path}")
        return output_path

    return ""


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python card_generator.py <deck_path> [output_dir]")
        print("Example: python card_generator.py ../decks/yitro/deck.json ../exports/yitro_layouts")
        sys.exit(1)

    deck_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "./layouts"

    files = generate_deck_layouts(deck_path, output_dir)
    print(f"\nGenerated {len(files)} card layouts")

    # Generate PDF
    pdf_path = os.path.join(output_dir, "deck.pdf")
    generate_print_pdf(output_dir, pdf_path)
