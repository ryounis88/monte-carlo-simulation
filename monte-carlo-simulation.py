import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy.stats import ttest_ind

# Streamlit App Title
st.title("Monte Carlo Simulation for Project Delivery Method Selection")

# Sidebar for User Inputs
st.sidebar.header("Simulation Parameters")
iterations = st.sidebar.number_input("Number of Simulations", min_value=100, step=100, value=10000)

st.sidebar.header("Weight Assignments (Total 100%)")
time_weight = st.sidebar.number_input("Weight for Time (%)", min_value=0, max_value=100, value=40)
cost_weight = st.sidebar.number_input("Weight for Cost (%)", min_value=0, max_value=100, value=40)
quality_weight = st.sidebar.number_input("Weight for Quality (%)", min_value=0, max_value=100, value=20)

# Normalize Weights
total_weight = time_weight + cost_weight + quality_weight
if total_weight != 100:
    st.sidebar.warning("Weights should sum to 100%. Adjust the values.")

weights = {
    "time": time_weight / 100,
    "cost": cost_weight / 100,
    "quality": quality_weight / 100,
}

# Function to display user input fields
def get_user_input(method_name, color):
    st.markdown(f"<h2 style='color:{color};'>{method_name}</h2>", unsafe_allow_html=True)

    time_min = st.number_input(f"{method_name} Time Min (months)", min_value=0.0, value=10.0)
    time_most_likely = st.number_input(f"{method_name} Time Most Likely (months)", min_value=0.0, value=15.0)
    time_max = st.number_input(f"{method_name} Time Max (months)", min_value=0.0, value=25.0)

    cost_min = st.number_input(f"{method_name} Cost Min ($M)", min_value=0.0, value=4.0)
    cost_most_likely = st.number_input(f"{method_name} Cost Most Likely ($M)", min_value=0.0, value=7.0)
    cost_max = st.number_input(f"{method_name} Cost Max ($M)", min_value=0.0, value=10.0)

    quality_min = st.number_input(f"{method_name} Quality Min (%)", min_value=0.0, value=70.0)
    quality_most_likely = st.number_input(f"{method_name} Quality Most Likely (%)", min_value=0.0, value=85.0)
    quality_max = st.number_input(f"{method_name} Quality Max (%)", min_value=0.0, value=95.0)

    st.markdown("<hr>", unsafe_allow_html=True)  # Horizontal separator

    return {
        "time": (time_min, time_most_likely, time_max),
        "cost": (cost_min, cost_most_likely, cost_max),
        "quality": (quality_min, quality_most_likely, quality_max)
    }

# Define Project Delivery Methods
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

        # Normalize scores (Lower Time/Cost = Higher Score, Higher Quality = Higher Score)
        norm_time = 1 - ((time - params["time"][0]) / (params["time"][2] - params["time"][0]))
        norm_cost = 1 - ((cost - params["cost"][0]) / (params["cost"][2] - params["cost"][0]))
        norm_quality = (quality - params["quality"][0]) / (params["quality"][2] - params["quality"][0])

        # Compute Weighted Score
        score = (
            norm_time * weights["time"] +
            norm_cost * weights["cost"] +
            norm_quality * weights["quality"]
        )
        scores.append(score)

    results.append({
        "method": method,
        "scores": scores,
        "mean_score": np.mean(scores),
        "std_dev": np.std(scores),
    })
    
    scores_dict[method] = scores

# Convert results into a DataFrame
df_results = pd.DataFrame(results).drop(columns=["scores"])

# Display results in Streamlit
st.subheader("Simulation Results")
st.dataframe(df_results)

# Pairwise t-tests for statistical significance
st.subheader("Statistical Significance (p-values from t-tests)")
p_values = pd.DataFrame(index=methods.keys(), columns=methods.keys())

for method1 in methods.keys():
    for method2 in methods.keys():
        if method1 != method2:
            t_stat, p_value = ttest_ind(scores_dict[method1], scores_dict[method2])
            p_values.loc[method1, method2] = round(p_value, 4)
        else:
            p_values.loc[method1, method2] = "-"

st.dataframe(p_values)

# Interactive PDF Chart
st.subheader("How Likely Are Different Scores? (PDF)")
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
st.subheader("Chances of Achieving a Certain Score (CDF)")
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

# Final Recommendation
st.header("Final Recommendation")
best_method = df_results.loc[df_results["mean_score"].idxmax()]
if df_results["mean_score"].max() - df_results["mean_score"].min() < 0.05:
    st.write("Differences between methods are small. Consider other factors like risk and complexity.")
else:
    st.write(f"**{best_method['method']}** is statistically and practically the best choice.")

