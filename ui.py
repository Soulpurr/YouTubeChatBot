import streamlit as st

from utils.create_qa_chain import create_qa_chain
from utils.get_transcript import get_transcript
from utils.split_text import split_text
from utils.create_vectorstore import create_vectorstore
from utils.extract_video_id import extract_video_id
from utils.get_transcript import list_available_transcript_languages
st.set_page_config(page_title="🎥 YouTube Transcript Assistant", layout="centered")
st.title("🎥 YouTube Transcript Assistant")

video_input = st.text_input("Enter YouTube Video URL or ID:")

# Language detection
selected_language = None
available_languages = []

if video_input:
    video_id = extract_video_id(video_input)
    if video_id:
        lang_info = list_available_transcript_languages(video_id)
        if isinstance(lang_info, dict) and "error" in lang_info:
            st.error(f"⚠️ Error: {lang_info['error']}")
        elif lang_info:
            available_languages = [f"{lang['language']} ({lang['code']})" for lang in lang_info]
            selected_language_display = st.selectbox("Select transcript language:", available_languages)
            selected_language = selected_language_display.split("(")[-1].strip(")")
        else:
            st.warning("⚠️ No transcripts found for this video.")

search_type = st.radio(
    "Select retrieval method for Q&A:",
    options=["similarity", "mmr", "compression"],
    index=1
)

question = st.text_input("Ask a question based on the video transcript:")

col1, col2, col3 = st.columns(3)

if col1.button("Get Answer"):
    with st.spinner("Processing..."):
        video_id = extract_video_id(video_input)
        if not video_id:
            st.error("❌ Invalid YouTube URL or ID.")
        elif not selected_language:
            st.error("❌ Please select a transcript language first.")
        else:
            transcript, transcript_list = get_transcript(video_id, selected_language)
            if isinstance(transcript, str) and not transcript_list:
                st.error(transcript)
            else:
                chunks = split_text(transcript)
                vector_store = create_vectorstore(chunks)
                qa_chain = create_qa_chain(vector_store=vector_store, search_type=search_type, language=selected_language, transcript=transcript)
                answer = qa_chain.invoke({"question": question, "language": selected_language})
                st.success("✅ Answer:")
                st.write(answer)

if col2.button("Generate Concise Summary"):
    with st.spinner("Summarizing..."):
        video_id = extract_video_id(video_input)
        if not video_id:
            st.error("❌ Invalid YouTube URL or ID.")
        elif not selected_language:
            st.error("❌ Please select a transcript language first.")
        else:
            transcript, transcript_list = get_transcript(video_id, selected_language)
            if isinstance(transcript, str) and not transcript_list:
                st.error(transcript)
            else:
                chain = create_qa_chain(summaryType="concise_summary", transcript=transcript, language=selected_language)
                summary = chain.invoke({"transcript": transcript, "language": selected_language})
                st.success("✅ Concise Summary:")
                st.write(summary)

if col3.button("Generate Detailed Summary"):
    with st.spinner("Summarizing..."):
        video_id = extract_video_id(video_input)
        if not video_id:
            st.error("❌ Invalid YouTube URL or ID.")
        elif not selected_language:
            st.error("❌ Please select a transcript language first.")
        else:
            transcript, transcript_list = get_transcript(video_id, selected_language)
            if isinstance(transcript, str) and not transcript_list:
                st.error(transcript)
            else:
                chain = create_qa_chain(summaryType="detailed_summary", transcript=transcript, language=selected_language)
                summary = chain.invoke(transcript)
                st.success("✅ Detailed Summary:")
                st.write(summary)
