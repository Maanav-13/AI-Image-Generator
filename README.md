# 🎨 Prism — AI Image Generator Chatbot

A simple, clean Streamlit web app that turns text prompts into AI-generated
images using the **Stability AI** image generation API. Pick a style, type
a prompt, and get an image — with prompt history, downloads, and a few
other extras built in.

## What it does

- Type a prompt (e.g. *"A futuristic Indian city at night"*).
- Choose a visual style (Realistic, Cyberpunk, Anime, Watercolor, Fantasy,
  Minimalist). The app rewrites your prompt behind the scenes to include
  style-specific keywords before sending it to the API — e.g. choosing
  "Anime" turns *"A cat wearing sunglasses"* into
  *"A cat wearing sunglasses, anime style, detailed, vibrant colors, ..."*.
- Click **Generate** and the image appears in the app.
- Every generation is saved to a **prompt history / gallery** for the
  session, each with a **download** button.
- Extras: negative prompt input, image size (aspect ratio) selector,
  generate up to 4 images at once, a random-prompt button, and a
  dark/light theme toggle.

## File structure

```
prism-image-gen/
├── app.py              # Streamlit UI only (layout, session state, widgets)
├── api_client.py        # All Stability AI API calls live here
├── prompts.py           # Style definitions + prompt-building logic
├── requirements.txt
├── .env.example          # Template for your local API key
├── .streamlit/
│   └── secrets.toml.example   # Template for Streamlit Cloud secrets
├── .gitignore
└── README.md
```

This separation means you can change the API provider in `api_client.py`,
add new styles in `prompts.py`, or redesign the UI in `app.py` without the
other files needing to change.

## How to run it locally

1. **Clone the repo and install dependencies** (Python 3.9+ recommended):

   ```bash
   git clone <your-repo-url>
   cd prism-image-gen
   python -m venv venv
   source venv/bin/activate   # on Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Add your API key** (see next section).

3. **Run the app**:

   ```bash
   streamlit run app.py
   ```

   Streamlit will open the app at `http://localhost:8501`.

## How to add your API key

1. Sign up at [platform.stability.ai](https://platform.stability.ai/) and
   create an API key under **Account → API Keys**.
2. Copy the example env file:

   ```bash
   cp .env.example .env
   ```

3. Open `.env` and paste your key:

   ```
   STABILITY_API_KEY=sk-your-real-key-here
   ```

   `.env` is listed in `.gitignore`, so it will never be committed.

The app reads the key via `os.environ["STABILITY_API_KEY"]` in
`api_client.py` — it is never hardcoded anywhere in the source.

## How to deploy it

### Streamlit Community Cloud (easiest)

1. Push this repo to GitHub (see below for a script that does this).
2. Go to [share.streamlit.io](https://share.streamlit.io/), sign in with
   GitHub, and click **New app**.
3. Select your repo, branch, and set the main file to `app.py`.
4. Before deploying, open **Advanced settings → Secrets** and add:

   ```toml
   STABILITY_API_KEY = "sk-your-real-key-here"
   ```

5. Click **Deploy**. The app reads this automatically via `st.secrets` in
   `app.py` — no code changes needed.

### Other platforms (Render, Railway, etc.)

Set `STABILITY_API_KEY` as an environment variable in the platform's
dashboard/secrets manager, and use a start command like:

```bash
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

## Known limitation

The Stability AI "Stable Image Core" endpoint generates **one image per
API request**. The "generate multiple images" option in this app simply
sends multiple sequential requests under the hood, so requesting 4 images
takes roughly 4x as long as requesting 1, and partial failures (e.g. one
request times out) can result in fewer than the requested number of
images being returned.
