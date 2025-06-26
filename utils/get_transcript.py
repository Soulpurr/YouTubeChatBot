from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
import re
from urllib.parse import urlparse, parse_qs

from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor


def list_available_transcript_languages(video_id):
    """
    Returns a list of available transcript languages for a given YouTube video ID.
    
    Each item in the list is a dictionary with:
    - 'language': Human-readable language name
    - 'code': Language code (e.g., 'en', 'fr')
    - 'auto_generated': Boolean indicating if the transcript is auto-generated
    """
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        available_languages = []

        for transcript in transcript_list:
            available_languages.append({
                "language": transcript.language,
                "code": transcript.language_code,
                "auto_generated": transcript.is_generated
            })

        return available_languages

    except Exception as e:
        return {"error": str(e)}


def get_transcript(video_id,language):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id,languages=[language])
        transcript = " ".join(chunk["text"] for chunk in transcript_list)
        return  transcript,transcript_list
    except TranscriptsDisabled:
        return "Transcripts are disabled for this video.", []
    except NoTranscriptFound:
        return "No transcript found in the specified language.", []
    except Exception as e:
        return f"An unexpected error occurred: {e}", []
    
id="hTSaweR8qMI"
print(list_available_transcript_languages(id))