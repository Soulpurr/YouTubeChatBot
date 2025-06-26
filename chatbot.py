# chatbot.py

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
from summarization_chain import build_full_summarization_chain

from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
load_dotenv()

embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
model = ChatGoogleGenerativeAI(model='models/gemini-1.5-flash')

def extract_video_id(url_or_id):
    """
    Accepts a YouTube full URL or direct video ID and returns the video ID.
    """
    # If it's already a video ID
    if len(url_or_id) == 11 and '/' not in url_or_id:
        return url_or_id

    # Parse full YouTube URL
    try:
        parsed_url = urlparse(url_or_id)
        if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
            return parse_qs(parsed_url.query).get("v", [None])[0]
        elif parsed_url.hostname == "youtu.be":
            return parsed_url.path.lstrip("/")
    except Exception:
        return None

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
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        transcript = " ".join(chunk["text"] for chunk in transcript_list)
        return transcript, transcript_list
    except TranscriptsDisabled:
        return "Transcripts are disabled for this video.", []
    except NoTranscriptFound:
        return "No transcript found in the specified language.", []
    except Exception as e:
        return f"An unexpected error occurred: {e}", []


def format_docs(retrieved_docs):
    return "\n\n".join(doc.page_content for doc in retrieved_docs)


def split_text(transcript,chunk_size=1200,chunk_overlap=200):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.create_documents([transcript])
    return chunks


def create_vectorstore(chunks):
    return FAISS.from_documents(chunks, embedding)






def create_qa_chain(vector_store=None, search_type=None, summaryType=None, transcript=None,language="english"):
    prompt = PromptTemplate(
    template="""
    You are a helpful and concise assistant. Use only the information provided in the context below to answer the question. 
    Do not rely on any outside or pre-trained knowledge.

    If the answer cannot be found in the context, reply with "I don't know."

    Respond in the following language: {language}

    Context:
    {context}

    Question:
    {question}
    """,
        input_variables=["context", "question", "language"]
    )


    prompt1 = PromptTemplate(
    template="""
        You are a professional summarizer. Read the transcript of a YouTube video provided below and generate a clear, complete, and concise summary.

        Make sure to cover all key parts of the content in a way that's easy to understand. Avoid adding any information not present in the transcript.

        Write the summary in the following language: {language}

        Transcript:
        {transcript}
        """,
            input_variables=["transcript", "language"]
    )


    # This will be overwritten conditionally
    final_chain = None

    if summaryType is None:
        # Step 1: Create base retriever using the provided search_type
        search = "mmr" if search_type == "compression" else (search_type or "similarity")

        retriever = vector_store.as_retriever(search_type=search, search_kwargs={"k": 6})

        # Step 2: Wrap retriever with compression layer if requested
        if search_type == "compression":
            compressor = LLMChainExtractor.from_llm(model)
            retriever = ContextualCompressionRetriever(
                base_compressor=compressor,
                base_retriever=retriever
            )

        # Step 3: Create chain for Q&A
        parser = StrOutputParser()
        parallel_chain = RunnableParallel({
            "question": RunnablePassthrough(),
            "context":  RunnableLambda(lambda x: x["question"])|retriever | RunnableLambda(format_docs),
            "language":RunnablePassthrough()
        })
        final_chain = parallel_chain | prompt | model | parser

    elif summaryType == "detailed_summary":
        num_chunks = 10
        avg_chunk_length = len(transcript) // num_chunks
        final_chain = build_full_summarization_chain(model, chunk_size=avg_chunk_length)

    elif summaryType == "concise_summary":
        final_chain = prompt1 | model | StrOutputParser()

    return final_chain



# video_id="hTSaweR8qMI"

# transcript, transcript_list = get_transcript(video_id,"hi")

# chunks = split_text(transcript)
# vector_store = create_vectorstore(chunks)
# chain=create_qa_chain(search_type="mmr",vector_store=vector_store,transcript=transcript,language="hindi")

# print(chain.invoke({"question":"Most expensive date?","language":"hindi"}))
# num_chunks = 10
# avg_chunk_length = len(transcript) // num_chunks
# summarization_chain=build_full_summarization_chain(model,chunk_size=avg_chunk_length)
# print(summarization_chain.invoke(transcript))
#print(model.invoke(f"Summarize the youtube video transcript below \n\n {transcript}"))



## Similarity

# simi_retri=vector_store.as_retriever(search_type="similarity",kwargs={"k":2})
# mmr_retri=vector_store.as_retriever(search_type="mmr",kwargs={"k":2})

# print(f"Similarity Retriever - > {simi_retri.invoke("How is react related to web development?")} \n\n")
# print(f"MMR - > {mmr_retri.invoke("How is react related to web development?")} \n\n")


# compressor=LLMChainExtractor.from_llm(model)
# compression_retriver=ContextualCompressionRetriever(
#     base_compressor=compressor,
#     base_retriever=mmr_retri
# )

# print(f"Compression - > {compression_retriver.invoke("How is react related to web development?")}")

