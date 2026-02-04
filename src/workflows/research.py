"""
Research functions and databases for Parasha Pack.

Contains character and parasha research data and lookup functions.
"""

from typing import List

from .models import CharacterResearch, ParashaResearch


# =============================================================================
# CHARACTER DATABASE
# =============================================================================

CHARACTER_DATABASE = {
    "moses": CharacterResearch(
        name_en="Moses",
        name_he="מֹשֶׁה",
        biblical_refs=["Exodus 2-40", "Numbers 1-36", "Deuteronomy 1-34"],
        key_stories=[
            "Baby in the basket on the Nile",
            "Burning bush encounter",
            "Leading the Exodus from Egypt",
            "Receiving the Torah at Sinai",
            "Striking the rock for water",
        ],
        personality_traits=["humble", "caring", "brave", "patient", "faithful"],
        relationships={
            "Miriam": "older sister",
            "Aaron": "older brother",
            "Yitro": "father-in-law and advisor",
            "Pharaoh": "confronted for freedom",
            "Israelites": "leader and teacher",
        },
        emotional_moments=[
            {"event": "Seeing the burning bush", "emotion": "awe and wonder"},
            {"event": "Reuniting with Yitro", "emotion": "joy and gratitude"},
            {"event": "Receiving the commandments", "emotion": "reverence"},
            {"event": "When people complained", "emotion": "tired but caring"},
        ],
        age_appropriate_summary="Moses was a kind leader who helped his people be free. He listened to God and taught everyone to be good to each other.",
    ),
    "miriam": CharacterResearch(
        name_en="Miriam",
        name_he="מִרְיָם",
        biblical_refs=["Exodus 2:1-10", "Exodus 15:20-21", "Numbers 12", "Numbers 20:1"],
        key_stories=[
            "Watching baby Moses in the basket",
            "Suggesting her mother as a nurse",
            "Leading the women in song at the sea",
            "The well that followed the Israelites",
        ],
        personality_traits=["brave", "musical", "protective", "joyful", "faithful"],
        relationships={
            "Moses": "younger brother",
            "Aaron": "brother",
            "Yocheved": "mother",
            "Pharaoh's daughter": "spoke to her about Moses",
        },
        emotional_moments=[
            {"event": "Hiding to watch baby Moses", "emotion": "worried but brave"},
            {"event": "Singing at the sea", "emotion": "overjoyed and grateful"},
            {"event": "Caring for her family", "emotion": "loving and protective"},
        ],
        age_appropriate_summary="Miriam was brave and loved to sing! She protected her baby brother Moses and later led everyone in celebrating with music.",
    ),
    "yitro": CharacterResearch(
        name_en="Yitro",
        name_he="יִתְרוֹ",
        biblical_refs=["Exodus 2:16-22", "Exodus 18"],
        key_stories=[
            "Welcoming Moses as a stranger",
            "Giving his daughter Tzipporah to Moses",
            "Visiting Moses in the desert",
            "Giving wise advice about judging fairly",
        ],
        personality_traits=["wise", "welcoming", "observant", "helpful", "grandfatherly"],
        relationships={
            "Moses": "son-in-law",
            "Tzipporah": "daughter",
            "Israelites": "wise advisor",
        },
        emotional_moments=[
            {"event": "Hearing about the Exodus", "emotion": "amazed and grateful"},
            {"event": "Reuniting with Moses", "emotion": "overjoyed"},
            {"event": "Seeing Moses overwhelmed", "emotion": "concerned and caring"},
            {"event": "Giving advice", "emotion": "wise and helpful"},
        ],
        age_appropriate_summary="Yitro was a wise grandfather who loved to help. He gave Moses great advice about being a good leader and sharing work with others.",
    ),
    "abraham": CharacterResearch(
        name_en="Abraham",
        name_he="אַבְרָהָם",
        biblical_refs=["Genesis 12-25"],
        key_stories=[
            "Leaving home for a new land",
            "Welcoming three visitors",
            "Looking at the stars with God's promise",
        ],
        personality_traits=["faithful", "welcoming", "brave", "kind", "generous"],
        relationships={
            "Sarah": "beloved wife",
            "Isaac": "son",
            "Lot": "nephew",
        },
        emotional_moments=[
            {"event": "Leaving his home", "emotion": "brave but uncertain"},
            {"event": "Welcoming guests", "emotion": "joyful and generous"},
            {"event": "Seeing the stars", "emotion": "hopeful and amazed"},
        ],
        age_appropriate_summary="Abraham was very welcoming and always invited people to his tent. He trusted God and started a big family.",
    ),
    "sarah": CharacterResearch(
        name_en="Sarah",
        name_he="שָׂרָה",
        biblical_refs=["Genesis 11-23"],
        key_stories=[
            "Traveling to a new land with Abraham",
            "Welcoming visitors to the tent",
            "Laughing when she heard she would have a baby",
            "Being a loving mother to Isaac",
        ],
        personality_traits=["beautiful", "hospitable", "patient", "joyful", "strong"],
        relationships={
            "Abraham": "beloved husband",
            "Isaac": "son",
        },
        emotional_moments=[
            {"event": "Hearing about a baby", "emotion": "surprised and happy"},
            {"event": "Holding Isaac", "emotion": "overjoyed"},
        ],
        age_appropriate_summary="Sarah was kind and always welcomed guests. She waited a long time and was so happy when baby Isaac was born!",
    ),
    # Purim characters
    "esther": CharacterResearch(
        name_en="Esther",
        name_he="אֶסְתֵּר",
        biblical_refs=["Megillat Esther"],
        key_stories=[
            "Becoming queen of Persia",
            "Keeping her Jewish identity secret",
            "Going to the king uninvited to save her people",
            "Hosting banquets for the king and Haman",
        ],
        personality_traits=["brave", "kind", "humble", "wise", "faithful"],
        relationships={
            "Mordechai": "cousin who raised her",
            "Achashverosh": "husband, the king",
            "Haman": "antagonist she confronted",
        },
        emotional_moments=[
            {"event": "Keeping her secret", "emotion": "nervous but determined"},
            {"event": "Going to the king uninvited", "emotion": "scared but brave"},
            {"event": "Revealing her identity", "emotion": "courageous"},
            {"event": "Saving her people", "emotion": "relieved and joyful"},
        ],
        age_appropriate_summary="Esther was a brave queen with a big secret — she was Jewish! When her people needed help, she was SO brave and saved everyone.",
    ),
    "mordechai": CharacterResearch(
        name_en="Mordechai",
        name_he="מׇרְדְּכַי",
        biblical_refs=["Megillat Esther"],
        key_stories=[
            "Raising his cousin Esther",
            "Refusing to bow to Haman",
            "Discovering a plot against the king",
            "Being honored by the king",
        ],
        personality_traits=["wise", "brave", "faithful", "protective", "principled"],
        relationships={
            "Esther": "younger cousin he raised",
            "Haman": "would not bow to him",
            "Achashverosh": "saved his life",
        },
        emotional_moments=[
            {"event": "Sending Esther to the king", "emotion": "worried but hopeful"},
            {"event": "Refusing to bow", "emotion": "firm and faithful"},
            {"event": "Being honored", "emotion": "humble"},
            {"event": "Celebrating victory", "emotion": "grateful and joyful"},
        ],
        age_appropriate_summary="Mordechai was like a wise grandpa who always knew what was right. He helped Esther be brave and stood up for what he believed.",
    ),
    "haman": CharacterResearch(
        name_en="Haman",
        name_he="הָמָן",
        biblical_refs=["Megillat Esther"],
        key_stories=[
            "Wanting everyone to bow to him",
            "Getting jealous when Mordechai wouldn't bow",
            "Making a bad plan because of jealousy",
            "His plan being stopped",
        ],
        personality_traits=["jealous", "proud", "misguided"],
        relationships={
            "Mordechai": "felt jealous of him",
            "Achashverosh": "worked for the king",
            "Esther": "didn't know her secret",
        },
        emotional_moments=[
            {"event": "Mordechai not bowing", "emotion": "jealous and hurt"},
            {"event": "Making his plan", "emotion": "frustrated"},
            {"event": "Being caught", "emotion": "embarrassed"},
        ],
        age_appropriate_summary="Haman felt very jealous when someone wouldn't bow to him. His jealousy made him make bad choices. We can feel jealous sometimes, but we should make good choices.",
    ),
    "achashverosh": CharacterResearch(
        name_en="King Achashverosh",
        name_he="אֲחַשְׁוֵרוֹשׁ",
        biblical_refs=["Megillat Esther"],
        key_stories=[
            "Looking for a new queen",
            "Choosing Esther as queen",
            "Not thinking before agreeing to Haman's plan",
            "Learning the truth and making things right",
        ],
        personality_traits=["confused", "careless", "eventually learns"],
        relationships={
            "Esther": "wife and queen",
            "Haman": "advisor he trusted too much",
            "Mordechai": "honored him in the end",
        },
        emotional_moments=[
            {"event": "Making hasty decisions", "emotion": "distracted"},
            {"event": "Learning the truth", "emotion": "surprised and upset"},
            {"event": "Making things right", "emotion": "determined"},
        ],
        age_appropriate_summary="King Achashverosh was a king who didn't always think before deciding. He learned it's important to ask questions and think carefully!",
    ),
}


