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
from utils.format_docs import format_docs
load_dotenv()

embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
model = ChatGoogleGenerativeAI(model='models/gemini-1.5-flash')



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


