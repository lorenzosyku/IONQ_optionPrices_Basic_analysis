import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

# Read JSON data from file
with open('options.json', 'r') as file:
    data = json.load(file)



# Extract calls and puts data
calls = data['options']['calls']
puts = data['options']['puts']

# Convert data to DataFrame
def create_df(options, option_type):
    return pd.DataFrame(
        [
            {
                "Strike": opt["strike"],
                "Bid Price": opt["bid"]["price"],
                "Ask Price": opt["ask"]["price"],
                "Bid-Ask Spread": opt["ask"]["price"] - opt["bid"]["price"],
                "Total Orders": opt["bid"]["orders"] + opt["ask"]["orders"],
                "Type": option_type
            }
            for opt in options
        ]
    )

calls_df = create_df(calls, "Call")
puts_df = create_df(puts, "Put")
options_df = pd.concat([calls_df, puts_df])

# Black-Scholes Model for Implied Volatility & Greeks
def black_scholes(S, K, T, r, sigma, option_type="call"):
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if option_type == "call":
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        delta = norm.cdf(d1)
    else:
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        delta = -norm.cdf(-d1)
    
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    vega = S * norm.pdf(d1) * np.sqrt(T)
    theta = - (S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
    rho = K * T * np.exp(-r * T) * norm.cdf(d2) if option_type == "call" else -K * T * np.exp(-r * T) * norm.cdf(-d2)
    
    return price, delta, gamma, vega, theta, rho

# Assumptions
S = 25  # Underlying stock price (example)
r = 0.05  # Risk-free rate (5%)
T = (pd.to_datetime("2027-01-15") - pd.Timestamp.today()).days / 365.0  # Time to expiry in years
sigma = 0.5  # Assumed volatility (50%)

# Compute Greeks for each option
options_df[["Price", "Delta", "Gamma", "Vega", "Theta", "Rho"]] = options_df.apply(
    lambda row: black_scholes(S, row["Strike"], T, r, sigma, row["Type"].lower()), axis=1, result_type="expand")

# Probability Analysis: Probability of Expiring In-The-Money (ITM)
options_df["Prob_ITM"] = options_df.apply(
    lambda row: norm.cdf((np.log(S / row["Strike"]) + (r - 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))), axis=1)

# Arbitrage Analysis: Put-Call Parity Violation Detection
def check_arbitrage(row):
    call_price = row["Price"] if row["Type"] == "Call" else np.nan
    put_price = row["Price"] if row["Type"] == "Put" else np.nan
    return abs(call_price - put_price - (S - row["Strike"] * np.exp(-r * T)))

options_df["Arbitrage_Opp"] = options_df.apply(check_arbitrage, axis=1)
options_df["Arbitrage_Opp_Flag"] = options_df["Arbitrage_Opp"] > 0.1  # Flag significant mispricing

# Visualization - Strike Price Distribution
# plt.figure(figsize=(10, 5))
# options_df["Strike"].hist(bins=20, color="orange", edgecolor="black")
# plt.xlabel("Strike Price")
# plt.ylabel("Frequency")
# plt.title("Distribution of Strike Prices")
# plt.show()

# Visualization - Most Liquid Options
# plt.figure(figsize=(10, 5))
# options_df.sort_values(by="Total Orders", ascending=False).head(10).plot(
#     x="Strike", y="Total Orders", kind="bar", legend=False, color="skyblue")
# plt.xlabel("Strike Price")
# plt.ylabel("Total Orders")
# plt.title("Top 10 Most Liquid Options")
# plt.xticks(rotation=45)
# plt.show()

# Print Results
print("Highest Strike Option:\n", options_df.loc[options_df['Strike'].idxmax()])
print("\nLowest Strike Option:\n", options_df.loc[options_df['Strike'].idxmin()])
print("\nMost Liquid Option:\n", options_df.loc[options_df['Total Orders'].idxmax()])
print("\nAverage Bid Prices:\n", options_df.groupby("Type")["Bid Price"].mean())
print("\nAverage Ask Prices:\n", options_df.groupby("Type")["Ask Price"].mean())
print("\nOptions Data with Greeks:\n", options_df)
print("\nProbability of Expiring ITM:\n", options_df[["Strike", "Type", "Prob_ITM"]])
print("\nArbitrage Opportunities:\n", options_df[options_df["Arbitrage_Opp_Flag"]])
