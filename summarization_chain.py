from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnableSequence
from langchain.text_splitter import RecursiveCharacterTextSplitter

# You'll pass the same model instance you use for QA

def get_chunk_summarization_chain(model):
    prompt = PromptTemplate(
        template="""
        You're summarizing a YouTube transcript split into parts.
        This is one part of the full transcript.
        Summarize this part clearly and concisely.

        ---
        {chunk}
        """,
        input_variables=["chunk"]
    )

    return prompt | model | StrOutputParser()

def get_final_summary_chain(model):
    prompt = PromptTemplate(
        template="""
        These are partial summaries of different segments of a long YouTube transcript.
        Write a single unified and concise summary based on them.

        ---
        {partial_summaries}
        """,
        input_variables=["partial_summaries"]
    )

    return prompt | model | StrOutputParser()

def build_full_summarization_chain(model, chunk_size=1000, chunk_overlap=200):
    # Step 1: Split transcript to chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    split_chunks = RunnableLambda(lambda transcript: splitter.create_documents([transcript]))

    # Step 2: Summarize each chunk
    chunk_summarizer = get_chunk_summarization_chain(model)
    summarize_chunks = RunnableLambda(lambda docs: [chunk_summarizer.invoke({"chunk": doc.page_content}) for doc in docs])

    # Step 3: Combine partials and summarize them
    combine_summaries = RunnableLambda(
        lambda partials: {"partial_summaries": "\n\n".join(partials)}
    ) 

    # Full chain
    return split_chunks | summarize_chunks | combine_summaries
