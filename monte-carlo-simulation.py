import numpy as np
import pandas as pd
import plotly.graph_objects as go
import ace_tools as tools

# Define the number of Monte Carlo simulations
iterations = 10000

# Define weight assignments
weights = {
    "time": 0.4,  # 40%
    "cost": 0.4,  # 40%
    "quality": 0.2  # 20%
}

# Define assumed input parameters for different project delivery methods
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
results = []
scores_dict = {}

for method, params in methods.items():
    scores = []
    for _ in range(iterations):
        time = np.random.triangular(*params["time"])
        cost = np.random.triangular(*params["cost"])
        quality = np.random.triangular(*params["quality"])

        # Proper Normalization with Correct Scoring
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

# Generate Recommendations Based on Results
recommendations = []
for r in results:
    method = r["method"]
    mean_score = r["mean_score"]
    std_dev = r["std_dev"]

    recommendation = f"**{method}**:\n"
    recommendation += f"- **Expected Performance**: Mean score of **{mean_score:.3f}**\n"
    recommendation += f"- **Risk Level**: Standard deviation of **{std_dev:.3f}**\n"

    if std_dev < 0.1:
        recommendation += "- **Recommendation**: This method has **consistent** performance and is suitable for predictable projects.\n"
    elif 0.1 <= std_dev < 0.2:
        recommendation += "- **Recommendation**: This method has **moderate** variability and should be used with some risk planning.\n"
    else:
        recommendation += "- **Recommendation**: This method has **high** variability and should be chosen if flexibility is acceptable.\n"

    recommendations.append(recommendation)

# Display Recommendations
recommendations_text = "\n\n".join(recommendations)

# Display results in a table
tools.display_dataframe_to_user(name="Monte Carlo Simulation Results", dataframe=df_results)

# Interactive PDF Chart
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

# Show PDF Chart
fig_pdf.show()

# Interactive CDF Chart
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

# Show CDF Chart
fig_cdf.show()

# Display Interpretations and Insights
interpretation_text = f"""
### **📌 Interpretation of Charts & Insights**

#### **📊 Probability Density Function (PDF) - "How Likely Are Different Scores?"**
- **What it Represents**: The PDF shows the **likelihood of different scores occurring** for each project delivery method.
- **How to Read It**: A **higher peak** means that particular score happens more often.

#### **📈 Cumulative Distribution Function (CDF) - "Chances of Achieving a Certain Score"**
- **What it Represents**: The CDF shows the **probability of scoring at or below a certain value**.
- **How to Read It**: A **steeper curve** means scores are tightly grouped (more predictable). A **gradual curve** means scores are more spread out (higher uncertainty).

--- 

### **📊 Key Recommendations Based on Monte Carlo Results**
{recommendations_text}
"""

# Display interpretation
print(interpretation_text)
