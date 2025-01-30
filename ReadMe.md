# Options Data Analysis Tool

A Python script to analyze and visualize options chain data from a JSON file. Extracts key metrics like bid-ask spreads, liquidity, and strike price distributions for both calls and puts.

## Features
- Processes JSON options chain data
- Calculates bid-ask spreads and total order liquidity
- Identifies:
  - Highest/lowest strike prices
  - Most liquid options
  - Average bid/ask prices by option type
- Generates visualizations:
  - Strike price distribution histogram
  - Top 10 most liquid options chart

## Prerequisites
- Python 3.x
- Required packages:
  ```bash
  pip install pandas matplotlib