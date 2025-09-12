import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import os
import PyPDF2
import docx

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set")

client = OpenAI(api_key=OPENAI_API_KEY)
# ------------------------
# File reader
# ------------------------
def extract_text_from_file(uploaded_file):
    file_extension = uploaded_file.name.split(".")[-1].lower()

    if file_extension == "pdf":
        reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

    elif file_extension == "docx":
        doc = docx.Document(uploaded_file)
        return "\n".join([p.text for p in doc.paragraphs])

    elif file_extension == "txt":
        return uploaded_file.read().decode("utf-8")

    else:
        raise ValueError("Unsupported file format! Please upload PDF, DOCX, or TXT.")


# ------------------------
# AI helper
# ------------------------
def generate_questions(resume_text, language="English"):
    language_instruction = "Please provide questions and answers in English."
    if language == "Hindi":
        language_instruction = "Please provide questions and answers in Hindi."


    prompt = f"""
    You are an interviewer. Based on this resume, generate 10 interview questions and answers.
    Make a mix of:
    - Technical questions (skills, projects, experience)
    - HR/Behavioral questions (teamwork, goals, challenges)
    {language_instruction}
    
    Resume:
    {resume_text}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1500
    )

    return response.choices[0].message.content


# ------------------------
# Streamlit UI
# ------------------------
st.set_page_config(page_title="🎯 AI Interview Questions Generator", layout="wide")

st.title("🎯 AI Interview Questions Generator")
st.write("Upload your resume and get smart interview questions!")

# Language selector
language = st.selectbox("Select Language", ["English", "Hindi"])

uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx", "txt"])

if uploaded_file is not None:
    try:
        resume_text = extract_text_from_file(uploaded_file)
        st.success("✅ Resume uploaded and text extracted!")

        if st.button("Generate Interview Questions"):
            with st.spinner("AI is generating interview questions..."):
                try:
                    questions = generate_questions(resume_text, language)
                    st.subheader("📋 Suggested Interview Questions & Answers")
                    for block in questions.split("\n"):
                        st.write(block)

                except Exception as e:
                    st.error(f"❌ Error while generating questions: {e}")

    except Exception as e:
        st.error(f"❌ Error processing resume: {e}")
