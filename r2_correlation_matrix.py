#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
r2_correlation_matrix.py

This script analyzes ETF price correlations and R-squared values:

1. Reads all ETF CSV files from the 'data' directory
2. Creates a correlation matrix of their closing prices
3. Calculates R-squared values (square of correlation coefficients)
4. Computes average correlation and R-squared for each ETF
5. Generates visualizations:
   - Correlation matrix heatmap
   - R-squared matrix heatmap
   - Bar charts of average correlation and R-squared by ETF
6. Saves results to CSV files and image files in the 'output' directory

Usage:
    python r2_correlation_matrix.py

Requirements:
    - pandas
    - numpy
    - matplotlib
    - seaborn
    - ETF data CSV files in the 'data' directory (run download_historical_data.py first)

Output files (saved in the 'output' directory):
    - etf_correlation_matrix.csv: Full correlation matrix
    - etf_r2_matrix.csv: Full R-squared matrix
    - etf_average_metrics.csv: Average correlation and R-squared by ETF
    - etf_correlation_matrix.png: Heatmap visualizations
    - etf_average_metrics.png: Bar chart visualizations
"""

import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set the dark background style
plt.style.use('dark_background')

def main():
    # Get the data directory
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    
    # Create data directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)
    
    # Create output directory for saving results
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Check if the data directory is empty
    if not os.path.exists(data_dir) or not os.listdir(data_dir):
        print(f"Data directory {data_dir} is empty. Please run download_historical_data.py first.")
        return
    
    # Find all CSV files in the data directory
    csv_files = glob.glob(os.path.join(data_dir, "*_data.csv"))
    
    if not csv_files:
        print(f"No CSV files found in {data_dir}. Please run download_historical_data.py first.")
        return
    
    print(f"Found {len(csv_files)} ETF data files.")
    
    # Create a dictionary to store the closing prices for each ETF
    etf_data = {}
    
    # Read each CSV file and extract the closing prices
    for csv_file in csv_files:
        # Extract the ETF ticker from the filename
        ticker = os.path.basename(csv_file).split('_')[0]
        
        try:
            # Read the CSV file
            df = pd.read_csv(csv_file, index_col=0, parse_dates=True)
            
            # Extract the closing prices
            etf_data[ticker] = df['Close']
            print(f"Loaded data for {ticker} with {len(df)} rows.")
        except Exception as e:
            print(f"Error loading data for {ticker}: {e}")
    
    if not etf_data:
        print("No ETF data could be loaded. Please check the CSV files.")
        return
    
    # Create a DataFrame with all ETF closing prices
    prices_df = pd.DataFrame(etf_data)
    
    # Calculate the correlation matrix
    correlation_matrix = prices_df.corr()
    
    # Calculate the R-squared matrix (square of correlation coefficients)
    r2_matrix = correlation_matrix ** 2
    
    # Calculate average correlation and R-squared for each ETF (excluding self-correlation)
    avg_correlation = {}
    avg_r2 = {}
    
    for ticker in correlation_matrix.columns:
        # Get all correlations for this ticker except with itself
        correlations = correlation_matrix[ticker].drop(ticker)
        r2_values = r2_matrix[ticker].drop(ticker)
        
        avg_correlation[ticker] = correlations.mean()
        avg_r2[ticker] = r2_values.mean()
    
    # Create DataFrames for average values
    avg_corr_df = pd.DataFrame.from_dict(avg_correlation, orient='index', columns=['Avg_Correlation'])
    avg_r2_df = pd.DataFrame.from_dict(avg_r2, orient='index', columns=['Avg_R2'])
    
    # Sort by average correlation
    avg_corr_df = avg_corr_df.sort_values('Avg_Correlation', ascending=False)
    avg_r2_df = avg_r2_df.sort_values('Avg_R2', ascending=False)
    
    print("\nAverage Correlation:")
    print(avg_corr_df)
    
    print("\nAverage R-squared:")
    print(avg_r2_df)
    
    print("\nCorrelation Matrix:")
    print(correlation_matrix)
    
    print("\nR-squared Matrix:")
    print(r2_matrix)
    
    # Save matrices to CSV files in the output directory
    corr_csv_file = os.path.join(output_dir, "etf_correlation_matrix.csv")
    r2_csv_file = os.path.join(output_dir, "etf_r2_matrix.csv")
    avg_metrics_csv_file = os.path.join(output_dir, "etf_average_metrics.csv")
    
    correlation_matrix.to_csv(corr_csv_file)
    r2_matrix.to_csv(r2_csv_file)
    
    # Combine average correlation and R-squared into one DataFrame
    avg_metrics = pd.concat([avg_corr_df, avg_r2_df], axis=1)
    avg_metrics.to_csv(avg_metrics_csv_file)
    
    print(f"Correlation matrix saved to {corr_csv_file}")
    print(f"R-squared matrix saved to {r2_csv_file}")
    print(f"Average metrics saved to {avg_metrics_csv_file}")
    
    # Create heatmap visualizations
    fig, axes = plt.subplots(1, 2, figsize=(20, 10))
    
    # Create a mask for the upper triangle
    mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
    
    # Draw the correlation heatmap
    sns.heatmap(
        correlation_matrix,
        mask=mask,
        cmap="RdBu_r",
        vmax=1.0,
        vmin=-1.0,
        center=0,
        square=True,
        linewidths=.5,
        cbar_kws={"shrink": .5},
        annot=True,
        fmt=".2f",
        ax=axes[0],
        annot_kws={"fontsize": 16}
    )
    axes[0].set_title('Correlation Matrix', fontsize=16)
    axes[0].tick_params(labelsize=16)
    
    # Draw the R-squared heatmap
    sns.heatmap(
        r2_matrix,
        mask=mask,
        cmap="YlGnBu",
        vmax=1.0,
        vmin=0,
        square=True,
        linewidths=.5,
        cbar_kws={"shrink": .5},
        annot=True,
        fmt=".2f",
        ax=axes[1],
        annot_kws={"fontsize": 16}
    )
    axes[1].set_title('R-squared Matrix', fontsize=16)
    axes[1].tick_params(labelsize=16)
    
    plt.tight_layout()
    
    # Save the plots to the output directory
    corr_output_file = os.path.join(output_dir, "etf_correlation_matrix.png")
    plt.savefig(corr_output_file, dpi=300, bbox_inches='tight')
    print(f"\nMatrix plots saved to {corr_output_file}")
    
    # Show the plots
    plt.show()
    
    # Create bar charts for average correlation and R-squared values
    fig, axes = plt.subplots(2, 1, figsize=(12, 14))
    
    # Plot average correlation
    sns.barplot(x=avg_corr_df.index, y='Avg_Correlation', data=avg_corr_df, ax=axes[0], palette='viridis')
    axes[0].set_title('Average Correlation', fontsize=16)
    axes[0].set_xlabel('Ticker', fontsize=16)
    axes[0].set_ylabel('Average Correlation', fontsize=16)
    axes[0].set_xticklabels(axes[0].get_xticklabels(), rotation=45, fontsize=16)
    axes[0].tick_params(axis='y', labelsize=16)
    axes[0].axhline(y=0, color='r', linestyle='-', alpha=0.3)
    
    # Add value labels on top of bars
    for i, v in enumerate(avg_corr_df['Avg_Correlation']):
        axes[0].text(i, v + 0.02, f'{v:.2f}', ha='center', fontsize=16)
    
    # Plot average R-squared
    sns.barplot(x=avg_r2_df.index, y='Avg_R2', data=avg_r2_df, ax=axes[1], palette='plasma')
    axes[1].set_title('Average R-squared', fontsize=16)
    axes[1].set_xlabel('Ticker', fontsize=16)
    axes[1].set_ylabel('Average R-squared', fontsize=16)
    axes[1].set_xticklabels(axes[1].get_xticklabels(), rotation=45, fontsize=16)
    axes[1].tick_params(axis='y', labelsize=16)
    
    # Add value labels on top of bars
    for i, v in enumerate(avg_r2_df['Avg_R2']):
        axes[1].text(i, v + 0.02, f'{v:.2f}', ha='center', fontsize=16)
    
    plt.tight_layout()
    
    # Save the bar charts to the output directory
    bar_output_file = os.path.join(output_dir, "etf_average_metrics.png")
    plt.savefig(bar_output_file, dpi=300, bbox_inches='tight')
    print(f"Average metrics bar charts saved to {bar_output_file}")
    
    # Show the bar charts
    plt.show()

if __name__ == "__main__":
    main()
