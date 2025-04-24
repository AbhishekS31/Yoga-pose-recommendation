import streamlit as st
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from PIL import Image
import requests
import io
import os
import json
import logging
from pinecone import Pinecone

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Custom CSS for styling
st.markdown("""
    <style>
    .main {
        background-color: #f5f7fa;
        padding: 20px;
        font-family: 'Arial', sans-serif;
    }
    .hero {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url('https://images.unsplash.com/photo-1545205597-3d9d02c29597?ixlib=rb-4.0.3&auto=format&fit=crop&w=1350&q=80');
        background-size: cover;
        background-position: center;
        padding: 40px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    }
    .pose-card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s, opacity 0.3s;
        opacity: 0;
        animation: fadeIn 0.5s forwards;
    }
    .pose-card:hover {
        transform: translateY(-5px);
    }
    .pose-title {
        font-size: 1.6em;
        color: #2c3e50;
        margin-bottom: 10px;
        font-weight: bold;
    }
    .pose-detail {
        font-size: 1em;
        color: #34495e;
        margin: 5px 0;
    }
    .sidebar .sidebar-content {
        background-color: #e8ecef;
        padding: 20px;
        border-radius: 10px;
    }
    .stButton>button {
        background-color: #3498db;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        border: none;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #2980b9;
    }
    .footer {
        text-align: center;
        padding: 20px;
        color: #7f8c8d;
        font-size: 0.9em;
        margin-top: 20px;
    }
    .dark-theme .main {
        background-color: #1e2a38;
        color: #ecf0f1;
    }
    .dark-theme .pose-card {
        background-color: #34495e;
        color: #ecf0f1;
    }
    .dark-theme .sidebar .sidebar-content {
        background-color: #2c3e50;
        color: #ecf0f1;
    }
    .dark-theme .pose-title, .dark-theme .pose-detail {
        color: #ecf0f1;
    }
    .dark-theme .hero {
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url('https://images.unsplash.com/photo-1545205597-3d9d02c29597?ixlib=rb-4.0.3&auto=format&fit=crop&w=1350&q=80');
    }
    @keyframes fadeIn {
        to { opacity: 1; }
    }
    </style>
""", unsafe_allow_html=True)

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("Environment variables loaded")
except ImportError:
    logger.warning("python-dotenv not installed; using hardcoded API key")

# Set Pinecone API key
if "PINECONE_API_KEY" not in os.environ:
    os.environ["PINECONE_API_KEY"] = "pcsk_2maiCQ_Hu1RBR1wHMwXJHgeW53oitZ5bwcbuH68BbCq8aHDiV5mqEueENZQQJUGdc1XB3m"

# Initialize Pinecone
try:
    pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    logger.info("Pinecone initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Pinecone: {e}")
    raise

# Initialize embeddings
try:
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    logger.info("Embeddings initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize embeddings: {e}")
    raise

# Load vector store
index_name = "yoga-poses"
try:
    vector_store = PineconeVectorStore(
        index_name=index_name,
        embedding=embeddings
    )
    logger.info("Vector store loaded successfully")
except Exception as e:
    logger.error(f"Failed to load vector store: {e}")
    raise

# Load pose types
try:
    with open("pose_types.json", "r") as f:
        pose_types = ["All"] + json.load(f)
    logger.info("pose_types.json loaded successfully")
except FileNotFoundError:
    pose_types = ["All", "Standing", "Seated", "Balancing", "Backbend", "Forward Bend"]
    st.info("pose_types.json not found. Using default pose types. Run load.py to generate dynamic pose types.")
    logger.warning("pose_types.json not found; using default pose types")
except Exception as e:
    logger.error(f"Failed to load pose_types.json: {e}")
    raise

# Streamlit app
st.markdown('<div class="hero"><h1>🧘 Yoga Pose Recommender</h1><p>Find the perfect yoga poses tailored to your needs.</p></div>', unsafe_allow_html=True)

