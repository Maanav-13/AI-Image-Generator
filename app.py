"""
app.py
------
Streamlit front end for the AI Image Generator chatbot.
This file only handles UI/layout and session state. All prompt
engineering lives in prompts.py and all API calls live in api_client.py.

Run locally with:
    streamlit run app.py
"""

import os
import base64
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

from prompts import get_style_names, build_final_prompt, get_random_prompt, STYLES
from api_client import generate_images, ASPECT_RATIOS, StabilityAPIError

# ----------------------------------------------------------------------
# Setup: load .env locally, fall back to Streamlit secrets when deployed
# ----------------------------------------------------------------------
load_dotenv()
if "STABILITY_API_KEY" not in os.environ and "STABILITY_API_KEY" in st.secrets:
    os.environ["STABILITY_API_KEY"] = st.secrets["STABILITY_API_KEY"]

st.set_page_config(
    page_title="Prism Image Generator",
    page_icon="🎨",
    layout="wide",
)

# ----------------------------------------------------------------------
# Session state
# ----------------------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []  # list of dicts: prompt, style, images, time
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
if "prompt_input" not in st.session_state:
    st.session_state.prompt_input = ""

# ----------------------------------------------------------------------
# Theme toggle (bonus). Streamlit doesn't allow true runtime theme
# switching without a rerun, so this injects CSS for a dark/light feel.
# ----------------------------------------------------------------------
def apply_theme(dark: bool):
    if dark:
        st.markdown(
            """
            <style>
            .stApp { background-color: #0e1117; color: #f0f0f0; }
            </style>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <style>
            .stApp { background-color: #ffffff; color: #0e1117; }
            </style>
            """,
            unsafe_allow_html=True,
        )


apply_theme(st.session_state.dark_mode)

# ----------------------------------------------------------------------
# Sidebar: settings
# ----------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")

    st.session_state.dark_mode = st.toggle("Dark mode", value=st.session_state.dark_mode)

    st.subheader("Image options")
    aspect_ratio = st.selectbox("Image size (aspect ratio)", ASPECT_RATIOS, index=0)
    num_images = st.slider("Number of images to generate", 1, 4, 1)
    negative_prompt = st.text_input(
        "Negative prompt (optional)",
        placeholder="e.g. blurry, low quality, watermark",
    )

    st.divider()
    if st.button("🗑️ Clear history"):
        st.session_state.history = []
        st.rerun()

# ----------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------
st.title("🎨 Prism — AI Image Generator")
st.write(
    "Describe what you want to see, pick a visual style, and let "
    "Stability AI generate it for you."
)

# ----------------------------------------------------------------------
# Main input area
# ----------------------------------------------------------------------
col1, col2 = st.columns([3, 1])

with col1:
    prompt = st.text_input(
        "Image prompt",
        value=st.session_state.prompt_input,
        placeholder="e.g. A futuristic Indian city at night",
        key="prompt_box",
    )

with col2:
    st.write("")  # vertical spacer to align button with text input
    st.write("")
    if st.button("🎲 Random prompt"):
        st.session_state.prompt_input = get_random_prompt()
        st.rerun()

style = st.radio(
    "Style",
    get_style_names(),
    horizontal=True,
    captions=[STYLES[s]["description"] for s in get_style_names()],
)

generate_clicked = st.button("✨ Generate", type="primary", use_container_width=True)

# ----------------------------------------------------------------------
# Generation
# ----------------------------------------------------------------------
if generate_clicked:
    if not prompt.strip():
        st.warning("Please enter a prompt before generating an image.")
    else:
        final_prompt = build_final_prompt(prompt, style)

        with st.expander("Final prompt sent to API", expanded=False):
            st.code(final_prompt)

        with st.spinner(f"Generating {num_images} image(s)..."):
            try:
                results = generate_images(
                    prompt=final_prompt,
                    negative_prompt=negative_prompt,
                    aspect_ratio=aspect_ratio,
                    count=num_images,
                )
            except StabilityAPIError as exc:
                results = [(None, str(exc))]

        images_b64 = []
        had_success = False
        for img_bytes, error in results:
            if error:
                st.error(error)
            else:
                had_success = True
                images_b64.append(base64.b64encode(img_bytes).decode("utf-8"))

        if had_success:
            st.session_state.history.insert(
                0,
                {
                    "user_prompt": prompt,
                    "style": style,
                    "final_prompt": final_prompt,
                    "images": images_b64,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
            )

# ----------------------------------------------------------------------
# Display: most recent generation first, then history/gallery
# ----------------------------------------------------------------------
if st.session_state.history:
    st.divider()
    latest = st.session_state.history[0]
    st.subheader("Latest result")
    cols = st.columns(len(latest["images"]))
    for i, (col, img_b64) in enumerate(zip(cols, latest["images"])):
        img_bytes = base64.b64decode(img_b64)
        with col:
            st.image(img_bytes, use_container_width=True)
            st.download_button(
                "⬇️ Download",
                data=img_bytes,
                file_name=f"prism_{latest['time'].replace(':', '-')}_{i}.png",
                mime="image/png",
                key=f"dl_latest_{i}",
            )

    if len(st.session_state.history) > 1:
        st.divider()
        st.subheader("📜 Prompt history / gallery")
        for entry_idx, entry in enumerate(st.session_state.history[1:], start=1):
            with st.expander(
                f"{entry['time']} — \"{entry['user_prompt']}\" ({entry['style']})"
            ):
                cols = st.columns(len(entry["images"]))
                for i, (col, img_b64) in enumerate(zip(cols, entry["images"])):
                    img_bytes = base64.b64decode(img_b64)
                    with col:
                        st.image(img_bytes, use_container_width=True)
                        st.download_button(
                            "⬇️ Download",
                            data=img_bytes,
                            file_name=f"prism_{entry['time'].replace(':', '-')}_{i}.png",
                            mime="image/png",
                            key=f"dl_hist_{entry_idx}_{i}",
                        )
else:
    st.info("Your generated images will appear here.")
