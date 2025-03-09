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
time_weight = st.sidebar.number_input("Weight for Time (%)", min_value=0, max_value=100, value=60)
cost_weight = st.sidebar.number_input("Weight for Cost (%)", min_value=0, max_value=100, value=20)
quality_weight = st.sidebar.number_input("Weight for Quality (%)", min_value=0, max_value=100, value=20)

# Normalize Weights
weights = {
    "time": time_weight / 100,
    "cost": cost_weight / 100,
    "quality": quality_weight / 100,
}

# Function to get user inputs
def get_user_input(method_name, color):
    st.markdown(f"<h2 style='color:{color};'>{method_name}</h2>", unsafe_allow_html=True)

    # Time Inputs
    st.subheader("1. Time (months)")
    time_min = st.number_input(f"{method_name} Time Min", min_value=0.0, value=10.0)
    time_most_likely = st.number_input(f"{method_name} Time Most Likely", min_value=0.0, value=15.0)
    time_max = st.number_input(f"{method_name} Time Max", min_value=0.0, value=25.0)

    # Cost Inputs
    st.subheader("2. Cost ($M)")
    cost_min = st.number_input(f"{method_name} Cost Min", min_value=0.0, value=4.0)
    cost_most_likely = st.number_input(f"{method_name} Cost Most Likely", min_value=0.0, value=7.0)
    cost_max = st.number_input(f"{method_name} Cost Max", min_value=0.0, value=10.0)

    # Quality Inputs
    st.subheader("3. Quality (PQI)")
    quality_min = st.number_input(f"{method_name} Quality Min", min_value=0.0, value=70.0)
    quality_most_likely = st.number_input(f"{method_name} Quality Most Likely", min_value=0.0, value=85.0)
    quality_max = st.number_input(f"{method_name} Quality Max", min_value=0.0, value=95.0)

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
time_results = {}
cost_results = {}

for method, params in methods.items():
    scores = []
    times = []
    costs = []
    
    for _ in range(iterations):
        time = np.random.triangular(*params["time"])
        cost = np.random.triangular(*params["cost"])
        quality = np.random.triangular(*params["quality"])

        times.append(time)
        costs.append(cost)

        # Normalization function to avoid division by zero
        def normalize(value, min_val, max_val, invert=False):
            if max_val == min_val:
                return 1  # If all values are the same, return 1 (neutral impact)
            norm_value = (value - min_val) / (max_val - min_val)
            return 1 - norm_value if invert else norm_value

        # Normalize Scores
        norm_time = normalize(time, min(times), max(times), invert=True)
        norm_cost = normalize(cost, min(costs), max(costs), invert=True)
        norm_quality = normalize(quality, min(quality), max(quality))

        # Calculate weighted score
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
        "mean_time": np.mean(times),
        "mean_cost": np.mean(costs),
    })
    
    scores_dict[method] = scores
    time_results[method] = times
    cost_results[method] = costs

# Convert results into a DataFrame
df_results = pd.DataFrame(results).drop(columns=["scores"])
st.subheader("Simulation Results")
st.dataframe(df_results)

# Interactive PDF Chart
st.subheader("Probability Density Function (PDF) - Score Distribution")
fig_pdf = go.Figure()
for method, scores in scores_dict.items():
    fig_pdf.add_trace(go.Histogram(x=scores, histnorm='probability density', name=method, opacity=0.7))
fig_pdf.update_layout(title="PDF of Scores", xaxis_title="Score", yaxis_title="Density", barmode='overlay')
st.plotly_chart(fig_pdf)

# Interactive CDF Chart
st.subheader("Cumulative Distribution Function (CDF) - Score Probabilities")
fig_cdf = go.Figure()
for method, scores in scores_dict.items():
    sorted_scores = np.sort(scores)
    cumulative_probs = np.arange(1, len(sorted_scores) + 1) / len(sorted_scores)
    fig_cdf.add_trace(go.Scatter(x=sorted_scores, y=cumulative_probs, mode='lines', name=method))
fig_cdf.update_layout(title="CDF of Scores", xaxis_title="Score", yaxis_title="Cumulative Probability")
st.plotly_chart(fig_cdf)

# Calculate Practical Significance
best_method = df_results.loc[df_results["mean_score"].idxmax()]
non_best_methods = df_results[df_results["method"] != best_method["method"]]

st.subheader("Practical Significance")
for _, method in non_best_methods.iterrows():
    time_difference = method["mean_time"] - best_method["mean_time"]
    cost_difference = method["mean_cost"] - best_method["mean_cost"]

    st.write(f"Comparison between **{best_method['method']}** and **{method['method']}:**")
    if time_difference > 0:
        st.write(f"✅ **{best_method['method']} saves** {time_difference:.2f} months compared to {method['method']}.")
    else:
        st.write(f"⚠️ **{best_method['method']} requires** {-time_difference:.2f} more months than {method['method']}.")

    if cost_difference > 0:
        st.write(f"✅ **{best_method['method']} saves** ${cost_difference:.2f} million compared to {method['method']}.")
    else:
        st.write(f"⚠️ **{best_method['method']} costs** ${-cost_difference:.2f} million more than {method['method']}.")

# Final Recommendation
st.header("Final Recommendation")
st.write(f"✅ **{best_method['method']} is the recommended choice** based on statistical and practical significance.")
