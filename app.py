import streamlit as st
import google.generativeai as genai
import json
import os

# ----------------------------
# Configuration
# ----------------------------
st.set_page_config(
    page_title="BiasCheck – SDG 5",
    page_icon="⚖️",  # Optional: keep one subtle icon
    layout="centered"
)

# Header with clear SDG context
st.title("BiasCheck")
st.markdown(
    "<small><em>Supporting UN Sustainable Development Goal 5: Gender Equality</em></small>",
    unsafe_allow_html=True
)
st.write("Analyze job descriptions for gendered language and receive inclusive alternatives.")

# Initialize Gemini
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    st.error("Please configure your GOOGLE_API_KEY in secrets or environment variables.")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# ----------------------------
# Helper Function
# ----------------------------
def analyze_bias(job_desc: str):
    prompt = f"""
You are an AI assistant promoting gender-inclusive hiring practices. Analyze the following job description for language that may unintentionally discourage women, non-binary, or underrepresented candidates. Focus on words with strong masculine or feminine connotations, exclusionary tone, or stereotypical assumptions.

Return your response in this exact JSON format:
{{
  "biased_phrases": [
    {{"phrase": "example", "reason": "brief explanation"}}
  ],
  "rewritten_description": "A revised, inclusive version of the job description using neutral, welcoming language.",
  "tips": ["tip 1", "tip 2"]
}}

If no bias is found, return empty arrays and the original text as rewritten_description.

Job description:
\"\"\"
{job_desc}
\"\"\"
"""
    try:
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        result = json.loads(response.text)
        return result
    except Exception as e:
        st.error(f"Analysis failed: {str(e)}")
        return None

# ----------------------------
# Input Section
# ----------------------------
st.markdown("### Job Description")
job_input = st.text_area(
    label="Enter the job posting you'd like to review:",
    height=180,
    placeholder="Example: We're seeking a rockstar developer who thrives in aggressive, fast-paced environments..."
)

# ----------------------------
# Action Button
# ----------------------------
if st.button("Analyze for Gender Bias"):
    if not job_input.strip():
        st.warning("Please enter a job description to analyze.")
    else:
        with st.spinner("Analyzing language for potential bias..."):
            result = analyze_bias(job_input)

        if result:
            # Biased Phrases
            if result["biased_phrases"]:
                st.markdown("### Potentially Exclusionary Language")
                for item in result["biased_phrases"]:
                    st.markdown(f"- **“{item['phrase']}”** — {item['reason']}")
            else:
                st.success("No gendered language detected. The description appears inclusive.")

            # Rewritten Version
            st.markdown("### Suggested Inclusive Revision")
            st.text_area(
                label="",
                value=result["rewritten_description"],
                height=160,
                disabled=True
            )

            # Tips
            if result.get("tips"):
                st.markdown("### Recommendations for Inclusive Writing")
                for tip in result["tips"]:
                    st.caption(f"• {tip}")

            # Disclaimer (required for responsible AI)
            st.caption(
                "Note: This tool provides general linguistic suggestions based on research on inclusive hiring. "
                "It does not constitute legal or HR advice. Always consult diversity and inclusion professionals for critical decisions."
            )