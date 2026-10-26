
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv

from analyzer import extract_pdf_text, analyze_resume

load_dotenv()

st.set_page_config(
    page_title="AI Document Intelligence",
    page_icon="📄",
    layout="wide",
)

st.title("📄 AI-Powered Document Intelligence")
st.write(
    "Upload a resume to extract information, "
    "generate an AI summary, and visualize skills."
)

uploaded_file = st.file_uploader(
    "Upload your resume (PDF)",
    type=["pdf"],
)

analysis_level = st.selectbox(
    "Choose analysis level",
    ["Basic", "Standard", "Detailed"],
)

if uploaded_file is not None:
    st.success(f"Uploaded: {uploaded_file.name}")

    if st.button("Analyze Resume", type="primary"):
        try:
            with st.spinner("Extracting and analyzing resume..."):
                pdf_bytes = uploaded_file.getvalue()
                resume_text = extract_pdf_text(pdf_bytes)

                level_instructions = {
                    "Basic": "Give a concise summary.",
                    "Standard": "Summarize the resume and identify key skills.",
                    "Detailed": (
                        "Provide a detailed summary of skills, education, "
                        "experience, and missing information."
                    ),
                }

                result = analyze_resume(
                    resume_text
                    + "\n\nAnalysis preference: "
                    + level_instructions[analysis_level]
                )

            st.session_state["resume_result"] = result.model_dump()
            st.session_state["resume_filename"] = uploaded_file.name

        except Exception as error:
            st.error(f"Analysis failed: {error}")

if "resume_result" in st.session_state:
    data = st.session_state["resume_result"]

    st.divider()
    st.header("📊 Analysis Results")

    st.subheader("Resume Summary")
    st.write(data["summary"])

    st.subheader("👤 Extracted Information")

    with st.form("edit_resume_form"):
        name = st.text_input("Name", value=data["name"])
        email = st.text_input("Email", value=data["email"])
        phone = st.text_input("Phone", value=data["phone"])

        skills_text = st.text_area(
            "Skills (comma-separated)",
            value=", ".join(data["skills"]),
        )

        submitted = st.form_submit_button("Save corrections")

        if submitted:
            data["name"] = name
            data["email"] = email
            data["phone"] = phone
            data["skills"] = [
                skill.strip()
                for skill in skills_text.split(",")
                if skill.strip()
            ]
            st.session_state["resume_result"] = data
            st.success("Your corrections have been saved.")

    st.subheader("🎓 Education")
    if data["education"]:
        st.dataframe(data["education"], use_container_width=True)
    else:
        st.info("No education details were extracted.")

    st.subheader("💼 Experience")
    if data["experience"]:
        st.dataframe(data["experience"], use_container_width=True)
    else:
        st.info("No experience details were extracted.")

    st.subheader("📈 Skills Visualization")
    skills = data["skills"]

    if skills:
        chart_data = {
            "Skill": skills,
            "Count": [1] * len(skills),
        }

        figure = px.bar(
            chart_data,
            x="Skill",
            y="Count",
            title="Skills Found in Resume",
            text="Skill",
        )
        figure.update_layout(
            showlegend=False,
            yaxis_title="Presence",
            xaxis_title="",
        )
        figure.update_yaxes(visible=False)
        st.plotly_chart(figure, use_container_width=True)
    else:
        st.info("No skills available to visualize.")

    st.subheader("✅ Completeness Check")

    required_fields = ["name", "email", "phone", "summary", "skills"]
    completed = sum(
        bool(data[field])
        and data[field] != "Not provided"
        for field in required_fields
    )
    score = round(completed / len(required_fields) * 100)

    st.progress(score / 100)
    st.metric("Completeness Score", f"{score}%")

    missing = [
        field
        for field in required_fields
        if not data[field] or data[field] == "Not provided"
    ]

    if missing:
        st.warning("Missing or incomplete: " + ", ".join(missing))
    else:
        st.success("All required fields contain information.")

    if data["missing_fields"]:
        st.write("AI-identified missing fields:", data["missing_fields"])

    st.download_button(
        "Download Analysis as JSON",
        data=__import__("json").dumps(data, indent=2),
        file_name="resume_analysis.json",
        mime="application/json",
    )