# Sidebar for filters and theme toggle
with st.sidebar:
    st.header("Filter & Settings")
    expertise_level = st.selectbox(
        "Expertise Level",
        ["All", "Beginner", "Intermediate", "Advanced"],
        help="Filter poses by difficulty level."
    )
    pose_type = st.selectbox(
        "Pose Type",
        pose_types,
        help="Filter poses by type (e.g., Standing, Seated)."
    )
    theme = st.selectbox("Theme", ["Light", "Dark"], help="Switch between light and dark themes.")
    clear_filters = st.button("Clear Filters")

# Apply dark theme if selected
if theme == "Dark":
    st.markdown('<style>.main { background-color: #1e2a38; } .stApp { background-color: #1e2a38; }</style>', unsafe_allow_html=True)
    st.markdown('<div class="dark-theme">', unsafe_allow_html=True)

# Reset filters if clear button is clicked
if clear_filters:
    expertise_level = "All"
    pose_type = "All"

# User input
user_query = st.text_input(
    "Search for a yoga pose:",
    placeholder="e.g., a beginner pose for balance",
    help="Enter a description to find matching yoga poses."
)

# Perform search
if user_query:
    with st.spinner("Searching for poses..."):
        try:
            # Perform vector search
            results = vector_store.similarity_search(user_query, k=6)  # Get top 6 results
            logger.info(f"Search completed for query: {user_query}")

            # Apply filters
            filtered_results = results
            if expertise_level != "All":
                filtered_results = [doc for doc in filtered_results if doc.metadata["expertise_level"] == expertise_level]
            if pose_type != "All":
                filtered_results = [doc for doc in filtered_results if pose_type in doc.metadata["pose_type"]]

            # Display results
            if filtered_results:
                st.subheader("Recommended Yoga Poses")
                cols = st.columns(2)  # Two-column layout
                for idx, doc in enumerate(filtered_results):
                    pose_data = doc.metadata
                    with cols[idx % 2]:
                        with st.container():
                            st.markdown(f"""
                                <div class="pose-card">
                                    <div class="pose-title">{pose_data['name']}</div>
                                    <div class="pose-detail"><b>Sanskrit Name:</b> {pose_data['sanskrit_name']}</div>
                                    <div class="pose-detail"><b>Expertise Level:</b> {pose_data['expertise_level']}</div>
                                    <div class="pose-detail"><b>Pose Type:</b> {', '.join(pose_data['pose_type'])}</div>
                                    <div class="pose-detail"><b>Follow-Up Poses:</b> {', '.join(pose_data.get('followup_poses', [])) or 'None'}</div>
                                </div>
                            """, unsafe_allow_html=True)
                            photo_url = pose_data.get("photo_url")
                            if photo_url:
                                try:
                                    response = requests.get(photo_url, timeout=5)
                                    response.raise_for_status()
                                    img = Image.open(io.BytesIO(response.content))
                                    st.image(img, caption=pose_data['name'], use_container_width=True)
                                    logger.info(f"Loaded image for {pose_data['name']}")
                                except Exception as e:
                                    st.write(f"Image not available: {e}")
                                    logger.warning(f"Failed to load image for {pose_data['name']}: {e}")
                            with st.expander("View Details"):
                                st.write(f"**Description**: {pose_data.get('description', 'No description available')}")
                                st.write("**Benefits**: Improves balance and flexibility (based on pose type).")
                                st.write("**Instructions**: Align your body as shown in the image, breathe deeply, and hold for 30-60 seconds.")
                            st.markdown("[Learn More about Yoga](https://www.yogajournal.com/poses)", unsafe_allow_html=True)
            else:
                st.warning("No poses found matching your criteria. Try adjusting the filters or search query.")
                logger.info("No results found for query and filters")
        except Exception as e:
            st.error(f"An error occurred during search: {e}")
            logger.error(f"Search failed: {e}")

# Close dark theme div if applied
if theme == "Dark":
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
    <div class="footer">
        Powered by Streamlit, Pinecone, and Hugging Face | Created by Abhishek | Dataset from <a href="https://huggingface.co/datasets/omergoshen/yoga_poses">Hugging Face</a>
    </div>
""", unsafe_allow_html=True)