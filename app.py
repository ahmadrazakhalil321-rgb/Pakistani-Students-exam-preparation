import streamlit as st
from google import genai
from pypdf import PdfReader

# Page Configuration
st.set_page_config(
    page_title="Pakistani Exam Prep AI", page_icon="📚", layout="wide"
)

st.title("🇵🇰 Pakistani Matric & Intermediate Exam Prep AI")
st.markdown(
    "Upload your textbook chapter, generate board-style practice questions,"
    " test your knowledge, and get feedback in **English**, **Urdu**, or **Roman"
    " Urdu**!"
)

# Sidebar for Configuration & Settings
with st.sidebar:
  st.header("⚙️ Configuration")
  api_key = st.text_input(
      "Enter Gemini API Key",
      type="password",
      help="Get your key from Google AI Studio",
  )

  st.header("🌐 Language Preference")
  language = st.selectbox(
      "Select Explanation Language", ["English", "Roman Urdu", "Urdu"]
  )

  st.markdown("---")
  st.markdown("### 📖 How to Use:")
  st.markdown(
      "1. Enter your Gemini API Key.\n2. Upload a chapter PDF or text file.\n3."
      " Click **Generate Practice Questions**.\n4. Type your answer and click"
      " **Evaluate Answer** for instant AI feedback!"
  )

if not api_key:
  st.warning(
      "⚠️ Please enter your Gemini API Key in the sidebar to get started."
  )
else:
  # Initialize Gemini Client
  client = genai.Client(api_key=api_key)

  uploaded_file = st.file_uploader(
      "Upload Textbook Chapter (PDF or TXT)", type=["pdf", "txt"]
  )

  chapter_text = ""
  if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
      reader = PdfReader(uploaded_file)
      for page in reader.pages:
        text = page.extract_text()
        if text:
          chapter_text += text + "\n"
    else:
      chapter_text = uploaded_file.read().decode("utf-8")

    if chapter_text:
      st.success(
          f"✅ Chapter uploaded successfully! Extracted {len(chapter_text)}"
          " characters."
      )

      with st.expander("👀 Preview Extracted Chapter Text"):
        st.write(chapter_text[:1500] + "...")

      st.markdown("---")
      col1, col2 = st.columns(2)

      with col1:
        if st.button("📝 Generate Practice Questions", use_container_width=True):
          with st.spinner(
              "Generating board-style Short & Long questions..."
          ):
            prompt = (
                "Based on the following textbook chapter text, generate 3-4"
                " board-style exam questions (mix of Short Questions and Long"
                " Questions) suitable for Pakistani Matric/Intermediate exams."
                f" Respond in {language}.\n\nChapter Text:\n{chapter_text[:12000]}"
            )
            response = client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt
            )
            st.session_state["questions"] = response.text

      # Display Questions if available
      if "questions" in st.session_state:
        st.subheader("📋 Practice Questions")
        st.markdown(st.session_state["questions"])

        st.markdown("---")
        st.subheader("✍️ Test Your Answer")
        user_answer = st.text_area(
            "Type your answer to the questions above:", height=150
        )

        if st.button("🔍 Evaluate Answer", use_container_width=True):
          if user_answer.strip():
            with st.spinner("Evaluating your answer against the chapter..."):
              eval_prompt = (
                  "You are an expert Pakistani board exam examiner. Based on"
                  " the textbook chapter text provided below, evaluate the"
                  " student's answer. Provide constructive feedback,"
                  " constructive grading (out of total marks), and the ideal"
                  f" model answer. You MUST explain everything in {language}.\n\nChapter"
                  f" Text:\n{chapter_text[:12000]}\n\nStudent's"
                  f" Answer:\n{user_answer}"
              )
              eval_response = client.models.generate_content(
                  model="gemini-2.5-flash", contents=eval_prompt
              )
              st.markdown("### 📊 Evaluation & Feedback")
              st.markdown(eval_response.text)
          else:
            st.warning("Please type your answer before evaluating.")
