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

for method, params in methods.items():
    scores = []
    for _ in range(iterations):
        time = np.random.triangular(*params["time"])
        cost = np.random.triangular(*params["cost"])
        quality = np.random.triangular(*params["quality"])

        # Normalize values
        norm_time = (time - params["time"][0]) / (params["time"][2] - params["time"][0])
        norm_cost = (cost - params["cost"][0]) / (params["cost"][2] - params["cost"][0])
        norm_quality = (quality - params["quality"][0]) / (params["quality"][2] - params["quality"][0])

        # Compute Weighted Score
        score = (
            norm_time * weights["time"] +
            norm_cost * weights["cost"] +
            norm_quality * weights["quality"]
        )
        scores.append(score)

    results.append({"method": method, "scores": scores, "mean_score": np.mean(scores), "std_dev": np.std(scores)})

# Convert results into a DataFrame
df_results = pd.DataFrame({
    "Method": [r["method"] for r in results],
    "Mean Score": [r["mean_score"] for r in results],
    "Standard Deviation": [r["std_dev"] for r in results]
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