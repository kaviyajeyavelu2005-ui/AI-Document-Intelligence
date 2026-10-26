
import os
import pymupdf

from google import genai
from pydantic import ValidationError

from schemas import ResumeAnalysis


def extract_pdf_text(pdf_bytes: bytes) -> str:
    """Extract readable text from a PDF resume."""
    text_parts = []

    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as document:
        if document.page_count == 0:
            raise ValueError("The PDF is empty.")

        for page in document:
            text_parts.append(page.get_text())

    extracted_text = "\n".join(text_parts).strip()

    if not extracted_text:
        raise ValueError(
            "No text found in the PDF. "
            "This may be a scanned resume that needs OCR."
        )

    return extracted_text


def analyze_resume(resume_text: str) -> ResumeAnalysis:
    """Analyze resume text using Gemini and validate the result."""
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is missing. "
            "Add it to your .env file."
        )

    if not resume_text.strip():
        raise ValueError("Resume text cannot be empty.")

    client = genai.Client(api_key=api_key)

    prompt = f"""
Analyze the resume provided below.

Rules:
- Use only information explicitly supported by the resume.
- Never invent personal details, skills, education, or experience.
- Use "Not provided" for missing single-value fields.
- Use empty lists when no list items are found.
- List missing required fields in missing_fields.
- Set completeness_score to 0; the application will calculate it.
- Return data that follows the supplied JSON schema.

Resume text:
<resume>
{resume_text[:30000]}
</resume>
"""

    response = client.models.generate_content(
        model="gemini-3.7-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_json_schema": ResumeAnalysis.model_json_schema(),
        },
    )

    if not response.text:
        raise ValueError("The AI returned an empty response.")

    try:
        result = ResumeAnalysis.model_validate_json(response.text)
    except ValidationError as exc:
        raise ValueError(
            f"The AI response did not pass schema validation: {exc}"
        ) from exc

    return result
