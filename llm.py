import json
import re
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI


# ============================================================
# Gemini API Key
# ============================================================

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    API_KEY = None


# ============================================================
# Gemini Model
# ============================================================

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is missing. "
        "Please add GEMINI_API_KEY in Streamlit Secrets."
    )


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=API_KEY,
    temperature=0
)


# ============================================================
# Extract smartphone requirements
# ============================================================

def extract_requirements(user_input):
    """
    Convert user's natural language phone requirements
    into structured JSON data.
    """

    prompt = f"""
You are a smartphone recommendation assistant.

The user will describe the smartphone they want.

Extract the important requirements from the user's message.

Return ONLY valid JSON.
Do not add markdown.
Do not add ```.

Use exactly these fields:

{{
    "budget": null,
    "gaming": 0,
    "camera": 0,
    "battery": 0,
    "performance": 0,
    "display": 0,
    "storage": 0,
    "ram": 0,
    "brand": "",
    "os": ""
}}

Rules:

1. budget:
   - Extract the maximum budget in Indian Rupees.
   - Example: "under 30000" -> 30000
   - Example: "budget is 25k" -> 25000
   - If budget is not mentioned -> null

2. gaming:
   - 1 if user wants gaming/gaming performance
   - otherwise 0

3. camera:
   - 1 if user wants a good camera/camera quality
   - otherwise 0

4. battery:
   - 1 if user wants good battery/battery life
   - otherwise 0

5. performance:
   - 1 if user wants fast performance/processor/performance
   - otherwise 0

6. display:
   - 1 if user specifically wants a good display, AMOLED, high refresh rate, etc.
   - otherwise 0

7. storage:
   - 1 if user wants more storage/ROM
   - otherwise 0

8. ram:
   - 1 if user specifically wants more RAM
   - otherwise 0

9. brand:
   - Extract a mentioned brand.
   - Example: Samsung, Apple, OnePlus
   - If not mentioned -> ""

10. os:
   - Extract Android or iOS if mentioned.
   - If not mentioned -> ""

User message:

{user_input}
"""

    try:

        response = llm.invoke(prompt)

        result = response.content

        # ----------------------------------------------------
        # Sometimes Gemini returns ```json ... ```
        # Remove markdown if present
        # ----------------------------------------------------

        result = result.strip()

        result = re.sub(
            r"^```json\s*",
            "",
            result,
            flags=re.IGNORECASE
        )

        result = re.sub(
            r"^```\s*",
            "",
            result
        )

        result = re.sub(
            r"\s*```$",
            "",
            result
        )

        result = result.strip()

        # ----------------------------------------------------
        # Convert JSON text into Python dictionary
        # ----------------------------------------------------

        data = json.loads(result)

        # ----------------------------------------------------
        # Make sure all expected fields exist
        # ----------------------------------------------------

        requirements = {
            "budget": data.get("budget"),
            "gaming": data.get("gaming", 0),
            "camera": data.get("camera", 0),
            "battery": data.get("battery", 0),
            "performance": data.get("performance", 0),
            "display": data.get("display", 0),
            "storage": data.get("storage", 0),
            "ram": data.get("ram", 0),
            "brand": data.get("brand", ""),
            "os": data.get("os", "")
        }

        return requirements

    except json.JSONDecodeError:

        # If Gemini returns something that isn't perfect JSON,
        # return safe default values.

        return {
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

    except Exception as e:

        # Show error in Streamlit without exposing API key
        st.error(f"Gemini error: {str(e)}")

        return {
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
# Local testing
# ============================================================

if __name__ == "__main__":

    test_input = (
        "I have a budget of 30000 rupees. "
        "I want a phone mainly for gaming and camera "
        "with good battery."
    )

    print("Testing Gemini...")

    result = extract_requirements(test_input)

    print("\nExtracted requirements:")
    print(json.dumps(result, indent=4))