"""Apple Human Interface–inspired dark UI tokens + global Streamlit CSS."""

from __future__ import annotations

import streamlit as st

# Approximates iOS/macOS dark mode system colors (SF Pro falls back to system UI fonts).
APPLE_CSS = """
<style>
/* --- Tokens (Apple-like dark mode) --- */
:root {
  --apple-bg: #000000;
  --apple-bg-elevated: #1C1C1E;
  --apple-bg-secondary: #2C2C2E;
  --apple-bg-tertiary: #3A3A3C;
  --apple-label: rgba(255, 255, 255, 0.92);
  --apple-secondary-label: rgba(235, 235, 245, 0.60);
  --apple-tertiary-label: rgba(235, 235, 245, 0.30);
  --apple-separator: rgba(84, 84, 88, 0.65);
  --apple-blue: #0A84FF;
  --apple-blue-soft: rgba(10, 132, 255, 0.18);
  --apple-green: #30D158;
  --apple-red: #FF453A;
  --apple-radius-lg: 14px;
  --apple-radius-md: 10px;
  --apple-radius-sm: 8px;
  --apple-font: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text",
    "Segoe UI", system-ui, sans-serif;
}

html, body, [data-testid="stAppViewContainer"] {
  font-family: var(--apple-font) !important;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* App chrome */
[data-testid="stHeader"] {
  background: transparent !important;
}
[data-testid="stToolbar"] {
  background: rgba(28, 28, 30, 0.72) !important;
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-bottom: 1px solid var(--apple-separator);
}

[data-testid="stAppViewContainer"] > .main {
  background: var(--apple-bg) !important;
}

section.main > div {
  padding-top: 1.25rem !important;
  padding-bottom: 3rem !important;
}

.block-container {
  padding-left: max(1.5rem, 4vw) !important;
  padding-right: max(1.5rem, 4vw) !important;
  max-width: 1180px !important;
}

/* Typography hierarchy */
h1 {
  font-weight: 600 !important;
  letter-spacing: -0.028em !important;
  font-size: clamp(1.65rem, 3vw, 2.05rem) !important;
  color: var(--apple-label) !important;
  margin-bottom: 0.35rem !important;
}

h2, h3 {
  font-weight: 600 !important;
  letter-spacing: -0.02em !important;
  color: var(--apple-label) !important;
}

[data-testid="stCaptionContainer"] p {
  color: var(--apple-secondary-label) !important;
  font-size: 0.9375rem !important;
  line-height: 1.45 !important;
}

/* Sidebar — grouped inset surface */
[data-testid="stSidebar"] {
  background: var(--apple-bg-elevated) !important;
  border-right: 1px solid var(--apple-separator) !important;
}
[data-testid="stSidebar"] .block-container {
  padding-top: 1.25rem !important;
}

/* Segmented control (horizontal radio) */
div[data-testid="stRadio"] > div {
  flex-direction: row !important;
  flex-wrap: wrap !important;
  gap: 0 !important;
  padding: 3px !important;
  background: var(--apple-bg-secondary) !important;
  border-radius: var(--apple-radius-md) !important;
  border: 1px solid var(--apple-separator) !important;
  width: fit-content !important;
  max-width: 100% !important;
}

div[data-testid="stRadio"] label {
  margin: 0 !important;
  padding: 0.45rem 1.15rem !important;
  border-radius: var(--apple-radius-sm) !important;
  font-weight: 500 !important;
  font-size: 0.9rem !important;
  color: var(--apple-secondary-label) !important;
  transition: background 0.15s ease, color 0.15s ease !important;
}

div[data-testid="stRadio"] label p {
  margin: 0 !important;
}

div[data-testid="stRadio"] label:has(input:checked) {
  background: var(--apple-bg-tertiary) !important;
  color: var(--apple-label) !important;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.35) !important;
}

div[data-testid="stRadio"] label:hover {
  color: var(--apple-label) !important;
}

/* Hide default radio circle affordance where possible */
div[data-testid="stRadio"] label input {
  margin-right: 0 !important;
}

/* Primary buttons — filled capsule */
.stButton > button[kind="primary"],
button[kind="primary"] {
  background: var(--apple-blue) !important;
  color: #ffffff !important;
  border: none !important;
  border-radius: var(--apple-radius-md) !important;
  font-weight: 600 !important;
  padding: 0.5rem 1rem !important;
  box-shadow: none !important;
}

.stButton > button[kind="secondary"],
button[kind="secondary"] {
  background: var(--apple-bg-secondary) !important;
  color: var(--apple-label) !important;
  border: 1px solid var(--apple-separator) !important;
  border-radius: var(--apple-radius-md) !important;
}

/* Chat */
[data-testid="stChatMessage"] {
  background: var(--apple-bg-elevated) !important;
  border: 1px solid var(--apple-separator) !important;
  border-radius: var(--apple-radius-lg) !important;
  padding: 0.85rem 1rem !important;
  margin-bottom: 0.65rem !important;
}

[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p,
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li {
  color: var(--apple-label) !important;
  line-height: 1.5 !important;
}

[data-testid="stChatInput"] {
  border-radius: var(--apple-radius-lg) !important;
  border: 1px solid var(--apple-separator) !important;
  background: var(--apple-bg-secondary) !important;
}

[data-testid="stChatInputSubmitButton"] button {
  border-radius: var(--apple-radius-md) !important;
}

/* Alerts / callouts */
div[data-testid="stAlert"] {
  border-radius: var(--apple-radius-md) !important;
  border-width: 1px !important;
}

/* Spinner */
.stSpinner > div {
  border-color: var(--apple-blue) transparent transparent transparent !important;
}

/* Dividers */
hr {
  border: none !important;
  border-top: 1px solid var(--apple-separator) !important;
}

[data-testid="stHorizontalBlock"] hr {
  margin: 1rem 0 !important;
}

/* Folium / embedded maps */
iframe[title="streamlit_folium.streamlit_folium"],
iframe[src*="folium"],
[data-testid="stIFrame"] iframe {
  border-radius: var(--apple-radius-md) !important;
  border: 1px solid var(--apple-separator) !important;
}

/* Dataframes */
[data-testid="stDataFrame"] {
  border-radius: var(--apple-radius-md) !important;
  border: 1px solid var(--apple-separator) !important;
  overflow: hidden !important;
}

/* Expanders */
.streamlit-expanderHeader {
  font-weight: 600 !important;
  border-radius: var(--apple-radius-sm) !important;
}

/* Footer */
footer[data-testid="stFooter"] {
  opacity: 0.35;
}

/* Links inside markdown */
a {
  color: #64D2FF !important;
}
</style>
"""

