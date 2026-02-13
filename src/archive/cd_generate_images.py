#!/usr/bin/env python3
"""
Generate images for Parasha Pack cards using Google Gemini.

Usage:
    export GEMINI_API_KEY="your-api-key"
    python generate_images.py ../decks/yitro/deck.json

With consistency review:
    python generate_images.py ../decks/yitro/deck.json --review
    python generate_images.py ../decks/yitro/deck.json --review --max-attempts 3

Get your API key at: https://aistudio.google.com/app/apikey
"""

import argparse
import json
import os
import shutil
import sys
import time
import urllib.request
import urllib.error
import base64
from dataclasses import asdict
from pathlib import Path
from typing import List, Dict, Optional


def load_reference_images(deck_path: Path, prompt: str) -> List[Dict]:
    """
    Load character reference images that match characters mentioned in the prompt.

    Supports two path formats:
    1. Canonical library: "characters/moses/middle_identity.png" (resolved from project root)
    2. Legacy local: "decks/yitro/references/moses_identity.png" (resolved from deck's references/)

    Args:
        deck_path: Path to the deck.json file
        prompt: The image generation prompt

    Returns:
        List of image parts for the API payload
    """
    references_dir = deck_path.parent / "references"
    manifest_path = references_dir / "manifest.json"

    if not manifest_path.exists():
        return []

    # Project root is parent of the deck directory (decks/yitro → parasha-pack)
    project_root = deck_path.parent.parent.parent

    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    image_parts = []
    prompt_lower = prompt.lower()

    for character_key, refs in manifest.items():
        # Check if character is mentioned in the prompt
        # Look for the character key or common variations
        if character_key.lower() in prompt_lower:
            identity_rel_path = refs.get("identity", "")
            identity_path = None

            # Try 1: Resolve from project root (canonical library format)
            # Paths like "characters/moses/middle_identity.png"
            if identity_rel_path.startswith("characters/"):
                candidate = project_root / identity_rel_path
                if candidate.exists():
                    identity_path = candidate

            # Try 2: Resolve from project root (legacy deck-relative format)
            # Paths like "decks/purim/references/haman_identity.png"
            if identity_path is None and identity_rel_path.startswith("decks/"):
                candidate = project_root / identity_rel_path
                if candidate.exists():
                    identity_path = candidate

            # Try 3: Fall back to local references directory (filename only)
            if identity_path is None:
                identity_filename = Path(identity_rel_path).name
                candidate = references_dir / identity_filename
                if candidate.exists():
                    identity_path = candidate

            if identity_path and identity_path.exists():
                with open(identity_path, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')

                image_parts.append({
                    "inlineData": {
                        "mimeType": "image/png",
                        "data": image_data
                    }
                })
                stage = refs.get("stage", "")
                stage_info = f" ({stage})" if stage else ""
                print(f"    [REF] Including {character_key}{stage_info} reference")
            else:
                print(f"    [WARN] Reference not found: {identity_rel_path}")

    return image_parts


def generate_image_nano_banana(
    prompt: str,
    api_key: str,
    output_path: str,
    aspect_ratio: str = "3:4",
    reference_images: Optional[List[Dict]] = None
) -> bool:
    """
    Generate an image using Nano Banana Pro model (best for children's book style).

    Args:
        prompt: The image generation prompt
        api_key: Gemini API key
        output_path: Path to save the generated image
        aspect_ratio: Aspect ratio (default 3:4 for cards)
        reference_images: Optional list of reference image parts for character consistency

    Returns:
        True if successful, False otherwise
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/nano-banana-pro-preview:generateContent?key={api_key}"

    # Build parts list: reference images first, then the prompt
    parts = []

    if reference_images:
        # Add instruction for using references
        parts.append({
            "text": "Use these character reference images to maintain visual consistency. The characters in the generated image should match these references exactly (same clothing, facial features, colors):\n"
        })
        parts.extend(reference_images)
        parts.append({"text": "\n\nNow generate this card image:\n\n" + prompt})
    else:
        parts.append({"text": prompt})

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE", "TEXT"],
            "imageConfig": {"aspectRatio": aspect_ratio}
        }
    }

    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method='POST')

        with urllib.request.urlopen(req, timeout=180) as response:
            result = json.loads(response.read().decode())

        if "candidates" in result:
            for candidate in result["candidates"]:
                for part in candidate.get("content", {}).get("parts", []):
                    if "inlineData" in part:
                        image_data = part["inlineData"].get("data")
                        if image_data:
                            with open(output_path, 'wb') as f:
                                f.write(base64.b64decode(image_data))
                            return True

        print(f"  No image in response")
        return False

    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        print(f"  HTTP Error {e.code}: {error_body[:200]}")
        return False
    except Exception as e:
        print(f"  Error: {e}")
        return False


def generate_image_imagen(prompt: str, api_key: str, output_path: str) -> bool:
    """
    Generate an image using Google Imagen 4.0 model (legacy).
    Note: Prefer nano-banana for better children's book style results.
    Note: Imagen does not support reference images.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict?key={api_key}"

    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "3:4",
            "personGeneration": "allow_adult",
            "safetySetting": "block_low_and_above"
        }
    }

    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method='POST')

        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode())

        if "predictions" in result and len(result["predictions"]) > 0:
            image_data = result["predictions"][0].get("bytesBase64Encoded")
            if image_data:
                with open(output_path, 'wb') as f:
                    f.write(base64.b64decode(image_data))
                return True

        print(f"  No image in response: {result}")
        return False

    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        print(f"  HTTP Error {e.code}: {error_body[:200]}")
        return False
    except Exception as e:
        print(f"  Error: {e}")
        return False


