"""
prompts.py
----------
Holds style definitions and the logic for turning a raw user prompt
into a style-conditioned prompt that gets sent to the image API.
Keeping this separate from the UI and API code means new styles can
be added here without touching app.py or api_client.py.
"""

import random

# Each style maps to a suffix that gets appended to the user's prompt,
# plus a short description shown in the UI.
STYLES = {
    "Realistic": {
        "suffix": "photorealistic, ultra detailed, sharp focus, natural lighting, 8k",
        "description": "Lifelike, photographic detail",
    },
    "Cyberpunk": {
        "suffix": "cyberpunk style, neon lights, futuristic, high contrast, rain-soaked streets, detailed",
        "description": "Neon-soaked, futuristic, high-tech",
    },
    "Anime": {
        "suffix": "anime style, detailed, vibrant colors, cel shaded, studio quality",
        "description": "Japanese animation aesthetic",
    },
    "Watercolor": {
        "suffix": "watercolor painting, soft brush strokes, pastel palette, paper texture, artistic",
        "description": "Soft, painterly, hand-painted look",
    },
    "Fantasy": {
        "suffix": "fantasy art, epic, magical atmosphere, intricate details, dramatic lighting",
        "description": "Epic and otherworldly",
    },
    "Minimalist": {
        "suffix": "minimalist design, clean lines, simple shapes, limited color palette, flat illustration",
        "description": "Clean, simple, modern",
    },
}

# A small set of example prompts for the "random prompt" bonus feature.
RANDOM_PROMPTS = [
    "A futuristic Indian city at night",
    "A cat wearing sunglasses",
    "An ancient temple floating in the clouds",
    "A robot tending a small rooftop garden",
    "A bustling night market on Mars",
    "A lighthouse on a cliff during a storm",
    "A dragon curled around a mountain peak",
    "A steampunk train crossing a desert",
    "An underwater city made of coral and glass",
    "A samurai standing in a field of cherry blossoms",
]


def get_style_names():
    """Return the list of style names for the radio buttons."""
    return list(STYLES.keys())


def build_final_prompt(user_prompt: str, style: str) -> str:
    """
    Combine the user's raw prompt with the suffix for the chosen style.

    Example:
        user_prompt = "A cat wearing sunglasses"
        style = "Anime"
        -> "A cat wearing sunglasses, anime style, detailed, vibrant colors, ..."
    """
    user_prompt = user_prompt.strip().rstrip(".")
    style_info = STYLES.get(style)
    if not style_info:
        return user_prompt
    return f"{user_prompt}, {style_info['suffix']}"


def get_random_prompt() -> str:
    """Return a random example prompt (bonus feature)."""
    return random.choice(RANDOM_PROMPTS)
