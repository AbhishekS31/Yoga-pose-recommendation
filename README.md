
# 🧘 Yoga Pose Recommender

Yoga Pose Reccomender is an intelligent yoga pose recommendation system built with Streamlit, Pinecone vector database, and HuggingFace embeddings. The application helps users discover yoga poses tailored to their needs, experience level, and preferences.

## Features

- 🔍 **Natural Language Search**: Find yoga poses using conversational queries
- 🧠 **AI-Powered Recommendations**: Get personalized pose suggestions based on your needs
- 🏷️ **Smart Filtering**: Filter poses by expertise level and pose type
- 🌓 **Light/Dark Mode**: Choose your preferred visual theme
- 📊 **Pose Details**: View descriptions, benefits, and follow-up poses

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/yogaa.git
   cd yogaa
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv myenv
   source myenv/bin/activate  # On Windows: myenv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your Pinecone API key:
   ```bash
   echo "PINECONE_API_KEY=your_pinecone_api_key_here" > .env
   ```

## Usage

### Data Loading

Before running the app, you need to load the yoga pose data into Pinecone:

```bash
python load.py
```

This script:
- Loads yoga pose data from `yoga_poses_alldata.json`
- Generates descriptions using GPT-2
- Creates embeddings using HuggingFace's sentence-transformers
- Stores vectors in Pinecone for efficient similarity search
- Creates a `pose_types.json` file for the app

### Running the App

Start the Streamlit application:

```bash
streamlit run app.py
```

The app will be accessible at http://localhost:8501

## Project Structure

- `app.py`: Main Streamlit application
- `load.py`: Script to load data and create embeddings
- `yoga_poses_alldata.json`: Dataset of yoga poses
- `pose_types.json`: Generated list of pose types
- `requirements.txt`: Project dependencies

## Technologies Used

- **Streamlit**: Frontend web application
- **Pinecone**: Vector database for similarity search
- **LangChain**: Framework for working with language models
- **HuggingFace**: Embeddings and models
- **Sentence-Transformers**: For creating text embeddings

## Requirements

- Python 3.8+
- Pinecone account with API key
- Internet connection (for loading models and images)

## License

MIT

## Acknowledgements

- Yoga pose dataset from [HuggingFace](https://huggingface.co/datasets/omergoshen/yoga_poses)
- Built with [Streamlit](https://streamlit.io), [Pinecone](https://www.pinecone.io), and [HuggingFace](https://huggingface.co)