# =============================================================================
# PARASHA DATABASE
# =============================================================================

PARASHA_DATABASE = {
    "yitro": ParashaResearch(
        name_en="Yitro",
        name_he="יִתְרוֹ",
        ref="Exodus 18:1-20:23",
        book="Exodus",
        summary="Yitro brings Moses's family back and gives wise advice. The Israelites receive the Ten Commandments at Mount Sinai.",
        key_events=[
            "Yitro hears about the Exodus and visits",
            "Yitro brings Tzipporah and the children",
            "Yitro sees Moses judging all day and gives advice",
            "Moses appoints helpers to share the work",
            "The Israelites camp at Mount Sinai",
            "God gives the Ten Commandments",
        ],
        main_characters=["Moses", "Yitro", "Aaron", "Tzipporah"],
        themes=["listening", "wisdom", "teamwork", "rules", "respect"],
        emotions=["joy", "amazement", "reverence", "gratitude"],
        mitzvot=["Honor your father and mother", "Keep Shabbat"],
        child_friendly_lesson="When someone gives us good advice, we should listen! Sharing work helps everyone.",
        suggested_theme="covenant",
        border_color="#5c2d91",
    ),
    "beshalach": ParashaResearch(
        name_en="Beshalach",
        name_he="בְּשַׁלַּח",
        ref="Exodus 13:17-17:16",
        book="Exodus",
        summary="The Israelites leave Egypt, cross the sea, and begin their journey in the desert with miracles along the way.",
        key_events=[
            "Leaving Egypt with joy",
            "Pharaoh chases the Israelites",
            "Crossing the sea on dry land",
            "Miriam leads singing and dancing",
            "Finding water at Marah",
            "Manna falls from heaven",
        ],
        main_characters=["Moses", "Miriam", "Aaron", "Pharaoh"],
        themes=["freedom", "trust", "miracles", "gratitude", "music"],
        emotions=["scared", "brave", "joyful", "grateful", "amazed"],
        mitzvot=["Remember Shabbat", "Trust in God"],
        child_friendly_lesson="Even when things seem scary, we can be brave! And when good things happen, we celebrate together.",
        suggested_theme="water",
        border_color="#2d8a8a",
    ),
}


