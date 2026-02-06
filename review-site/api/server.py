#!/usr/bin/env python3
"""
Flask API Server for Parasha Pack Review Site.

Provides REST API endpoints for:
- Viewing deck status
- Approving checkpoints
- Triggering card regeneration
- Resuming the orchestrator

Usage:
    python server.py
    # Server runs at http://localhost:5000

Endpoints:
    GET  /api/status/<deck>           - Get deck pipeline status
    GET  /api/decks                   - List all decks
    POST /api/approve/<deck>/<checkpoint> - Approve a checkpoint
    POST /api/regenerate/<deck>/<card_id> - Regenerate a card
    GET  /api/reviews/<deck>          - Get all card reviews
    GET  /api/reviews/<deck>/<card_id> - Get specific card review
"""

import os
import sys

# Add parent directories to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "src"))

try:
    from flask import Flask, jsonify, request
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("Flask not installed. Run: pip install flask flask-cors")

from handlers import (
    get_deck_status,
    approve_checkpoint,
    resume_orchestrator,
    regenerate_card,
    get_deck_list,
    get_card_review,
    get_all_card_reviews,
    get_review_summary,
)


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Enable CORS for local development
    if FLASK_AVAILABLE:
        CORS(app, origins=["http://localhost:*", "http://127.0.0.1:*", "file://"])

    # Health check
    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok", "service": "parasha-pack-api"})

    # List all decks
    @app.route("/api/decks")
    def list_decks():
        decks = get_deck_list()
        return jsonify({"decks": decks})

    # Get deck status
    @app.route("/api/status/<deck>")
    def deck_status(deck):
        status = get_deck_status(deck.lower())
        return jsonify(status)

    # Approve checkpoint
    @app.route("/api/approve/<deck>/<checkpoint>", methods=["POST"])
    def approve(deck, checkpoint):
        data = request.get_json(silent=True) or {}
        notes = data.get("notes", "")

        result = approve_checkpoint(deck.lower(), checkpoint, notes)

        if result.get("success"):
            # Optionally resume orchestrator
            if data.get("resume", False):
                resume_result = resume_orchestrator(deck)
                result["resume"] = resume_result

            return jsonify(result)
        else:
            return jsonify(result), 400

    # Regenerate card
    @app.route("/api/regenerate/<deck>/<card_id>", methods=["POST"])
    def regenerate(deck, card_id):
        data = request.get_json(silent=True) or {}
        auto_retry = data.get("auto_retry", True)

        result = regenerate_card(deck.lower(), card_id, auto_retry)

        if result.get("success"):
            return jsonify(result)
        else:
            return jsonify(result), 400

    # Get all reviews for a deck
    @app.route("/api/reviews/<deck>")
    def reviews(deck):
        all_reviews = get_all_card_reviews(deck.lower())
        summary = get_review_summary(deck.lower())

        return jsonify({
            "deck": deck,
            "reviews": all_reviews,
            "summary": summary,
        })

    # Get specific card review
    @app.route("/api/reviews/<deck>/<card_id>")
    def card_review(deck, card_id):
        review = get_card_review(deck.lower(), card_id)

        if review:
            return jsonify(review)
        else:
            return jsonify({"error": f"No review found for {card_id}"}), 404

    # Resume orchestrator (without approval)
    @app.route("/api/resume/<deck>", methods=["POST"])
    def resume(deck):
        result = resume_orchestrator(deck)

        if result.get("success"):
            return jsonify(result)
        else:
            return jsonify(result), 400

    return app


def main():
    """Run the Flask development server."""
    if not FLASK_AVAILABLE:
        print("Error: Flask is not installed.")
        print("Install with: pip install flask flask-cors")
        sys.exit(1)

    app = create_app()

    print("=" * 60)
    print("Parasha Pack Review Site API")
    print("=" * 60)
    print()
    print("Starting server at http://localhost:5000")
    print()
    print("Endpoints:")
    print("  GET  /api/health                    - Health check")
    print("  GET  /api/decks                     - List all decks")
    print("  GET  /api/status/<deck>             - Get deck status")
    print("  POST /api/approve/<deck>/<checkpoint> - Approve checkpoint")
    print("  POST /api/regenerate/<deck>/<card_id> - Regenerate card")
    print("  GET  /api/reviews/<deck>            - Get all reviews")
    print("  POST /api/resume/<deck>             - Resume orchestrator")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)

    app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == "__main__":
    main()
