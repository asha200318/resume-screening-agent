import streamlit as st
import os, tempfile, pandas as pd
import PyPDF2, docx2txt

st.set_page_config(page_title="Resume Screening Agent", layout="wide")
st.title("📄 AI Resume Screening Agent")

st.write("Paste job description, upload resumes (pdf/docx). Agent returns match score and feedback.")

job_desc = st.text_area("Job Description (paste here)", height=200)
uploaded_files = st.file_uploader("Upload resumes (PDF or DOCX)", type=["pdf", "docx"], accept_multiple_files=True)

# ------------------------------
# Text extraction functions
# ------------------------------
def extract_text_from_pdf(file_obj):
    text = ""
    try:
        reader = PyPDF2.PdfReader(file_obj)
        for p in reader.pages:
            page_text = p.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        st.error(f"PDF read error: {e}")
    return text

def extract_text_from_docx(file_obj):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(file_obj.read())
        tmp_path = tmp.name
    text = docx2txt.process(tmp_path)
    return text

def extract_text(uploaded_file):
    uploaded_file.seek(0)
    if uploaded_file.name.lower().endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    elif uploaded_file.name.lower().endswith(".docx"):
        return extract_text_from_docx(uploaded_file)
    else:
        return ""

# ------------------------------
# Dummy scoring function
# ------------------------------
def ask_openai_for_score(job_description, resume_text):
    # Temporary dummy response for testing UI without API
    return {
        "score": 85,
        "short_feedback": "Good match for the job description.",
        "highlights": ["Python", "Django", "SQL"]
    }

# ------------------------------
# Analyze resumes
# ------------------------------
if st.button("Analyze Resumes"):
    if not job_desc:
        st.warning("Please paste job description first.")
    elif not uploaded_files:
        st.warning("Please upload one or more resumes.")
    else:
        results = []
        with st.spinner("Analyzing..."):
            for f in uploaded_files:
                txt = extract_text(f)
                if not txt.strip():
                    st.warning(f"No text extracted from {f.name}. It might be scanned image PDF.")
                    score = None
                    feedback = "No text extracted."
                    highlights = []
                else:
                    resp = ask_openai_for_score(job_desc, txt)
                    score = resp.get("score")
                    feedback = resp.get("short_feedback")
                    highlights = resp.get("highlights", [])

                st.subheader(f.name)
                st.write("*Score:*", score)
                st.write("*Feedback:*", feedback)
                if highlights:
                    st.write("*Highlights:*", ", ".join(highlights))

                results.append({"filename": f.name, "score": score, "feedback": feedback, "highlights": highlights})

        # Show table and allow CSV download
        df = pd.DataFrame(results)
        st.markdown("---")
        st.subheader("All Results")
        st.dataframe(df)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download results CSV", data=csv, file_name="screening_results.csv", mime="text/csv")


