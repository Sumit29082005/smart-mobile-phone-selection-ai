import streamlit as st
import pandas as pd

from llm import extract_requirements


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Smart Mobile Phone Selection AI",
    page_icon="📱",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: bold;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        margin-bottom: 30px;
    }

    .result-card {
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #ddd;
        margin-bottom: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TITLE
# ============================================================

st.markdown(
    '<div class="main-title">📱 Smart Mobile Phone Selection AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Find a suitable smartphone based on your requirements</div>',
    unsafe_allow_html=True
)


# ============================================================
# LOAD CSV
# ============================================================

@st.cache_data
def load_phones():

    try:

        df = pd.read_csv("phones.csv")

        return df

    except FileNotFoundError:

        st.error("phones.csv file not found.")

        return pd.DataFrame()


phones_df = load_phones()


# ============================================================
# CHECK CSV
# ============================================================

if phones_df.empty:

    st.warning("No phone data available.")

    st.stop()


# ============================================================
# SHOW DATASET INFO
# ============================================================

with st.expander("📊 Phone Dataset"):

    st.write(
        f"Total phones available: **{len(phones_df)}**"
    )

    st.dataframe(
        phones_df,
        use_container_width=True
    )


# ============================================================
# USER INPUT
# ============================================================

st.subheader("🔍 Tell us what phone you need")

requirements_text = st.text_area(
    "Enter your requirements",
    placeholder=(
        "Example:\n"
        "I need a phone under ₹30,000 with good gaming, "
        "camera, battery and performance. I want 8GB RAM and 256GB storage."
    ),
    height=150
)


# ============================================================
# FIND MOBILES BUTTON
# ============================================================

find_button = st.button(
    "🔎 Find Mobiles",
    type="primary",
    use_container_width=True
)


# ============================================================
# PROCESS
# ============================================================

if find_button:

    # --------------------------------------------------------
    # CHECK INPUT
    # --------------------------------------------------------

    if not requirements_text or not requirements_text.strip():

        st.warning("Please enter your mobile requirements first.")

        st.stop()


    # --------------------------------------------------------
    # AI REQUIREMENTS
    # --------------------------------------------------------

    with st.spinner("🤖 AI is understanding your requirements..."):

        requirements = extract_requirements(
            requirements_text
        )


    # --------------------------------------------------------
    # DISPLAY AI REQUIREMENTS
    # --------------------------------------------------------

    st.subheader("🤖 AI Extracted Requirements")

    st.json(requirements)


    # --------------------------------------------------------
    # CREATE COPY OF DATA
    # --------------------------------------------------------

    results_df = phones_df.copy()


    # ========================================================
    # BUDGET FILTER
    # ========================================================

    budget = requirements.get("budget")

    if budget is not None:

        # Try to identify price column
        price_column = None

        possible_price_columns = [
            "price",
            "Price",
            "PRICE",
            "Price (₹)",
            "price_inr",
            "Price_INR"
        ]

        for col in possible_price_columns:

            if col in results_df.columns:

                price_column = col
                break

        if price_column:

            results_df[price_column] = pd.to_numeric(
                results_df[price_column],
                errors="coerce"
            )

            results_df = results_df[
                results_df[price_column] <= float(budget)
            ]


    # ========================================================
    # BRAND FILTER
    # ========================================================

    brand = requirements.get("brand", "")

    if brand:

        brand_column = None

        possible_brand_columns = [
            "brand",
            "Brand",
            "BRAND",
            "manufacturer",
            "Manufacturer"
        ]

        for col in possible_brand_columns:

            if col in results_df.columns:

                brand_column = col
                break

        if brand_column:

            results_df = results_df[
                results_df[brand_column]
                .astype(str)
                .str.contains(
                    str(brand),
                    case=False,
                    na=False
                )
            ]


    # ========================================================
    # RAM FILTER
    # ========================================================

    required_ram = requirements.get("ram", 0)

    if required_ram and required_ram > 0:

        ram_column = None

        possible_ram_columns = [
            "ram",
            "RAM",
            "Ram",
            "ram_gb",
            "RAM_GB"
        ]

        for col in possible_ram_columns:

            if col in results_df.columns:

                ram_column = col
                break

        if ram_column:

            ram_values = (
                results_df[ram_column]
                .astype(str)
                .str.extract(r"(\d+)", expand=False)
            )

            ram_values = pd.to_numeric(
                ram_values,
                errors="coerce"
            )

            results_df = results_df[
                ram_values >= float(required_ram)
            ]


    # ========================================================
    # STORAGE FILTER
    # ========================================================

    required_storage = requirements.get(
        "storage",
        0
    )

    if required_storage and required_storage > 0:

        storage_column = None

        possible_storage_columns = [
            "storage",
            "Storage",
            "ROM",
            "rom",
            "storage_gb",
            "Storage_GB"
        ]

        for col in possible_storage_columns:

            if col in results_df.columns:

                storage_column = col
                break

        if storage_column:

            storage_values = (
                results_df[storage_column]
                .astype(str)
                .str.extract(r"(\d+)", expand=False)
            )

            storage_values = pd.to_numeric(
                storage_values,
                errors="coerce"
            )

            # Only apply this when value looks like actual GB
            if storage_values.notna().any():

                # User's numeric storage preference is usually
                # not directly comparable here, so we don't
                # aggressively remove phones.
                pass


    # ========================================================
    # RESULT CHECK
    # ========================================================

    if results_df.empty:

        st.warning(
            "😕 No phones found matching the basic requirements."
        )

        st.info(
            "Try increasing your budget or removing some restrictions."
        )

        st.stop()


    # ========================================================
    # FUZZY LOGIC
    # ========================================================

    try:

        from fuzzy_logic import calculate_phone_suitability

        try:

            fuzzy_result = calculate_phone_suitability(
                results_df,
                requirements
            )

        except TypeError:

            fuzzy_result = calculate_phone_suitability(
                requirements,
                results_df
            )


        # ----------------------------------------------------
        # Convert result to DataFrame
        # ----------------------------------------------------

        if isinstance(fuzzy_result, pd.DataFrame):

            results_df = fuzzy_result.copy()

        elif isinstance(fuzzy_result, list):

            results_df = pd.DataFrame(
                fuzzy_result
            )

        elif isinstance(fuzzy_result, dict):

            results_df = pd.DataFrame(
                [fuzzy_result]
            )


    except Exception as e:

        st.warning(
            "Fuzzy logic could not be applied. Showing matching phones instead."
        )

        # Do not crash application


    # ========================================================
    # FIND SCORE COLUMN
    # ========================================================

    score_column = None

    possible_score_columns = [
        "suitability_score",
        "Suitability Score",
        "Suitability",
        "score",
        "Score",
        "match_score",
        "Match Score",
        "matching_score",
        "Matching Score"
    ]

    for col in possible_score_columns:

        if col in results_df.columns:

            score_column = col

            break


    # ========================================================
    # SORT RESULTS
    # ========================================================

    if score_column:

        results_df[score_column] = pd.to_numeric(
            results_df[score_column],
            errors="coerce"
        )

        results_df = results_df.sort_values(
            by=score_column,
            ascending=False
        )


    # ========================================================
    # PHONE NAME COLUMN
    # ========================================================

    phone_column = None

    possible_phone_columns = [
        "name",
        "Name",
        "phone",
        "Phone",
        "phone_name",
        "Phone Name",
        "model",
        "Model",
        "mobile",
        "Mobile"
    ]

    for col in possible_phone_columns:

        if col in results_df.columns:

            phone_column = col

            break


    # ========================================================
    # TOP RESULTS
    # ========================================================

    st.subheader("🏆 Recommended Mobiles")


    top_results = results_df.head(5)


    # ========================================================
    # DISPLAY CARDS
    # ========================================================

    for index, row in top_results.iterrows():

        phone_name = (
            str(row[phone_column])
            if phone_column
            else f"Mobile {index + 1}"
        )

        score_text = ""

        if score_column:

            score_text = (
                f"Suitability Score: "
                f"{row[score_column]:.2f}"
            )

        st.markdown(
            f"""
            <div class="result-card">

            <h3>📱 {phone_name}</h3>

            <p>{score_text}</p>

            </div>
            """,
            unsafe_allow_html=True
        )


    # ========================================================
    # COMPLETE RESULTS
    # ========================================================

    st.subheader("📋 All Matching Mobiles")

    st.dataframe(
        results_df,
        use_container_width=True
    )


    # ========================================================
    # DOWNLOAD
    # ========================================================

    csv_data = results_df.to_csv(
        index=False
    )

    st.download_button(
        label="⬇️ Download Results",
        data=csv_data,
        file_name="recommended_mobiles.csv",
        mime="text/csv",
        use_container_width=True
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "🤖 Smart Mobile Phone Selection AI | "
    "AI + Fuzzy Logic"
)