import streamlit as st
from pypdf import PdfReader
from google import genai


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="StudyAI",
    page_icon="🎓",
    layout="wide"
)


# =========================================================
# GEMINI CONNECTION
# =========================================================

try:
    client = genai.Client(
        api_key=st.secrets["GEMINI_API_KEY"]
    )
except Exception as e:
    client = None


MODEL_NAME = "gemini-2.0-flash"


# =========================================================
# APP TITLE
# =========================================================

st.title("🎓 StudyAI")
st.subheader("Your Personal AI Study Assistant")

st.write(
    "Upload your study notes and use AI to summarize them, "
    "generate quizzes, or ask questions."
)

st.divider()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("⚙️ StudyAI Settings")

st.sidebar.write("Current AI Model:")

st.sidebar.code(MODEL_NAME)


# =========================================================
# PDF TEXT EXTRACTION
# =========================================================

def extract_text_from_pdf(uploaded_file):

    try:

        pdf_reader = PdfReader(uploaded_file)

        extracted_text = ""

        for page in pdf_reader.pages:

            text = page.extract_text()

            if text:
                extracted_text += text + "\n"

        return extracted_text

    except Exception as e:

        st.error("❌ Error reading PDF.")

        st.code(str(e))

        return ""


# =========================================================
# ASK GEMINI
# =========================================================

def ask_ai(prompt):

    if client is None:

        st.error(
            "❌ Gemini API connection could not be created."
        )

        return None

    try:

        response = client.models.generate_content(

            model=MODEL_NAME,

            contents=prompt

        )

        return response.text

    except Exception as e:

        st.error(
            "❌ Gemini AI could not generate a response."
        )

        st.code(str(e))

        return None


# =========================================================
# PDF UPLOAD
# =========================================================

st.header("📚 Upload Your Notes")

uploaded_file = st.file_uploader(
    "Choose a PDF file",
    type=["pdf"]
)


# =========================================================
# PROCESS PDF
# =========================================================

notes = ""


if uploaded_file is not None:

    st.success(
        f"✅ Uploaded: {uploaded_file.name}"
    )

    with st.spinner(
        "📖 Reading your PDF..."
    ):

        notes = extract_text_from_pdf(
            uploaded_file
        )


    if notes:

        st.success(
            "✅ Your notes are ready!"
        )

        st.info(
            f"📄 Characters extracted: {len(notes)}"
        )

    else:

        st.error(
            "❌ No text could be extracted from this PDF."
        )

        st.warning(
            "This may be a scanned or image-based PDF."
        )


st.divider()


# =========================================================
# SELECT FEATURE
# =========================================================

st.header("🎯 Choose What You Want To Do")

feature = st.selectbox(

    "Select a feature",

    [
        "📄 Summarize Notes",
        "📝 Generate Quiz",
        "💬 Ask Your Notes"
    ]

)


# =========================================================
# FEATURE 1 - SUMMARIZE NOTES
# =========================================================

if feature == "📄 Summarize Notes":

    st.subheader(
        "📄 Summarize Your Notes"
    )


    summary_type = st.selectbox(

        "Select summary type",

        [
            "Short Summary",
            "Detailed Summary",
            "Exam-Oriented Summary"
        ]

    )


    if not uploaded_file:

        st.warning(
            "⚠️ Please upload a PDF first."
        )


    else:

        if st.button(
            "✨ Generate Summary"
        ):

            if not notes:

                st.error(
                    "No text was found in the PDF."
                )


            else:

                notes_for_ai = notes[:30000]


                with st.spinner(
                    "🤖 AI is creating your summary..."
                ):

                    prompt = f"""
You are an expert AI study assistant.

Analyze the following study notes.

Create a {summary_type}.

IMPORTANT INSTRUCTIONS:

- Explain everything clearly.
- Use simple language.
- Do not skip important concepts.
- Include important definitions.
- Include important formulas.
- Use headings and bullet points.
- Highlight important exam points.
- Make the answer useful for a college student preparing for exams.

Study Notes:

-------------------------

{notes_for_ai}

-------------------------

Now create the summary.
"""


                    result = ask_ai(
                        prompt
                    )


                if result:

                    st.success(
                        "✅ Summary Generated!"
                    )

                    st.markdown(
                        "## 📚 Your Summary"
                    )

                    st.markdown(
                        result
                    )


# =========================================================
# FEATURE 2 - GENERATE QUIZ
# =========================================================

elif feature == "📝 Generate Quiz":

    st.subheader(
        "📝 Generate Quiz From Your Notes"
    )


    number_of_questions = st.slider(

        "Number of Questions",

        min_value=5,

        max_value=20,

        value=10

    )


    difficulty = st.selectbox(

        "Difficulty Level",

        [
            "Easy",
            "Medium",
            "Hard"
        ]

    )


    if not uploaded_file:

        st.warning(
            "⚠️ Please upload a PDF first."
        )


    else:

        if st.button(
            "🧠 Generate Quiz"
        ):

            if not notes:

                st.error(
                    "No text was found in the PDF."
                )


            else:

                notes_for_ai = notes[:30000]


                with st.spinner(
                    "🤖 AI is creating your quiz..."
                ):

                    prompt = f"""
You are an expert college exam question creator.

Create a quiz based ONLY on the study notes below.

Number of questions:
{number_of_questions}

Difficulty:
{difficulty}

For each question:

1. Write the question.
2. Give four options.
3. Give the correct answer.
4. Give a short explanation.

Use this format:

Question 1:
[Question]

A. [Option]
B. [Option]
C. [Option]
D. [Option]

Correct Answer:
[Answer]

Explanation:
[Explanation]

Make sure the questions are important for exams.

Study Notes:

-------------------------

{notes_for_ai}

-------------------------
"""


                    result = ask_ai(
                        prompt
                    )


                if result:

                    st.success(
                        "✅ Quiz Generated!"
                    )

                    st.markdown(
                        "## 📝 Your Quiz"
                    )

                    st.markdown(
                        result
                    )


# =========================================================
# FEATURE 3 - ASK YOUR NOTES
# =========================================================

elif feature == "💬 Ask Your Notes":

    st.subheader(
        "💬 Ask Questions About Your Notes"
    )


    if not uploaded_file:

        st.warning(
            "⚠️ Please upload a PDF first."
        )


    else:

        question = st.text_area(

            "Enter your question",

            placeholder=
            "Example: Explain this topic in simple words.",

            height=100

        )


        if st.button(
            "🔍 Ask AI"
        ):

            if not question.strip():

                st.warning(
                    "⚠️ Please enter a question."
                )


            elif not notes:

                st.error(
                    "No text was found in the PDF."
                )


            else:

                notes_for_ai = notes[:30000]


                with st.spinner(
                    "🤖 AI is reading your notes..."
                ):

                    prompt = f"""
You are a helpful AI study assistant.

Answer the student's question using the uploaded study notes.

Student Question:

{question}

IMPORTANT:

- Give a clear answer.
- Explain in simple language.
- Give examples when useful.
- Use bullet points when appropriate.
- If the answer is not found in the notes, say:
"This information is not available in your uploaded notes."

Study Notes:

-------------------------

{notes_for_ai}

-------------------------

Now answer the student's question.
"""


                    result = ask_ai(
                        prompt
                    )


                if result:

                    st.success(
                        "✅ Answer"
                    )

                    st.markdown(
                        result
                    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🎓 StudyAI | Built with Python, Streamlit and Gemini"
)
