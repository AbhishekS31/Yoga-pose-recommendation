#!/usr/bin/env python3
"""
Startup script for the YogaAI application that properly handles event loops.
This solves the common issue between PyTorch and asyncio event loops.
"""

import os
import sys
import subprocess

# Prevent PyTorch warnings and improve compatibility
os.environ["PYTHONWARNINGS"] = "ignore"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1" 
os.environ["MKL_NUM_THREADS"] = "1"

# Create a dedicated Python process with the right event loop setup
startup_script = """
import asyncio
import nest_asyncio
import torch

# Initialize and apply event loop policies before anything else
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
nest_asyncio.apply()

# Force PyTorch to run single-threaded
torch.set_num_threads(1)

# Import and run streamlit programmatically
import streamlit.web.bootstrap as bootstrap
bootstrap._load_config_options()
bootstrap._register_static_file_handler()
bootstrap._fix_sys_path()

# Run the actual app
bootstrap._run_with_logger('streamlit run app.py {args}', {{}})
"""

# Write the startup script to a temporary file
with open("temp_startup.py", "w") as f:
    f.write(startup_script)

# Install required packages if not already installed
try:
    import nest_asyncio
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "nest_asyncio"])

# Run the temporary script
subprocess.call([sys.executable, "temp_startup.py"])

# Clean up
if os.path.exists("temp_startup.py"):
    os.remove("temp_startup.py")