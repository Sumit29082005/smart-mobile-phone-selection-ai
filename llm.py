import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate


load_dotenv()


# Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash"
)


# -------------------------------------------------
# Requirement Extraction
# -------------------------------------------------

requirement_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are a smartphone requirement extraction assistant.

Read the user's smartphone requirements and extract:

1. Budget
2. Camera preference
3. Gaming preference
4. Battery preference
5. Performance preference

Return the answer in exactly this format:

Budget: <amount>
Camera: <low/medium/high>
Gaming: <low/medium/high>
Battery: <low/medium/high>
Performance: <low/medium/high>

If something is not mentioned, write:
Not specified.
"""
    ),
    (
        "human",
        "{user_input}"
    )
])


requirement_chain = requirement_prompt | llm


# -------------------------------------------------
# Extract requirements
# -------------------------------------------------

def extract_requirements(user_input):

    response = requirement_chain.invoke({
        "user_input": user_input
    })


    if isinstance(response.content, list):

        for item in response.content:

            if isinstance(item, dict):

                if item.get("type") == "text":

                    return item.get("text", "")

    else:

        return response.content


    return ""


# -------------------------------------------------
# AI Recommendation Explanation
# -------------------------------------------------

explanation_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are an AI smartphone recommendation assistant.

Explain why the recommended smartphones are suitable
for the user's requirements.

Use the user's requirements, phone specifications,
and fuzzy suitability scores provided to you.

Your explanation should:

1. Mention the user's main requirements.
2. Explain why each recommended phone matches.
3. Mention important strengths such as camera,
   gaming, battery, performance and price.
4. Mention the fuzzy suitability score.
5. Clearly explain if a phone is above the user's budget.
6. Do not invent specifications that are not provided.
7. Keep the explanation simple and easy to understand.

Do not say that one phone is universally the best.
Explain the recommendations based on the user's
specific requirements.

Use this format:

AI Recommendation Explanation

User Requirements:
<short summary>

1. <Phone Name>
<2-3 sentences explaining why it matches>

2. <Phone Name>
<2-3 sentences explaining why it matches>

3. <Phone Name>
<2-3 sentences explaining why it matches>

Final Summary:
<short overall explanation>
"""
    ),
    (
        "human",
        """
User requirements:

{requirements}

Recommended phones:

{phones}
"""
    )
])


explanation_chain = explanation_prompt | llm


# -------------------------------------------------
# Generate AI explanation
# -------------------------------------------------

def generate_explanation(requirements, phones):

    response = explanation_chain.invoke({
        "requirements": requirements,
        "phones": phones
    })


    if isinstance(response.content, list):

        text_parts = []

        for item in response.content:

            if isinstance(item, dict):

                if item.get("type") == "text":

                    text_parts.append(
                        item.get("text", "")
                    )

        return "\n".join(text_parts)


    return response.content