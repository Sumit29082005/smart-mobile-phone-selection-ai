import streamlit as st
import pandas as pd

from llm import extract_requirements
from fuzzy_logic import calculate_phone_suitability


# Page title
st.title("📱 Smart Mobile Phone Selection System")

st.write(
    "AI + Fuzzy Logic based mobile phone recommendation system"
)


# User input
user_input = st.text_area(
    "Enter your mobile requirements:",
    placeholder="Example: I have a budget of 30000 rupees. "
                "I want high gaming, good camera and good battery."
)


# Recommendation button
if st.button("🔍 Find Best Phones"):

    if user_input.strip() == "":
        st.warning("Please enter your requirements.")

    else:

        # Step 1: Extract requirements using LLM
        requirements_text = extract_requirements(user_input)

        st.subheader("🤖 AI Extracted Requirements")

        st.text(requirements_text)


        # Step 2: Convert LLM output into dictionary

        requirements = {}

        for line in requirements_text.splitlines():

            if ":" in line:

                key, value = line.split(":", 1)

                requirements[key.strip()] = value.strip()


        # Get budget
        budget_text = requirements.get(
            "Budget",
            "0"
        )

        budget_number = "".join(
            character
            for character in budget_text
            if character.isdigit()
        )

        if budget_number:
            user_budget = float(budget_number)
        else:
            user_budget = 0


        # Get camera preference
        camera_preference = requirements.get(
            "Camera",
            "medium"
        ).lower()


        # Get gaming preference
        gaming_preference = requirements.get(
            "Gaming",
            "medium"
        ).lower()


        # Get battery preference
        battery_preference = requirements.get(
            "Battery",
            "medium"
        ).lower()


        # Get performance preference
        performance_preference = requirements.get(
            "Performance",
            "medium"
        ).lower()


        # Step 3: Load phone dataset

        phones = pd.read_csv("phones.csv")


        results = []


        # Step 4: Calculate fuzzy score for every phone

        for _, phone in phones.iterrows():

            phone_data = {

                "Price": phone["Price"],

                "Camera": phone["Camera"],

                "Gaming": phone["Gaming"],

                "Battery": phone["Battery"],

                "Performance": phone["Performance"]

            }


            score = calculate_phone_suitability(

                phone=phone_data,

                user_budget=user_budget,

                camera_preference=camera_preference,

                gaming_preference=gaming_preference,

                battery_preference=battery_preference,

                performance_preference=performance_preference

            )


            # Store phone information and fuzzy score

            results.append({

                "Phone": phone["Phone"],

                "Price": phone["Price"],

                "Camera": phone["Camera"],

                "Gaming": phone["Gaming"],

                "Battery": phone["Battery"],

                "Performance": phone["Performance"],

                "Suitability": round(score, 2)

            })


        # Step 5: Convert results into DataFrame

        results_df = pd.DataFrame(results)


        # Sort phones according to suitability score

        results_df = results_df.sort_values(

            by="Suitability",

            ascending=False

        )


        # Step 6: Show top 3 recommended phones

        st.subheader("🏆 Recommended Phones")


        top_phones = results_df.head(3)


        for _, phone in top_phones.iterrows():

            st.write(
                "### 📱 " + str(phone["Phone"])
            )

            st.write(
                "💰 Price: ₹" +
                str(int(phone["Price"]))
            )

            st.write(
                "📷 Camera: " +
                str(phone["Camera"])
            )

            st.write(
                "🎮 Gaming: " +
                str(phone["Gaming"])
            )

            st.write(
                "🔋 Battery: " +
                str(phone["Battery"])
            )

            st.write(
                "⚡ Performance: " +
                str(phone["Performance"])
            )

            st.write(
                "⭐ Suitability Score: " +
                str(phone["Suitability"])
            )

            st.divider()


        # Step 7: Show complete phone list

        st.subheader("📋 All Phones")

        st.dataframe(
            results_df,
            use_container_width=True
        )