import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Streamlit App Title
st.title("Project Delivery Method Selection")
st.write("This app helps in selecting the best project delivery method by simulating different scenarios based on user-defined input values.")

# Sidebar for User Inputs
st.sidebar.header("Simulation Parameters")
iterations = st.sidebar.number_input("Number of Simulations", min_value=100, step=100, value=1000)

st.sidebar.header("Weight Assignments (Total 100%)")
time_weight = st.sidebar.number_input("Weight for Time (%)", min_value=0, value=30)
cost_weight = st.sidebar.number_input("Weight for Cost (%)", min_value=0, value=30)
scope_weight = st.sidebar.number_input("Weight for Scope (%)", min_value=0, value=20)
quality_weight = st.sidebar.number_input("Weight for Quality (%)", min_value=0, value=20)

# Normalize Weights
total_weight = time_weight + cost_weight + scope_weight + quality_weight
if total_weight != 100:
    st.sidebar.warning("Weights should sum to 100%. Adjust the values.")

weights = {
    "time": time_weight / 100,
    "cost": cost_weight / 100,
    "scope": scope_weight / 100,
    "quality": quality_weight / 100,
}

# Project Delivery Methods Input
st.header("Project Delivery Method Inputs (Editable Table)")

columns = ["Method", "Time Min (months)", "Time Most Likely (months)", "Time Max (months)", 
           "Cost Min ($M)", "Cost Most Likely ($M)", "Cost Max ($M)", 
           "Scope Min (%)", "Scope Most Likely (%)", "Scope Max (%)", 
           "Quality Min (%)", "Quality Most Likely (%)", "Quality Max (%)"]

data = [
    ["Design-Bid-Build (DBB)", 6, 12, 24, 3.0, 5.0, 7.0, 70, 85, 95, 75, 88, 98],
    ["Design-Build (DB)", 5, 10, 20, 3.5, 4.5, 6.5, 72, 86, 96, 78, 89, 99],
    ["Construction Manager at Risk (CMAR)", 7, 14, 22, 3.2, 4.8, 6.8, 74, 87, 97, 76, 90, 99]
]

df_input = pd.DataFrame(data, columns=columns)

# Editable Data Table
df_input = st.data_editor(df_input)

# Convert table input into dictionary
methods = {}
for index, row in df_input.iterrows():
    methods[row["Method"]] = {
        "time": (row["Time Min (months)"], row["Time Most Likely (months)"], row["Time Max (months)"]),
        "cost": (row["Cost Min ($M)"], row["Cost Most Likely ($M)"], row["Cost Max ($M)"]),
        "scope": (row["Scope Min (%)"], row["Scope Most Likely (%)"], row["Scope Max (%)"]),
        "quality": (row["Quality Min (%)"], row["Quality Most Likely (%)"], row["Quality Max (%)"]),
    }

# Monte Carlo Simulation
st.header("Running Monte Carlo Simulation...")
results = []

for method, params in methods.items():
    scores = []
    for _ in range(iterations):
        time = np.random.triangular(*params["time"])
        cost = np.random.triangular(*params["cost"])
        scope = np.random.triangular(*params["scope"])
        quality = np.random.triangular(*params["quality"])

        # Normalize values
        norm_time = (time - params["time"][0]) / (params["time"][2] - params["time"][0])
        norm_cost = (cost - params["cost"][0]) / (params["cost"][2] - params["cost"][0])
        norm_scope = (scope - params["scope"][0]) / (params["scope"][2] - params["scope"][0])
        norm_quality = (quality - params["quality"][0]) / (params["quality"][2] - params["quality"][0])

        # Compute Weighted Score
        score = (norm_time * weights["time"] +
                 norm_cost * weights["cost"] +
                 norm_scope * weights["scope"] +
                 norm_quality * weights["quality"])
        scores.append(score)

    results.append({"method": method, "scores": scores, "mean_score": np.mean(scores)})

# Convert results into a DataFrame
df_results = pd.DataFrame({
    "Method": [r["method"] for r in results],
    "Mean Score": [r["mean_score"] for r in results]
})

# Display Results
st.subheader("Simulation Results")
st.write(df_results)

# Plot PDFs
st.subheader("Probability Density Functions (PDFs)")
plt.figure(figsize=(10, 6))
for r in results:
    sns.kdeplot(r["scores"], label=f"{r['method']} (Mean: {r['mean_score']:.3f})", shade=True)
plt.title("Probability Density Function (PDF) of Scores")
plt.xlabel("Score")
plt.ylabel("Density")
plt.legend()
st.pyplot(plt)

# Plot CDFs
st.subheader("Cumulative Distribution Functions (CDFs)")
plt.figure(figsize=(10, 6))
for r in results:
    sns.ecdfplot(r["scores"], label=f"{r['method']}")
plt.title("Cumulative Probability (CDF) of Scores")
plt.xlabel("Score")
plt.ylabel("Cumulative Probability")
plt.legend()
st.pyplot(plt)

# Interpretation of Results
st.header("Interpretation of Results")
best_method = df_results.loc[df_results["Mean Score"].idxmax()]["Method"]
st.write(f"Based on the Monte Carlo simulation, the **best project delivery method** is **{best_method}**, as it has the highest mean score.")

st.write("### Key Observations:")
for r in results:
    st.write(f"**{r['method']}**:")
    st.write(f"  - Mean Score: {r['mean_score']:.3f}")
    st.write(f"  - Performance Variability: A narrow PDF indicates consistency, while a wider distribution means higher variability.")

# Recommendations
st.header("Recommendations")
st.write("- If the project **prioritizes time**, select the method with the lowest variability in schedule performance.")
st.write("- If **cost is the primary concern**, choose the method with the most stable cost distribution.")
st.write("- If **scope adherence is critical**, opt for the method with the highest probability of meeting scope expectations.")
st.write("- If **quality is a key factor**, select the method that consistently scores highest in quality.")

st.write("For final decision-making, consider additional factors such as project complexity, risk tolerance, and stakeholder preferences.")