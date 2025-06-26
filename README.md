# 🎥 YouTube Transcript Assistant

This is a Streamlit-based app that allows users to interact with YouTube video transcripts. You can:
- Ask questions about a video transcript
- Generate concise or detailed summaries
- Choose from available transcript languages
- Get responses in the language of the transcript

## 🔧 Features

- **Multilingual Transcript Support**: Detects available languages and allows you to select which one to use.
- **Retrieval-Augmented Q&A**: Ask context-aware questions using similarity, MMR, or compressed retrievers.
- **Summarization Options**: Choose between a concise or detailed summary of the transcript.
- **Gemini Integration**: Uses Gemini 1.5 Flash API for high-quality responses and summaries.

## 📂 Project Structure

├── ui.py # Main Streamlit application
├── chatbot.py # Utility logic for transcript retrieval, vector store, chains
├── summarization_chain.py # Logic for hierarchical summarization
├── .env # Environment file (ignored by Git)
├── .gitignore # Git ignore configuration
└── requirements.txt # Required Python packages

bash
Copy
Edit

## ▶️ Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/Soulpurr/YouTubeChatBot.git
2. Install dependencies
Make sure you have Python 3.10+ and install dependencies with:

bash
Copy
Edit
pip install -r requirements.txt
3. Set up environment
Create a .env file and add your Gemini API key:

ini
Copy
Edit
GOOGLE_API_KEY=your_google_api_key
4. Run the app
bash
Copy
Edit
streamlit run ui.py
✅ Usage
Paste a YouTube URL or video ID.

Select a language from the available transcript options.

Ask questions, or click buttons to generate summaries.

🧠 Technologies Used
LangChain for building language model chains

Gemini API (Google Generative AI) for summarization and answering

YouTube Transcript API for fetching transcripts

Streamlit for building the UI

FAISS for vector search