HERO_MARKDOWN = """
<div class="apple-hero-wrap">
  <p class="apple-eyebrow">Bengaluru · Rentals</p>
  <h1 class="apple-hero-title">Rental Truth-Teller</h1>
  <p class="apple-hero-sub">The second opinion your broker doesn’t want you to have.</p>
</div>
"""


def inject_apple_dark_theme() -> None:
    """Inject global CSS once per run (idempotent visually)."""
    st.markdown(APPLE_CSS, unsafe_allow_html=True)


def render_hero() -> None:
    """Large-type hero aligned with Apple marketing typography rhythm."""
    st.markdown(
        """
<style>
.apple-hero-wrap {
  margin-bottom: 1.35rem;
  padding-bottom: 0.25rem;
}
.apple-eyebrow {
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: rgba(235, 235, 245, 0.45);
  margin: 0 0 0.35rem 0;
}
.apple-hero-title {
  font-size: clamp(1.85rem, 4vw, 2.45rem);
  font-weight: 600;
  letter-spacing: -0.035em;
  line-height: 1.1;
  margin: 0 0 0.5rem 0;
  color: rgba(255, 255, 255, 0.95);
}
.apple-hero-sub {
  font-size: 1.05rem;
  line-height: 1.45;
  color: rgba(235, 235, 245, 0.58);
  margin: 0;
  max-width: 36rem;
}
</style>
"""
        + HERO_MARKDOWN,
        unsafe_allow_html=True,
    )


def section_title(text: str) -> None:
    """Sidebar / section label style."""
    st.markdown(
        f'<p style="margin:0 0 0.5rem 0;font-size:0.72rem;font-weight:600;'
        f'letter-spacing:0.07em;text-transform:uppercase;color:rgba(235,235,245,0.45);">'
        f"{text}</p>",
        unsafe_allow_html=True,
    )
