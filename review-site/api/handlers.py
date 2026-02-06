"""
API Handlers for Review Site.

Shared logic for API endpoints, used by both Flask server
and potentially other integrations.
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

# Try to import yaml
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


def get_decks_dir() -> Path:
    """Get the decks directory path."""
    return Path(__file__).parent.parent.parent / "decks"


def get_src_dir() -> Path:
    """Get the src directory path."""
    return Path(__file__).parent.parent.parent / "src"


def load_deck_state(deck_name: str) -> Optional[dict]:
    """
    Load pipeline state for a deck.

    Args:
        deck_name: Deck name (lowercase)

    Returns:
        State dict or None if not found
    """
    deck_path = get_decks_dir() / deck_name / "pipeline"

    # Try YAML first, then JSON
    state_yaml = deck_path / "state.yaml"
    state_json = deck_path / "state.json"

    if state_yaml.exists() and YAML_AVAILABLE:
        with open(state_yaml, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    elif state_json.exists():
        with open(state_json, 'r', encoding='utf-8') as f:
            return json.load(f)

    return None


def save_deck_state(deck_name: str, state: dict) -> bool:
    """
    Save pipeline state for a deck.

    Args:
        deck_name: Deck name (lowercase)
        state: State dict to save

    Returns:
        True if saved successfully
    """
    deck_path = get_decks_dir() / deck_name / "pipeline"

    if not deck_path.exists():
        return False

    state["updated_at"] = datetime.now().isoformat()

    if YAML_AVAILABLE:
        state_path = deck_path / "state.yaml"
        with open(state_path, 'w', encoding='utf-8') as f:
            yaml.dump(state, f, default_flow_style=False, allow_unicode=True)
    else:
        state_path = deck_path / "state.json"
        with open(state_path, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

    return True


def get_deck_status(deck_name: str) -> dict:
    """
    Get the current status of a deck's pipeline.

    Args:
        deck_name: Deck name (lowercase)

    Returns:
        Status dict with state information
    """
    state = load_deck_state(deck_name)

    if not state:
        # Check if deck exists at all
        deck_path = get_decks_dir() / deck_name
        if deck_path.exists():
            return {
                "exists": True,
                "has_pipeline": False,
                "status": "no_pipeline",
                "message": "Deck exists but no pipeline state found",
            }
        return {
            "exists": False,
            "status": "not_found",
            "message": f"Deck '{deck_name}' not found",
        }

    # Build status response
    status = {
        "exists": True,
        "has_pipeline": True,
        "parasha": state.get("parasha"),
        "content_type": state.get("content_type", "parasha"),
        "current_stage": state.get("current_stage"),
        "completed_stages": state.get("completed_stages", []),
        "created_at": state.get("created_at"),
        "updated_at": state.get("updated_at"),
        "checkpoints": state.get("checkpoints", {}),
        "needs_human_review": state.get("needs_human_review", []),
    }

    # Determine overall status
    if state.get("current_stage") == "complete":
        status["status"] = "complete"
    elif any(c.get("status") == "pending" for c in state.get("checkpoints", {}).values()):
        status["status"] = "awaiting_approval"
        pending = [k for k, v in state.get("checkpoints", {}).items() if v.get("status") == "pending"]
        status["pending_checkpoints"] = pending
    elif state.get("needs_human_review"):
        status["status"] = "needs_review"
    else:
        status["status"] = "in_progress"

    return status


def approve_checkpoint(deck_name: str, checkpoint: str, notes: str = "") -> dict:
    """
    Approve a checkpoint for a deck.

    Args:
        deck_name: Deck name (lowercase)
        checkpoint: Checkpoint name (structure, identity, final)
        notes: Optional approval notes

    Returns:
        Result dict
    """
    state = load_deck_state(deck_name)

    if not state:
        return {
            "success": False,
            "error": f"Deck '{deck_name}' not found or has no pipeline",
        }

    # Check if checkpoint is pending
    checkpoints = state.get("checkpoints", {})
    checkpoint_data = checkpoints.get(checkpoint, {})

    if checkpoint_data.get("status") != "pending":
        return {
            "success": False,
            "error": f"Checkpoint '{checkpoint}' is not pending (status: {checkpoint_data.get('status', 'none')})",
        }

    # Approve the checkpoint
    checkpoints[checkpoint] = {
        "status": "approved",
        "approved_at": datetime.now().isoformat(),
        "notes": notes,
    }
    state["checkpoints"] = checkpoints

    if not save_deck_state(deck_name, state):
        return {
            "success": False,
            "error": "Failed to save state",
        }

    return {
        "success": True,
        "message": f"Checkpoint '{checkpoint}' approved for {deck_name}",
        "checkpoint": checkpoint,
        "notes": notes,
    }


def resume_orchestrator(deck_name: str) -> dict:
    """
    Resume the orchestrator for a deck in the background.

    Args:
        deck_name: Deck name

    Returns:
        Result dict
    """
    src_dir = get_src_dir()

    # Start orchestrator in background
    cmd = [
        "python", "-m", "workflows", "deck",
        deck_name.title(),  # Capitalize for parasha name
        "--auto",
        "--resume",
    ]

    try:
        process = subprocess.Popen(
            cmd,
            cwd=src_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,  # Detach from parent
        )

        return {
            "success": True,
            "message": f"Orchestrator resumed for {deck_name}",
            "pid": process.pid,
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to resume orchestrator: {e}",
        }


def regenerate_card(deck_name: str, card_id: str, auto_retry: bool = True) -> dict:
    """
    Trigger regeneration of a single card image.

    Args:
        deck_name: Deck name (lowercase)
        card_id: Card ID to regenerate
        auto_retry: Whether to use auto-retry mode

    Returns:
        Result dict
    """
    deck_path = get_decks_dir() / deck_name
    deck_json = deck_path / "deck.json"
    src_dir = get_src_dir()

    if not deck_json.exists():
        return {
            "success": False,
            "error": f"Deck '{deck_name}' not found",
        }

    # Build command
    cmd = [
        "python", "generate_images.py",
        str(deck_json),
        "--card", card_id,
    ]

    if auto_retry:
        cmd.append("--auto-retry")
        cmd.append("--verbose")

    try:
        result = subprocess.run(
            cmd,
            cwd=src_dir,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        success = result.returncode == 0

        return {
            "success": success,
            "card_id": card_id,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Generation timed out after 5 minutes",
            "card_id": card_id,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "card_id": card_id,
        }


def get_deck_list() -> list[dict]:
    """
    Get list of all decks with their status.

    Returns:
        List of deck info dicts
    """
    decks_dir = get_decks_dir()
    decks = []

    if not decks_dir.exists():
        return decks

    for deck_dir in sorted(decks_dir.iterdir()):
        if not deck_dir.is_dir():
            continue

        # Skip special directories
        if deck_dir.name.startswith(".") or deck_dir.name == "registry.json":
            continue

        deck_info = {
            "name": deck_dir.name,
            "has_deck_json": (deck_dir / "deck.json").exists(),
            "has_pipeline": (deck_dir / "pipeline").exists(),
        }

        # Get pipeline status if available
        if deck_info["has_pipeline"]:
            state = load_deck_state(deck_dir.name)
            if state:
                deck_info["current_stage"] = state.get("current_stage")
                deck_info["updated_at"] = state.get("updated_at")

        # Count images
        images_dir = deck_dir / "images"
        if images_dir.exists():
            deck_info["image_count"] = len(list(images_dir.glob("*.png")))

        decks.append(deck_info)

    return decks


def get_card_review(deck_name: str, card_id: str) -> Optional[dict]:
    """
    Get the latest review for a specific card.

    Args:
        deck_name: Deck name (lowercase)
        card_id: Card ID

    Returns:
        Review dict or None
    """
    reviews_dir = get_decks_dir() / deck_name / "reviews"
    review_path = reviews_dir / f"{card_id}_review.json"

    if not review_path.exists():
        return None

    with open(review_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_all_card_reviews(deck_name: str) -> dict:
    """
    Get all card reviews for a deck.

    Args:
        deck_name: Deck name (lowercase)

    Returns:
        Dict mapping card_id to review
    """
    reviews_dir = get_decks_dir() / deck_name / "reviews"
    reviews = {}

    if not reviews_dir.exists():
        return reviews

    for review_file in reviews_dir.glob("*_review.json"):
        card_id = review_file.stem.replace("_review", "")
        with open(review_file, 'r', encoding='utf-8') as f:
            reviews[card_id] = json.load(f)

    return reviews


def get_review_summary(deck_name: str) -> Optional[dict]:
    """
    Get review summary for a deck.

    Args:
        deck_name: Deck name (lowercase)

    Returns:
        Summary dict or None
    """
    summary_path = get_decks_dir() / deck_name / "reviews" / "summary.json"

    if not summary_path.exists():
        return None

    with open(summary_path, 'r', encoding='utf-8') as f:
        return json.load(f)
