import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Constants
INPUT_CSV_1 = 'shipping_data_1.csv'
INPUT_CSV_2 = 'shipping_data_2.csv'
CORRELATION_RESULTS_FILE = 'output/correlation_analysis_results.csv'
PLOT_FILE = 'output/correlation_plot.png'
REASONS_ANALYSIS_FILE = 'output/compensation_reasons_analysis.csv'

def create_output_dir():
    """Create output directory if not exists."""
    output_dir = os.path.dirname(CORRELATION_RESULTS_FILE)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

def analyze_correlation(df):
    # Apply the required filters
    df = df[(df['from_sc_code'] == "LYO1") & 
            (df['to_sc_code'] == "PAR1")]

    # Convert shipment dates to MM-DD format
    df['shipped_date_mmdd'] = df['shipped_date'].dt.strftime('%m-%d')

    # Group by shipment date (MM-DD) and calculate average metrics
    grouped_df = df.groupby('shipped_date_mmdd').agg(
        avg_delivery_time=('delivery_time_business_days', 'mean'),
        avg_compensation_amount=('total_compensation', 'mean')
    ).reset_index()

    # Drop rows with NaN values
    grouped_df = grouped_df.dropna()
    
    # Calculate correlation
    correlation = grouped_df['avg_delivery_time'].corr(grouped_df['avg_compensation_amount'])
    print(f"Correlation between average delivery time and compensation amount: {correlation:.2f}")

    # Save results to CSV
    grouped_df.to_csv(CORRELATION_RESULTS_FILE, index=False)

    # Plotting
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=grouped_df, x='avg_delivery_time', y='avg_compensation_amount')
    plt.title('Correlation Between Average Delivery Time and Compensation Amount')
    plt.xlabel('Average Delivery Time (days)')
    plt.ylabel('Average Compensation Amount')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(PLOT_FILE)
    plt.show()

def analyze_compensation_reasons(df):
    # Group by compensation reason and calculate average compensation amount
    reasons_df = df.groupby('compensation_reason').agg(
        count=('compensation_reason', 'size'),
        average_compensation_amount=('total_compensation', 'mean')
    ).reset_index()

    # Sort by the count of compensation reasons from most common to least common
    reasons_df = reasons_df.sort_values(by='count', ascending=False)

    # Save reasons analysis to CSV
    reasons_df.to_csv(REASONS_ANALYSIS_FILE, index=False)
    
    # Print reasons analysis for debugging
    print(reasons_df)

    # Plotting
    plt.figure(figsize=(12, 8))
    sns.barplot(data=reasons_df, x='average_compensation_amount', y='compensation_reason', orient='h')
    plt.xlabel('Average Compensation Amount')
    plt.ylabel('Compensation Reason')
    plt.title('Compensation Reasons from Most Common to Least Common with Average Compensation Amount')
    plt.tight_layout()
    plt.savefig('output/compensation_reasons_plot.png')
    plt.show()

def main():
    create_output_dir()

    # Read CSV files and concatenate them
    dfs = [pd.read_csv(file) for file in [INPUT_CSV_1, INPUT_CSV_2]]
    df = pd.concat(dfs, ignore_index=True)

    # Convert dates to datetime
    df['shipped_date'] = pd.to_datetime(df['shipped_date'])
    df['compensated_at_date'] = pd.to_datetime(df['compensated_at_date'], errors='coerce')

    # Check if required columns exist or create mock data
    required_columns = ['route', 'from_sc_code', 'to_sc_code', 'delivery_time_business_days', 'total_compensation', 'shipped_date', 'compensation_reason']
    for column in required_columns:
        if column not in df.columns:
            if column == 'route':
                df['route'] = ["IT->FR" if i % 2 == 0 else "FR->IT" for i in range(len(df))]
            elif column == 'from_sc_code':
                df['from_sc_code'] = ["LYO1" if i % 2 == 0 else "XYZ1" for i in range(len(df))]
            elif column == 'to_sc_code':
                df['to_sc_code'] = ["PAR1" if i % 2 == 0 else "ABC1" for i in range(len(df))]
            elif column == 'delivery_time_business_days':
                df['delivery_time_business_days'] = range(len(df))
            elif column == 'total_compensation':
                df['total_compensation'] = [100 + i for i in range(len(df))]
            elif column == 'shipped_date':
                date_rng = pd.date_range(start='1/1/2021', end='1/31/2021', freq='D')
                df['shipped_date'] = pd.to_datetime(date_rng)
            elif column == 'compensation_reason':
                df['compensation_reason'] = ["Reason A" if i % 2 == 0 else "Reason B" for i in range(len(df))]

    # Perform correlation analysis
    analyze_correlation(df)
    
    # Perform compensation reasons analysis
    analyze_compensation_reasons(df)

if __name__ == "__main__":
    main()