def generate_image_gemini_flash(prompt: str, api_key: str, output_path: str) -> bool:
    """
    Generate an image using Gemini Flash model with image generation.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp-image-generation:generateContent?key={api_key}"

    payload = {
        "contents": [{
            "parts": [{"text": f"Generate an image: {prompt}"}]
        }],
        "generationConfig": {
            "responseModalities": ["IMAGE", "TEXT"]
        }
    }

    headers = {"Content-Type": "application/json"}

    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')

        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode())

        # Extract image from response
        if "candidates" in result:
            for candidate in result["candidates"]:
                content = candidate.get("content", {})
                for part in content.get("parts", []):
                    if "inlineData" in part:
                        image_data = part["inlineData"].get("data")
                        if image_data:
                            image_bytes = base64.b64decode(image_data)
                            with open(output_path, 'wb') as f:
                                f.write(image_bytes)
                            return True

        print(f"  No image in response")
        return False

    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        print(f"  HTTP Error {e.code}: {error_body[:200]}")
        return False
    except Exception as e:
        print(f"  Error: {e}")
        return False


def review_generated_image(
    deck_path: Path,
    card: dict,
    api_key: str,
    verbose: bool = False
) -> Optional[dict]:
    """
    Review a generated image for character consistency.
    Returns review result dict or None if no characters to review.
    """
    try:
        from consistency_reviewer import review_card, update_learnings
        result = review_card(deck_path, card, api_key, verbose)
        return result
    except ImportError:
        print("  [WARN] consistency_reviewer not available, skipping review")
        return None
    except Exception as e:
        print(f"  [WARN] Review failed: {e}")
        return None


def get_learned_reinforcements(deck_path: Path, card: dict) -> List[str]:
    """
    Get prompt reinforcements based on learned failure patterns.
    """
    try:
        from consistency_reviewer import get_prompt_reinforcements, extract_characters_from_prompt

        project_root = deck_path.parent.parent.parent
        prompt = card.get("image_prompt", "")

        # Get characters from prompt
        manifest_path = deck_path.parent / "references" / "manifest.json"
        known_characters = set()
        if manifest_path.exists():
            with open(manifest_path, 'r') as f:
                known_characters = set(json.load(f).keys())

        from consistency_reviewer import extract_characters_from_prompt
        characters = extract_characters_from_prompt(prompt, known_characters)

        # Get reinforcements for each character
        reinforcements = []
        for char in characters:
            reinforcements.extend(get_prompt_reinforcements(char, project_root))

        return reinforcements
    except Exception:
        return []


def strengthen_prompt_from_review(prompt: str, review_result: dict) -> str:
    """
    Add reinforcements to prompt based on review failures.
    """
    if not review_result:
        return prompt

    reinforcements = []

    for char_review in review_result.get("characters", []):
        char_name = char_review.get("name", "unknown")
        attributes = char_review.get("attributes", {})

        for attr_name, attr_data in attributes.items():
            score = attr_data.get("score", 100) if isinstance(attr_data, dict) else 100
            note = attr_data.get("note", "") if isinstance(attr_data, dict) else ""

            # If attribute failed (< 70), add reinforcement
            if score < 70:
                reinforcements.append(
                    f"CRITICAL FIX NEEDED - {char_name.upper()} {attr_name.upper()}: "
                    f"Previous attempt scored {score}/100. Issue: {note}. "
                    f"This MUST be corrected in the new image."
                )

    if reinforcements:
        prompt += "\n\n=== CONSISTENCY FIXES REQUIRED ===\n"
        prompt += "\n".join(reinforcements)

    return prompt


def save_rejected_image(
    output_path: Path,
    review_result: dict,
    attempt: int
):
    """
    Save rejected image and review to rejected/ directory.
    """
    rejected_dir = output_path.parent / "rejected"
    rejected_dir.mkdir(exist_ok=True)

    card_id = output_path.stem
    rejected_image_path = rejected_dir / f"{card_id}_v{attempt}.png"
    rejected_review_path = rejected_dir / f"{card_id}_v{attempt}_review.json"

    # Move image to rejected
    if output_path.exists():
        shutil.move(str(output_path), str(rejected_image_path))
        print(f"  -> Rejected image saved: {rejected_image_path.name}")

    # Save review
    if review_result:
        review_dict = asdict(review_result) if hasattr(review_result, '__dataclass_fields__') else review_result
        with open(rejected_review_path, 'w', encoding='utf-8') as f:
            json.dump(review_dict, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description="Generate images for Parasha Pack cards")
    parser.add_argument("deck_path", help="Path to deck.json file")
    parser.add_argument("--api-key", help="Gemini API key (or set GEMINI_API_KEY env var)")
    parser.add_argument("--card", help="Generate image for specific card ID only")
    parser.add_argument("--skip-existing", action="store_true", help="Skip cards that already have images")
    parser.add_argument("--model", choices=["nano-banana", "imagen", "flash"], default="nano-banana", help="Model to use (nano-banana recommended)")
    parser.add_argument("--no-refs", action="store_true", help="Disable character reference images")

    # Review options
    parser.add_argument("--review", action="store_true", help="Enable consistency review after generation")
    parser.add_argument("--max-attempts", type=int, default=1, help="Max generation attempts per card (with --review)")
    parser.add_argument("--min-score", type=int, default=70, help="Minimum score to accept (with --review)")
    parser.add_argument("--review-verbose", action="store_true", help="Show detailed review scores")

    args = parser.parse_args()

    # Get API key
    api_key = args.api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: Gemini API key required.")
        print("Set GEMINI_API_KEY environment variable or use --api-key flag")
        print("\nGet your API key at: https://aistudio.google.com/app/apikey")
        sys.exit(1)

    # Load deck
    deck_path = Path(args.deck_path)
    if not deck_path.exists():
        print(f"Error: Deck file not found: {deck_path}")
        sys.exit(1)

    with open(deck_path, 'r', encoding='utf-8') as f:
        deck = json.load(f)

    # Setup output directory
    images_dir = deck_path.parent / "images"
    images_dir.mkdir(exist_ok=True)

    deck_name = deck.get('parasha_en') or deck.get('holiday_en', 'Unknown')
    print(f"Generating images for: {deck_name}")
    print(f"Output directory: {images_dir}")
    print(f"Model: {args.model}")
    print(f"Character references: {'disabled' if args.no_refs else 'enabled'}")
    if args.review:
        print(f"Consistency review: enabled (min score: {args.min_score}, max attempts: {args.max_attempts})")
    print("-" * 50)

    # Track results
    success_count = 0
    skip_count = 0
    fail_count = 0
    review_results = {}

    # Generate images for each card
    for card in deck["cards"]:
        card_id = card["card_id"]

        # Filter by specific card if requested
        if args.card and card_id != args.card:
            continue

        output_path = images_dir / f"{card_id}.png"

        # Skip if image exists and flag set
        if args.skip_existing and output_path.exists():
            print(f"[SKIP] {card_id} - image exists")
            skip_count += 1
            continue

        original_prompt = card.get("image_prompt", "")
        if not original_prompt:
            print(f"[SKIP] {card_id} - no prompt")
            skip_count += 1
            continue

        # Add learned reinforcements to prompt
        prompt = original_prompt
        if args.review and not args.no_refs:
            reinforcements = get_learned_reinforcements(deck_path, card)
            if reinforcements:
                prompt += "\n\n=== LEARNED CONSISTENCY REQUIREMENTS ===\n"
                prompt += "\n".join(reinforcements)
                print(f"[GEN] {card_id}: {card['title_en'][:30]}... (+{len(reinforcements)} reinforcements)")
            else:
                print(f"[GEN] {card_id}: {card['title_en'][:30]}...")
        else:
            print(f"[GEN] {card_id}: {card['title_en'][:30]}...")

        # Generation loop with optional review
        final_success = False
        final_review = None

        for attempt in range(1, args.max_attempts + 1):
            if attempt > 1:
                print(f"  [RETRY] Attempt {attempt}/{args.max_attempts}")

            # Load reference images for character consistency (nano-banana only)
            reference_images = None
            if args.model == "nano-banana" and not args.no_refs:
                reference_images = load_reference_images(deck_path, prompt)

            # Generate based on model
            if args.model == "nano-banana":
                success = generate_image_nano_banana(prompt, api_key, str(output_path), reference_images=reference_images)
            elif args.model == "imagen":
                success = generate_image_imagen(prompt, api_key, str(output_path))
            else:
                success = generate_image_gemini_flash(prompt, api_key, str(output_path))

            if not success:
                print(f"  [FAIL] Generation failed")
                continue

            # Run consistency review if enabled
            if args.review:
                # Create a temporary card dict with updated image path for review
                review_card_data = {**card, "image_path": f"images/{card_id}.png"}
                review_result = review_generated_image(deck_path, review_card_data, api_key, args.review_verbose)

                if review_result:
                    score = review_result.overall_score
                    recommendation = review_result.recommendation

                    # Color-coded output
                    if recommendation == "PASS":
                        color, reset = "\033[92m", "\033[0m"
                    elif recommendation == "REVIEW":
                        color, reset = "\033[93m", "\033[0m"
                    else:
                        color, reset = "\033[91m", "\033[0m"

                    print(f"  {color}[{recommendation}]{reset} Score: {score}/100")

                    if args.review_verbose and review_result.blocking_issues:
                        print(f"    Issues: {', '.join(review_result.blocking_issues)}")

                    # Check if score meets threshold
                    if score >= args.min_score:
                        final_success = True
                        final_review = review_result
                        break
                    else:
                        # Save rejected and try again
                        save_rejected_image(output_path, review_result, attempt)

                        if attempt < args.max_attempts:
                            # Strengthen prompt for next attempt
                            review_dict = asdict(review_result)
                            prompt = strengthen_prompt_from_review(original_prompt, review_dict)
                            time.sleep(2)  # Rate limit
                        else:
                            # Max attempts reached, keep last image
                            print(f"  [WARN] Max attempts reached, keeping last image")
                            # Regenerate one more time without saving to rejected
                            if args.model == "nano-banana":
                                generate_image_nano_banana(prompt, api_key, str(output_path), reference_images=reference_images)
                            final_success = True
                            final_review = review_result
                else:
                    # No review result (no characters to check)
                    final_success = True
                    break
            else:
                # No review, just accept
                final_success = True
                break

            time.sleep(2)  # Rate limit between attempts

        if final_success:
            print(f"  -> Saved: {output_path.name}")
            success_count += 1
            card["image_path"] = f"images/{card_id}.png"

            if final_review:
                review_results[card_id] = final_review
        else:
            fail_count += 1

        # Rate limiting - wait between cards
        time.sleep(2)

    # Save updated deck with image paths
    with open(deck_path, 'w', encoding='utf-8') as f:
        json.dump(deck, f, indent=2, ensure_ascii=False)

    print("-" * 50)
    print(f"Complete! Success: {success_count}, Skipped: {skip_count}, Failed: {fail_count}")

    if success_count > 0:
        print(f"\nImages saved to: {images_dir}")
        print(f"Deck updated with image paths: {deck_path}")

    # Save review results and update learnings if review was enabled
    if args.review and review_results:
        try:
            from consistency_reviewer import save_reviews, update_learnings

            reviews_dir = deck_path.parent / "reviews"
            summary = save_reviews(review_results, reviews_dir)

            # Update global learnings
            project_root = deck_path.parent.parent.parent
            deck_name = deck_path.parent.name
            learnings = update_learnings(review_results, deck_name, project_root)

            print(f"\nReview Summary:")
            print(f"  Average score: {summary['average_score']}/100")
            print(f"  Pass: {summary['scores']['pass']}, Review: {summary['scores']['review']}, "
                  f"Regenerate: {summary['scores']['regenerate']}, Reject: {summary['scores']['reject']}")
            print(f"  Reviews saved to: {reviews_dir}")

            # Show learned recommendations
            recommendations = learnings.get("global_patterns", {}).get("recommended_reinforcements", {})
            if recommendations:
                print(f"\nLearned reinforcement recommendations:")
                for key, rec in sorted(recommendations.items(), key=lambda x: -x[1].get("failure_rate", 0)):
                    print(f"  [{rec['priority'].upper()}] {key}: {rec['failure_rate']}% failure rate")
        except ImportError:
            print("\n[WARN] Could not save review results (consistency_reviewer not available)")
        except Exception as e:
            print(f"\n[WARN] Error saving reviews: {e}")


if __name__ == "__main__":
    main()
