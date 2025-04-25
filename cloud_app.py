"""
Cloud-specific version of the YogaAI app with event loop handling built in.
For local development, use run_app.py instead.
"""

import os
# Configure environment variables first
os.environ["PYTHONWARNINGS"] = "ignore"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

# Set up event loop before any other imports
import asyncio
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

try:
    import nest_asyncio
    nest_asyncio.apply()
except ImportError:
    pass

# Now we can safely import the rest
import streamlit as st

# Streamlit app - set_page_config must be the first Streamlit command
st.set_page_config(
    page_title="YogaAI - Find Your Perfect Pose",
    page_icon="🧘",
    layout="wide"
)

# Import the remaining code from app.py
# We're doing an exec to avoid code duplication
with open("app.py", "r") as f:
    app_code = f.read()

# Extract everything after the st.set_page_config
if "st.set_page_config" in app_code:
    app_code = app_code.split("st.set_page_config(", 1)[1]
    app_code = app_code.split(")", 1)[1]

# Execute the remaining code
exec(app_code)