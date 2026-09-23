import json
import re
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI


# ============================================================
# GEMINI API KEY
# ============================================================

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    API_KEY = None


# ============================================================
# GEMINI MODEL
# ============================================================

if API_KEY:

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        api_key=API_KEY,
        temperature=0
    )

else:
    llm = None


# ============================================================
# DEFAULT REQUIREMENTS
# ============================================================

DEFAULT_REQUIREMENTS = {
    "budget": None,
    "gaming": 0,
    "camera": 0,
    "battery": 0,
    "performance": 0,
    "display": 0,
    "storage": 0,
    "ram": 0,
    "brand": "",
    "os": ""
}


# ============================================================
# EXTRACT REQUIREMENTS
# ============================================================

def extract_requirements(user_input):

    if not user_input or not user_input.strip():
        return DEFAULT_REQUIREMENTS.copy()

    if llm is None:
        st.error("Gemini API key is missing. Please add GEMINI_API_KEY in Streamlit Secrets.")
        return DEFAULT_REQUIREMENTS.copy()

    prompt = f"""
You are a smartphone requirement extraction AI.

Read the user's smartphone requirement and convert it into JSON.

User requirement:
{user_input}

Return ONLY valid JSON.

Use exactly these fields:

{{
    "budget": number or null,
    "gaming": number from 0 to 10,
    "camera": number from 0 to 10,
    "battery": number from 0 to 10,
    "performance": number from 0 to 10,
    "display": number from 0 to 10,
    "storage": number from 0 to 10,
    "ram": number from 0 to 10,
    "brand": string,
    "os": string
}}

Rules:

1. If budget is mentioned, extract the maximum budget as a number.
2. If gaming is important, give gaming a value between 1 and 10.
3. If camera is important, give camera a value between 1 and 10.
4. If battery is important, give battery a value between 1 and 10.
5. If performance is important, give performance a value between 1 and 10.
6. If display is important, give display a value between 1 and 10.
7. If storage is mentioned, extract the storage requirement.
8. If RAM is mentioned, extract the RAM requirement.
9. If brand is mentioned, extract it.
10. If Android or iOS is mentioned, extract it.
11. If something is not mentioned, use 0 for numerical preference fields.
12. If budget is not mentioned, use null.
13. Do not write explanations.
14. Return JSON only.

Example:

{{
    "budget": 30000,
    "gaming": 9,
    "camera": 8,
    "battery": 8,
    "performance": 9,
    "display": 7,
    "storage": 8,
    "ram": 8,
    "brand": "",
    "os": "Android"
}}
"""

    try:

        response = llm.invoke(prompt)

        # Get text from Gemini response
        result = response.content

        if isinstance(result, list):
            result = " ".join(
                item.get("text", "")
                if isinstance(item, dict)
                else str(item)
                for item in result
            )

        result = str(result).strip()

        # Remove markdown JSON fences if Gemini returns them
        result = re.sub(r"```json", "", result, flags=re.IGNORECASE)
        result = re.sub(r"```", "", result)
        result = result.strip()

        # Find JSON object
        match = re.search(r"\{.*\}", result, re.DOTALL)

        if match:
            result = match.group(0)

        requirements = json.loads(result)

        # Make sure all expected keys exist
        final_requirements = DEFAULT_REQUIREMENTS.copy()

        for key in final_requirements:

            if key in requirements:
                final_requirements[key] = requirements[key]

        return final_requirements

    except Exception as e:

        st.error(f"Gemini error: {e}")

        return DEFAULT_REQUIREMENTS.copy()