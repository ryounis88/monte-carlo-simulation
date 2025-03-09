import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Streamlit App Title
st.title("Monte Carlo Simulation for Project Delivery Method Selection")

# Sidebar for User Inputs
st.sidebar.header("Simulation Parameters")
iterations = st.sidebar.number_input("Number of Simulations", min_value=100, step=100, value=10000)

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

# Define Project Delivery Methods
methods = {
    "Design-Bid-Build (DBB)": {
        "time": (6, 12, 24),
        "cost": (3.0, 5.0, 7.0),
        "quality": (75, 88, 98)
    },
    "Design-Build (DB)": {
        "time": (5, 10, 18),
        "cost": (2.5, 4.5, 6.5),
        "quality": (80, 90, 99)
    },
    "Construction Manager at Risk (CMAR)": {
        "time": (7, 14, 22),
        "cost": (3.2, 4.8, 6.8),
        "quality": (78, 89, 98)
    }
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

        # Correct Normalization
        norm_time = 1 - ((time - params["time"][0]) / (params["time"][2] - params["time"][0])) if params["time"][2] > params["time"][0] else 0
        norm_cost = 1 - ((cost - params["cost"][0]) / (params["cost"][2] - params["cost"][0])) if params["cost"][2] > params["cost"][0] else 0
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

# Display results in Streamlit
st.subheader("Simulation Results")
st.dataframe(df_results)

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

# Interpretation of Results
st.header("Interpretation of Results")
best_method = df_results.loc[df_results["Mean Score"].idxmax()]["Method"]
st.write(f"Based on the Monte Carlo simulation, the **best project delivery method** is **{best_method}**, as it has the highest mean score.")

st.write("### Key Observations:")
for r in results:
    st.write(f"**{r['method']}**:")
    st.write(f"  - Mean Score: {r['mean_score']:.3f}")
    st.write(f"  - Standard Deviation: {r['std_dev']:.3f} (Indicates variability in performance)")

# Recommendations
st.header("Recommendations")
for r in results:
    st.write(f"### **{r['method']}**")
    st.write(f"- **Expected Performance**: Mean score of **{r['mean_score']:.3f}**")
    st.write(f"- **Risk Level**: Standard deviation of **{r['std_dev']:.3f}**")
    if r["std_dev"] < 0.1:
        st.write("- **Recommendation**: This method has **consistent** performance and is suitable for predictable projects.")
    elif 0.1 <= r["std_dev"] < 0.2:
        st.write("- **Recommendation**: This method has **moderate** variability and should be used with some risk planning.")
    else:
        st.write("- **Recommendation**: This method has **high** variability and should be chosen if flexibility is acceptable.")

st.write("For final decision-making, consider additional factors such as project complexity, risk tolerance, and stakeholder preferences.")
