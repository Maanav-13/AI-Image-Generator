"""
api_client.py
-------------
All communication with the Stability AI Image Generation API lives here.
Keeping it separate from app.py means the UI code never has to know
about HTTP requests, headers, or response parsing.

Uses the Stability AI "Stable Image Core" endpoint (v2beta), which
returns image bytes directly.
Docs: https://platform.stability.ai/docs/api-reference
"""

import os
import requests

STABILITY_API_HOST = "https://api.stability.ai"
GENERATE_ENDPOINT = f"{STABILITY_API_HOST}/v2beta/stable-image/generate/core"

# Supported aspect ratios for this endpoint (bonus: image size selector)
ASPECT_RATIOS = ["1:1", "16:9", "9:16", "4:3", "3:4"]


class StabilityAPIError(Exception):
    """Raised when the Stability AI API returns an error response."""
    pass


def get_api_key() -> str:
    """
    Read the API key from the environment. Works for both:
    - local development via a .env file (loaded by python-dotenv in app.py)
    - Streamlit Cloud deployment via st.secrets (app.py copies it into
      the environment before this function is called)
    """
    api_key = os.environ.get("STABILITY_API_KEY")
    if not api_key:
        raise StabilityAPIError(
            "No API key found. Set STABILITY_API_KEY in your .env file "
            "or in Streamlit Secrets."
        )
    return api_key


def generate_image(
    prompt: str,
    negative_prompt: str = "",
    aspect_ratio: str = "1:1",
    output_format: str = "png",
):
    """
    Call the Stability AI API to generate a single image.

    Returns: raw image bytes (PNG or JPEG) on success.
    Raises: StabilityAPIError on failure.
    """
    api_key = get_api_key()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "image/*",
    }

    data = {
        "prompt": prompt,
        "output_format": output_format,
        "aspect_ratio": aspect_ratio,
    }
    if negative_prompt.strip():
        data["negative_prompt"] = negative_prompt.strip()

    try:
        response = requests.post(
            GENERATE_ENDPOINT,
            headers=headers,
            files={"none": ""},  # required by Stability's multipart API
            data=data,
            timeout=60,
        )
    except requests.exceptions.RequestException as exc:
        raise StabilityAPIError(f"Network error contacting Stability AI: {exc}")

    if response.status_code == 200:
        return response.content

    # Try to extract a useful error message from the API response
    try:
        error_json = response.json()
        message = error_json.get("errors", [response.text])
        message = ", ".join(message) if isinstance(message, list) else str(message)
    except ValueError:
        message = response.text

    raise StabilityAPIError(f"API error ({response.status_code}): {message}")


def generate_images(prompt: str, negative_prompt: str, aspect_ratio: str, count: int):
    """
    Generate multiple images by calling generate_image() repeatedly.
    The Stable Image Core endpoint generates one image per request,
    so this loops client-side for the "multiple image generation" bonus.

    Returns a list of (image_bytes, error_message) tuples so the caller
    can show partial results even if one request in the batch fails.
    """
    results = []
    for _ in range(count):
        try:
            img_bytes = generate_image(
                prompt=prompt,
                negative_prompt=negative_prompt,
                aspect_ratio=aspect_ratio,
            )
            results.append((img_bytes, None))
        except StabilityAPIError as exc:
            results.append((None, str(exc)))
    return results