# =============================================================================
# RESEARCH FUNCTIONS
# =============================================================================

def research_character(name: str) -> CharacterResearch:
    """
    Research a biblical character using pre-defined database.

    Args:
        name: Character name (English, e.g., "Miriam", "Moses", "Yitro")

    Returns:
        CharacterResearch dataclass with all gathered information
    """
    name_lower = name.lower().strip()

    if name_lower in CHARACTER_DATABASE:
        return CHARACTER_DATABASE[name_lower]

    # Return empty research for unknown characters
    return CharacterResearch(
        name_en=name.title(),
        name_he="",
        age_appropriate_summary=f"Research needed for {name}",
    )


def research_parasha(name: str) -> ParashaResearch:
    """
    Research a Torah portion using pre-defined database.

    Args:
        name: Parasha name (English, e.g., "Yitro", "Beshalach")

    Returns:
        ParashaResearch dataclass with all gathered information
    """
    # Try to get theme colors from sefaria_client if available
    try:
        from sefaria_client import PARASHA_THEMES, get_border_color
    except ImportError:
        PARASHA_THEMES = {}
        get_border_color = lambda n, b: "#5c2d91"

    name_lower = name.lower().strip()

    if name_lower in PARASHA_DATABASE:
        return PARASHA_DATABASE[name_lower]

    # Get theme from sefaria_client if available
    theme = PARASHA_THEMES.get(name.title(), "covenant")
    border_color = get_border_color(name.title(), "")

    return ParashaResearch(
        name_en=name.title(),
        name_he="",
        ref="",
        book="",
        summary=f"Research needed for {name}",
        suggested_theme=theme,
        border_color=border_color,
    )


def list_available_characters() -> List[str]:
    """List all characters with pre-defined research data."""
    return list(CHARACTER_DATABASE.keys())


def list_available_parshiyot() -> List[str]:
    """List all parshiyot with pre-defined research data."""
    return list(PARASHA_DATABASE.keys())


def get_character_summary(name: str) -> str:
    """Get a quick summary of a character's research."""
    research = research_character(name)
    return f"""
{research.name_en} ({research.name_he})
{'='*40}
Traits: {', '.join(research.personality_traits)}
Stories: {', '.join(research.key_stories[:3])}...
Summary: {research.age_appropriate_summary}
"""


def get_parasha_summary(name: str) -> str:
    """Get a quick summary of a parasha's research."""
    research = research_parasha(name)
    return f"""
{research.name_en} ({research.name_he})
{'='*40}
Reference: {research.ref}
Theme: {research.suggested_theme}
Characters: {', '.join(research.main_characters)}
Lesson: {research.child_friendly_lesson}
"""
