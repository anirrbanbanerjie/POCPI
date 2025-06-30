# streamlit_app.py
import streamlit as st
import pandas as pd
from detector import detect_anomalies
from db import init_db, log_decision
import altair as alt
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
init_db()

st.title("🐾 Pet Claims Analyzer")

# ============================
# Sidebar
# ============================

with st.sidebar:
    st.header("🔐 User Access")
    role = st.sidebar.selectbox(
    "Select Role",
    ["adjuster", "supervisor", "admin"],
    key="role_select"
)

    st.header("📤 Upload Claims File")
    uploaded = st.file_uploader("Upload claims CSV", type="csv")

# ============================
# Load & Process Data
# ============================

if uploaded:
    try:
        df = pd.read_csv(uploaded, parse_dates=['claim_date'], na_values=['null', 'None'])
        df.dropna(subset=['pet_id', 'customer_id', 'provider', 'procedure', 'cost', 'claim_date', 'breed'], inplace=True)
        df = detect_anomalies(df)
        st.session_state.claims_df = df
    except Exception as e:
        st.error(f"Failed to read and process file: {e}")
        st.stop()
else:
    st.warning("Please upload a CSV file to begin.")
    st.stop()

# Role selection
role = st.sidebar.selectbox("Select Role", ["adjuster", "supervisor", "admin"])

# Upload
if role in ["adjuster", "admin"]:
    uploaded = st.sidebar.file_uploader("Upload claims CSV", type="csv")

if 'claims_df' not in st.session_state and uploaded:
    df = pd.read_csv(uploaded, parse_dates=['claim_date'])
    st.session_state.claims_df = detect_anomalies(df)

df = st.session_state.get('claims_df', pd.DataFrame())

# Tabs based on role
tabs = {"adjuster": ["Claims", "Manual Review"], "supervisor": ["Manual Review", "Analytics"], "admin": ["Claims", "Manual Review", "Analytics"]}
selected_tabs = tabs[role]
tab_objs = st.tabs(selected_tabs)

# Tab 1: Claims
if "Claims" in selected_tabs:
    with tab_objs[selected_tabs.index("Claims")]:
        st.subheader("All Processed Claims")
        st.dataframe(df)

# Tab 2: Manual Review
if "Manual Review" in selected_tabs:
    with tab_objs[selected_tabs.index("Manual Review")]:
        st.subheader("🧐 Flagged Claims Review")
        queue = df[df['status'] == 'flagged_for_review']

        if queue.empty:
            st.success("✅ No flagged claims to review.")
        else:
            for i, row in queue.iterrows():
                with st.container():
                    col1, col2 = st.columns([4, 2])

                    with col1:
                        st.markdown(f"""
                            **Pet ID:** {row['pet_id']}  
                            **Customer ID:** {row['customer_id']}  
                            **Breed:** {row['breed']}  
                            **Procedure:** {row['procedure']}  
                            **Cost:** ${row['cost']}  
                            **Provider:** {row['provider']}  
                            **Claim Date:** {row['claim_date'].date()}  
                            **Reason:** {row['flag_reason']}  
                            **ML Flag:** {row['ml_flag']}  
                        """)

                    with col2:
                        decision_key = f"decision_{i}_{row['pet_id']}"
                        decision = st.selectbox(
                            "Decision",
                            ["Keep flagged", "Approve", "Mark as Fraud"],
                            key=decision_key
                        )

                        if st.button("Submit Decision", key=f"submit_{i}_{row['pet_id']}"):
                            if decision == "Approve":
                                df.at[i, 'status'] = 'approved'
                                log_decision(claim_id=row['pet_id'], decision='approved', role=role)
                                st.success("Approved.")
                            elif decision == "Mark as Fraud":
                                df.at[i, 'status'] = 'fraud'
                                log_decision(claim_id=row['pet_id'], decision='fraud', role=role)
                                st.warning("Marked as fraud.")
                            else:
                                st.info("Kept flagged.")

# Tab 3: Analytics
if "Analytics" in selected_tabs:
    with tab_objs[selected_tabs.index("Analytics")]:
        st.subheader("Analytics Dashboard")

        # Volume over time
        df['claim_month'] = df['claim_date'].dt.to_period('M').dt.to_timestamp()
        volume = df.groupby('claim_month').size().reset_index(name='count')
        flagged = df[df['status']=='flagged_for_review'].groupby('claim_month').size().reset_index(name='flagged')
        merged = volume.merge(flagged, on='claim_month', how='left').fillna(0)
        merged['pct_flagged'] = merged['flagged'] / merged['count'] * 100

        c1, c2 = st.columns(2)
        with c1:
            st.altair_chart(alt.Chart(volume).mark_line().encode(x='claim_month', y='count'), use_container_width=True)
        with c2:
            st.altair_chart(alt.Chart(merged).mark_line(color='red').encode(x='claim_month', y='pct_flagged'), use_container_width=True)

        # Heatmap
        st.subheader("Heatmap: Breed vs. Procedure")
        heat = df.groupby(['breed', 'procedure']).size().reset_index(name='count')
        pivot = heat.pivot(index='breed', columns='procedure', values='count').fillna(0)

        fig, ax = plt.subplots(figsize=(12, 10))
        sns.heatmap(pivot, cmap="YlOrBr", linewidths=0.5)
        st.pyplot(fig)
