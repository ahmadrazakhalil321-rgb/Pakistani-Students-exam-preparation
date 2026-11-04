import streamlit as st
import os
import pypdf
import google.generativeai as genai

# Page configuration
st.set_page_config(
    page_title="PakStudy Exam Prep AI",
    page_icon="📚",
    layout="wide"
)

# App title and description
st.title("🇵🇰 Pakistani Student Exam Prep AI")
st.markdown("Upload your Matric or Intermediate textbook chapter, generate exam-style questions, and get detailed answers evaluated in **English, Urdu, or Roman Urdu**.")

# Sidebar for configuration
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("Enter your Google Gemini API Key", type="password")

language = st.sidebar.selectbox(
    "Select Explanation Language",
    ["Roman Urdu", "Urdu", "English"]
)

if not api_key:
    st.warning("Please enter your Google Gemini API Key in the sidebar to proceed.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# Helper function to extract text from uploaded file
def extract_text(uploaded_file):
    if uploaded_file.type == "application/pdf":
        reader = pypdf.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    elif uploaded_file.type == "text/plain":
        return uploaded_file.getvalue().decode("utf-8")
    return ""

uploaded_file = st.file_uploader("Upload Chapter (PDF or TXT)", type=["pdf", "txt"])

if uploaded_file is not None:
    with st.spinner("Processing textbook chapter..."):
        chapter_text = extract_text(uploaded_file)
        st.session_state['chapter_text'] = chapter_text
        st.success(f"Successfully loaded chapter! ({len(chapter_text)} characters extracted)")

if 'chapter_text' in st.session_state and st.session_state['chapter_text']:
    chapter_text = st.session_state['chapter_text']
    
    tab1, tab2 = st.tabs(["📝 Generate Practice Questions", "💡 Answer Evaluation & Tutor"])
    
    with tab1:
        st.header("Generate Chapter Practice Questions")
        q_type = st.selectbox("Select Question Type", ["Multiple Choice Questions (MCQs)", "Short Questions", "Long / Detailed Questions"])
        num_questions = st.slider("Number of Questions", 3, 10, 5)
        
        if st.button("Generate Questions"):
            with st.spinner("Generating exam questions based on Pakistani board standards..."):
                prompt = f"""
                You are an expert Pakistani board exam tutor (Matric / Intermediate FSc).
                Based on the textbook chapter provided below, generate {num_questions} {q_type}.
                Language requirement for the questions: {language}. If Urdu or Roman Urdu is selected, make it natural and easy for Pakistani students to understand.
                
                Chapter Content:
                {chapter_text[:15000]}
                
                Provide clear questions and include an answer key at the bottom.
                """
                response = model.generate_content(prompt)
                st.markdown("### Generated Practice Questions")
                st.markdown(response.text)
                st.session_state['last_questions'] = response.text
                
    with tab2:
        st.header("Answer Evaluation & Explanation")
        st.markdown("Test your preparation! Paste a question (or pick one generated earlier), write your answer, and let the AI evaluate it against the chapter.")
        
        user_question = st.text_area("Question", value=st.session_state.get('last_questions', ''))
        user_answer = st.text_area("Your Answer")
        
        if st.button("Evaluate Answer"):
            if not user_answer.strip():
                st.warning("Please enter your answer first.")
            else:
                with st.spinner("Evaluating your answer and preparing detailed feedback..."):
                    eval_prompt = f"""
                    You are a strict and helpful Pakistani board examiner (Matric/Intermediate).
                    Evaluate the student's answer based strictly on the textbook chapter text provided below.
                    
                    Language requirement for your feedback: {language}.
                    
                    Question:
                    {user_question}
                    
                    Student's Answer:
                    {user_answer}
                    
                    Textbook Chapter Reference:
                    {chapter_text[:15000]}
                    
                    Provide:
                    1. Correctness Assessment (Marks / Evaluation status)
                    2. Detailed feedback explaining what was correct and what was missing.
                    3. Model answer in {language}.
                    """
                    eval_response = model.generate_content(eval_prompt)
                    st.markdown("### Examiner Feedback")
                    st.markdown(eval_response.text)
