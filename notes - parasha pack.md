Are you sure there is no Gemini 3 flash in preview? Check the ai studio documentation website: https://ai.google.dev/gemini-api/docs/gemini-3 - are there any API limits to be concerned with?
What is the total cost to generate a deck including the cost of all models any any other costs?

⏺ Done. The implementation plan is at  
 agents/AGENTIC_WORKFLOW_PLAN.md.

---

Commands to Run the Plan

Start Fresh

/clear

Then Run Phase 1 (Auto-Regeneration Loop)

/plan Implement Phase 1 from agents/AGENTIC_WORKFLOW_PLAN.md -
Add auto-retry loop to generate_images.py. Read the plan
first, then implement the --auto-retry flag with
MAX_ATTEMPTS=2 and AUTO_REGENERATE_THRESHOLD=75. Also upgrade
consistency_reviewer.py to use gemini-3-flash-preview.

Or Run All Phases Sequentially

/plan Implement the agentic workflow from
agents/AGENTIC_WORKFLOW_PLAN.md. Start with Phase 1
(auto-retry), then Phase 2 (orchestrator), then Phase 3
(notifications + API). Read the plan carefully and implement
each phase, testing as you go.

Quick Reference After Implementation

# Test Phase 1 - Auto-retry

source .env && export GEMINI_API_KEY && \
 python src/generate_images.py decks/yitro/deck.json --card
spotlight_1 --auto-retry --verbose

# Test Phase 2 - Full orchestrator (after implemented)

python workflows.py deck Mishpatim --auto

# Test Phase 3 - Review site API (after implemented)

python review-site/api/server.py

After you /clear, run this command:

Implement Phase 1 from agents/AGENTIC_WORKFLOW_PLAN.md - Add
auto-retry loop to generate_images.py. Read the plan first,
then implement the --auto-retry flag with MAX_ATTEMPTS=2 and
AUTO_REGENERATE_THRESHOLD=75. Also upgrade  
 consistency_reviewer.py to use gemini-3-flash-preview. Test
with: source .env && export GEMINI_API_KEY && python  
 src/generate_images.py decks/yitro/deck.json --card spotlight_1
--auto-retry --verbose

Or for all phases:

Implement the agentic workflow from
agents/AGENTIC_WORKFLOW_PLAN.md. Read the full plan, then
implement Phase 1, 2, and 3 in order, testing each phase before
moving to the next.

Your progress on the Tetzaveh deck is already saved automatically.
Here's how it works:

How Deck Progress is Saved

The orchestrator saves everything to decks/tetzaveh/pipeline/:

decks/tetzaveh/pipeline/  
 ├── state.yaml # Pipeline state (current stage, checkpoint
status)
├── 01-output.yaml # Agent 1 output (parasha research)
├── 02-output.yaml # Agent 2 output (deck structure)
├── 03-output.yaml # (created when agent 3 runs)
...

To resume later:
cd src
source ../.env && export ANTHROPIC_API_KEY
python3 -m workflows.cli deck Tetzaveh --auto --resume

The --resume flag reads state.yaml and picks up where it left off.

Current State

Your Tetzaveh deck is paused at the structure checkpoint (after
Agent 2). The edits we just made to 01-output.yaml and
02-output.yaml are saved and will be used when you continue.

Next Steps to Continue

1. Approve the structure checkpoint (via API or manually):

# Option 1: API

curl -X POST http://localhost:5000/api/approve/tetzaveh/structure

# Option 2: Manual - edit state.yaml

2. Resume the pipeline:
   python3 -m workflows.cli deck Tetzaveh --auto --resume

This will run agents 3-6 (content writer, Hebrew expert, visual
director, editor) and pause again at the identity checkpoint for
character review.

Let me also document the YEAR_CONTEXT population process in the
workflow documentation.
