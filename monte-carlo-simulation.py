import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Streamlit App Title
st.title("Monte Carlo Simulation for Project Delivery Method Selection")

# Sidebar for User Inputs
st.sidebar.header("Simulation Parameters")
iterations = st.sidebar.number_input("Number of Simulations", min_value=100, step=100, value=1000)

st.sidebar.header("Weight Assignments (Total 100%)")
time_weight = st.sidebar.number_input("Weight for Time (%)", min_value=0, value=40)
cost_weight = st.sidebar.number_input("Weight for Cost (%)", min_value=0, value=40)
quality_weight = st.sidebar.number_input("Weight for Quality (%)", min_value=0, value=20)

# Normalize Weights
total_weight = time_weight + cost_weight + quality_weight
if total_weight != 100:
    st.sidebar.warning("Weights should sum to 100%. Adjust the values.")

weights = {
    "time": time_weight / 100,
    "cost": cost_weight / 100,
    "quality": quality_weight / 100,
}

# Function to display user input fields with color-coded headings
def get_user_input(method_name, color):
    st.markdown(f"<h2 style='color:{color};'>{method_name}</h2>", unsafe_allow_html=True)

    time_range = (
        st.number_input(f"{method_name} Time Min (months)", min_value=0.0, value=6.0),
        st.number_input(f"{method_name} Time Most Likely (months)", min_value=0.0, value=12.0),
        st.number_input(f"{method_name} Time Max (months)", min_value=0.0, value=24.0),
    )

    cost_range = (
        st.number_input(f"{method_name} Cost Min ($M)", min_value=0.0, value=3.0),
        st.number_input(f"{method_name} Cost Most Likely ($M)", min_value=0.0, value=5.0),
        st.number_input(f"{method_name} Cost Max ($M)", min_value=0.0, value=7.0),
    )

    quality_range = (
        st.number_input(f"{method_name} Quality Min (%)", min_value=0.0, value=75.0),
        st.number_input(f"{method_name} Quality Most Likely (%)", min_value=0.0, value=88.0),
        st.number_input(f"{method_name} Quality Max (%)", min_value=0.0, value=98.0),
    )

    # Draw a horizontal separator
    st.markdown("<hr>", unsafe_allow_html=True)

    return {"time": time_range, "cost": cost_range, "quality": quality_range}

# Define Project Delivery Methods with Color-Coded Sections
methods = {
    "Design-Bid-Build (DBB)": get_user_input("Design-Bid-Build (DBB)", "blue"),
    "Design-Build (DB)": get_user_input("Design-Build (DB)", "green"),
    "Construction Manager at Risk (CMAR)": get_user_input("Construction Manager at Risk (CMAR)", "red"),
}

# Monte Carlo Simulation
st.header("Running Monte Carlo Simulation...")
results = []
scores_dict = {}

for method, params in methods.items():
    scores = []
    for _ in range(iterations):
        time = np.random.triangular(*params["time"])
        cost = np.random.triangular(*params["cost"])
        quality = np.random.triangular(*params["quality"])

        # Proper Normalization per Method
        norm_time = (time - params["time"][0]) / (params["time"][2] - params["time"][0]) if params["time"][2] > params["time"][0] else 0
        norm_cost = (cost - params["cost"][0]) / (params["cost"][2] - params["cost"][0]) if params["cost"][2] > params["cost"][0] else 0
        norm_quality = (quality - params["quality"][0]) / (params["quality"][2] - params["quality"][0]) if params["quality"][2] > params["quality"][0] else 0

        # Compute Weighted Score
        score = (
            norm_time * weights["time"] +
            norm_cost * weights["cost"] +
            norm_quality * weights["quality"]
        )
        scores.append(score)

    results.append({"method": method, "scores": scores, "mean_score": np.mean(scores), "std_dev": np.std(scores)})
    scores_dict[method] = scores

# Convert results into a DataFrame
df_results = pd.DataFrame({
    "Method": [r["method"] for r in results],
    "Mean Score": [r["mean_score"] for r in results],
    "Standard Deviation": [r["std_dev"] for r in results]
})

# Display Results
st.subheader("Simulation Results")
st.write(df_results)

# Interactive PDF Chart
st.subheader("How Likely Are Different Scores?")
fig_pdf = go.Figure()
for method, scores in scores_dict.items():
    fig_pdf.add_trace(go.Histogram(
        x=scores, histnorm='probability density',
        name=method, opacity=0.7
    ))
fig_pdf.update_layout(title="Probability Density Function (PDF) - Score Distribution",
                      xaxis_title="Score",
                      yaxis_title="Density",
                      barmode='overlay')
st.plotly_chart(fig_pdf)

# Interactive CDF Chart
st.subheader("Chances of Achieving a Certain Score")
fig_cdf = go.Figure()
for method, scores in scores_dict.items():
    sorted_scores = np.sort(scores)
    cumulative_probs = np.arange(1, len(sorted_scores) + 1) / len(sorted_scores)
    fig_cdf.add_trace(go.Scatter(
        x=sorted_scores, y=cumulative_probs, mode='lines',
        name=method
    ))
fig_cdf.update_layout(title="Cumulative Distribution Function (CDF) - Score Probabilities",
                      xaxis_title="Score",
                      yaxis_title="Cumulative Probability")
st.plotly_chart(fig_cdf)