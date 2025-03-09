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

# Function to display user input fields in table format
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

        # Store time and cost for later comparison
        times.append(time)
        costs.append(cost)

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

    results.append({
        "method": method,
        "scores": scores,
        "mean_score": np.mean(scores),
        "std_dev": np.std(scores),
        "mean_time": np.mean(times),
        "mean_cost": np.mean(costs)
    })
    
    scores_dict[method] = scores
    time_results[method] = times
    cost_results[method] = costs

# Convert results into a DataFrame
df_results = pd.DataFrame(results).drop(columns=["scores"])

# Display results in Streamlit
st.subheader("Simulation Results")
st.dataframe(df_results)

# Practical Significance: Best vs Worst Time & Cost
best_method = df_results.loc[df_results["mean_score"].idxmax()]
worst_method = df_results.loc[df_results["mean_score"].idxmin()]

time_saved = worst_method["mean_time"] - best_method["mean_time"]
cost_saved = worst_method["mean_cost"] - best_method["mean_cost"]
time_savings_percentage = (time_saved / worst_method["mean_time"]) * 100
cost_savings_percentage = (cost_saved / worst_method["mean_cost"]) * 100

st.subheader("Practical Significance")
st.write(f"By choosing **{best_method['method']}**, an estimated **{time_saved:.2f} months** ({time_savings_percentage:.1f}%) can be saved in project duration.")
st.write(f"Similarly, **{cost_saved:.2f} million dollars** ({cost_savings_percentage:.1f}%) can be saved in project cost.")

# Recommendations
st.header("Recommendations")
st.write(f"The best project delivery method is **{best_method['method']}**, as it has the highest expected performance.")
if df_results["mean_score"].max() - df_results["mean_score"].min() < 0.05:
    st.write("However, the differences are small, and other factors (such as legal constraints or project complexity) should also be considered.")

