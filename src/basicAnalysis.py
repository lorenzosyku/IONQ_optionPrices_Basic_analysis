import json
import pandas as pd
import matplotlib.pyplot as plt

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

# Basic Analysis
highest_strike = options_df.loc[options_df['Strike'].idxmax()]
lowest_strike = options_df.loc[options_df['Strike'].idxmin()]
most_liquid_option = options_df.loc[options_df['Total Orders'].idxmax()]
avg_bid_price = options_df.groupby("Type")["Bid Price"].mean()
avg_ask_price = options_df.groupby("Type")["Ask Price"].mean()

# Visualization - Strike Price Distribution
plt.figure(figsize=(10, 5))
options_df["Strike"].hist(bins=20, color="orange", edgecolor="black")
plt.xlabel("Strike Price")
plt.ylabel("Frequency")
plt.title("Distribution of Strike Prices")
plt.show()

# Visualization - Most Liquid Options
plt.figure(figsize=(10, 5))
options_df.sort_values(by="Total Orders", ascending=False).head(10).plot(
    x="Strike", y="Total Orders", kind="bar", legend=False, color="skyblue")
plt.xlabel("Strike Price")
plt.ylabel("Total Orders")
plt.title("Top 10 Most Liquid Options")
plt.xticks(rotation=45)
plt.show()

# Print Results
print("Highest Strike Option:\n", highest_strike)
print("\nLowest Strike Option:\n", lowest_strike)
print("\nMost Liquid Option:\n", most_liquid_option)
print("\nAverage Bid Prices:\n", avg_bid_price)
print("\nAverage Ask Prices:\n", avg_ask_price)