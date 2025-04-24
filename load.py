from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.docstore.document import Document
import json
import os
import logging
from pinecone import Pinecone, ServerlessSpec
from transformers import pipeline

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

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

index_name = "yoga-poses"

# Create index if it doesn't exist
if index_name not in pc.list_indexes().names():
    try:
        pc.create_index(
            name=index_name,
            dimension=384,  # Matches all-MiniLM-L6-v2
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
        logger.info(f"Created Pinecone index: {index_name}")
    except Exception as e:
        logger.error(f"Failed to create Pinecone index: {e}")
        raise

# Load dataset
try:
    with open("yoga_poses_alldata.json", "r") as f:
        data = json.load(f)
    logger.info("Dataset loaded successfully")
except FileNotFoundError:
    logger.error("yoga_poses_alldata.json not found in project directory")
    raise
except Exception as e:
    logger.error(f"Failed to load dataset: {e}")
    raise

# Initialize text generation model
try:
    generator = pipeline("text-generation", model="gpt2")
    logger.info("GPT-2 model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load GPT-2 model: {e}")
    raise

# Generate descriptions and collect pose types
pose_types = set()
for pose in data:
    try:
        # Generate description
        prompt = f"Describe the benefits of the yoga pose {pose['name']} for {', '.join(pose.get('pose_type', []))} in one sentence."
        description = generator(prompt, max_length=50, num_return_sequences=1)[0]["generated_text"]
        pose["description"] = description.strip()
        # Collect pose types
        pose_types.update(pose.get("pose_type", []))
        logger.info(f"Generated description for {pose['name']}")
    except Exception as e:
        logger.warning(f"Failed to generate description for {pose['name']}: {e}")
        pose["description"] = f"{pose['name']} is a {pose['expertise_level'].lower()} yoga pose."

# Save pose types for app
try:
    with open("pose_types.json", "w") as f:
        json.dump(list(pose_types), f)
    logger.info("pose_types.json saved successfully")
except Exception as e:
    logger.error(f"Failed to save pose_types.json: {e}")
    raise

# Prepare documents
documents = []
for pose in data:
    content = f"{pose['name']} ({pose['expertise_level']}) {pose['description']}"
    
    # Ensure followup_poses is always a list of strings (not null)
    followup_poses = pose.get("followup_poses", [])
    if followup_poses is None:
        followup_poses = []
    # Ensure all items in the list are strings
    followup_poses = [str(pose) for pose in followup_poses if pose is not None]
    
    metadata = {
        "name": pose["name"],
        "sanskrit_name": pose.get("sanskrit_name", ""),
        "expertise_level": pose["expertise_level"],
        "photo_url": pose.get("photo_url", ""),
        "pose_type": pose.get("pose_type", []),
        "description": pose["description"],
        "followup_poses": followup_poses  # Use the sanitized list
    }
    documents.append(Document(page_content=content, metadata=metadata))

# Initialize embeddings
try:
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    logger.info("Embeddings initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize embeddings: {e}")
    raise

# Create Pinecone vector store and add documents
try:
    vector_store = PineconeVectorStore.from_documents(
        documents=documents,
        embedding=embeddings,
        index_name=index_name
    )
    logger.info("Data loaded into Pinecone successfully")
except Exception as e:
    logger.error(f"Failed to load data into Pinecone: {e}")
    raise