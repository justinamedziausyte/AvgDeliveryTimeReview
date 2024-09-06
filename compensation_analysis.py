import pandas as pd
import matplotlib.pyplot as plt
import os

# Constants
INPUT_CSV_1 = 'shipping_data_1.csv'
INPUT_CSV_2 = 'shipping_data_2.csv'
RESULTS_FILE = 'output/compensation_analysis_results.txt'  # Ensure this path is correct
OUTPUT_DIR = 'output'

def create_output_dir():
    """Create output directory if not exists."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def load_data(files):
    """Load and concatenate CSV files."""
    try:
        dfs = [pd.read_csv(file) for file in files]
        df = pd.concat(dfs, ignore_index=True)
        print("CSV files read and concatenated successfully.")
        return df
    except Exception as e:
        print(f"Error reading or concatenating CSV files: {e}")
        return None

def preprocess_data(df):
    """Convert date columns to datetime format."""
    df['shipped_date'] = pd.to_datetime(df['shipped_date'])
    df['compensated_at_date'] = pd.to_datetime(df['compensated_at_date'], errors='coerce')
    return df

def analyze_compensations(df):
    """Analyze compensation data and write results to a file."""
    print("Starting analysis of compensations...")
    with open(RESULTS_FILE, 'w') as f:
        # Filter out rows without compensation
        compensation_df = df.dropna(subset=['total_compensation'])
        
        # Calculate total compensated shipments and total compensation amount
        total_compensated_transactions = len(compensation_df)
        total_compensation = compensation_df['total_compensation'].sum()
        
        # Compensation by Amount Summary
        avg_compensation = compensation_df['total_compensation'].mean()
        median_compensation = compensation_df['total_compensation'].median()
        max_compensation = compensation_df['total_compensation'].max()
        min_compensation = compensation_df['total_compensation'].min()

        compensation_amounts_summary = (
            f"Total Compensation Amount: ${total_compensation:.2f}\n"
            f"Average Compensation Amount: ${avg_compensation:.2f}\n"
            f"Median Compensation Amount: ${median_compensation:.2f}\n"
            f"Maximum Compensation Amount: ${max_compensation:.2f}\n"
            f"Minimum Compensation Amount: ${min_compensation:.2f}\n"
        )

        # Print and write compensation amounts summary
        print("Compensation Amounts Summary:")
        print(compensation_amounts_summary)
        f.write("Compensation Amounts Summary:\n")
        f.write(compensation_amounts_summary)

        # Compensation by Reason Summary
        compensation_by_reason = compensation_df.groupby('compensation_reason').agg(
            count=('total_compensation', 'size'),
            total_amount=('total_compensation', 'sum'),
            avg_amount=('total_compensation', 'mean')
        ).reset_index()

        # Add weights (percentages) for compensated shipments
        compensation_by_reason['transaction_weight'] = compensation_by_reason['count'] / total_compensated_transactions * 100
        compensation_by_reason['amount_weight'] = compensation_by_reason['total_amount'] / total_compensation * 100

        # Format the compensation by reason summary for file writing
        compensation_by_reason_summary = "\n".join(
            f"{row['compensation_reason']}: "
            f"Count = {row['count']}, "
            f"Total Amount = ${row['total_amount']:.2f}, "
            f"Average Amount = ${row['avg_amount']:.2f}, "
            f"Transaction Weight = {row['transaction_weight']:.2f}%, "
            f"Amount Weight = {row['amount_weight']:.2f}%"
            for idx, row in compensation_by_reason.iterrows()
        )
        
        # Print and write compensation by reason summary
        print("\nCompensation by Reason Summary:")
        print(compensation_by_reason_summary)
        f.write("\n\nCompensation by Reason Summary:\n")
        f.write(compensation_by_reason_summary)
    print("Compensation analysis completed and saved to file.")

def analyze_seasonal_patterns(df):
    """Perform seasonal pattern analysis and create stacked area chart."""
    # Convert shipment dates to MM-DD format for seasonal analysis
    df['shipped_month_day'] = df['shipped_date'].dt.strftime('%m-%d')
    
    # Group by shipment month-day and compensation reason to sum total compensation
    grouped_df = df.groupby(['shipped_month_day', 'compensation_reason']).agg(
        total_compensation=('total_compensation', 'sum')
    ).reset_index()

    # Drop rows with NaN values
    grouped_df = grouped_df.dropna()

    # Pivot the grouped dataframe for stacked area chart format
    pivot_df = grouped_df.pivot(index='shipped_month_day', columns='compensation_reason', values='total_compensation')
    pivot_df.fillna(0, inplace=True)

    # Plotting the stacked area chart
    plt.figure(figsize=(14, 8))
    pivot_df.plot.area(stacked=True, figsize=(14, 8), cmap='tab20')
    plt.xlabel('Month-Day')
    plt.ylabel('Total Compensation Amount')
    plt.title('Proportion of Compensation Amount by Shipment Date and Reason')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.legend(title='Compensation Reason')
    plt.savefig(os.path.join(OUTPUT_DIR, 'compensation_stacked_area.png'))
    plt.show()
    print("Seasonal pattern analysis completed and chart saved.")

def main():
    create_output_dir()
    print("Output directory created.")
    
    input_files = [INPUT_CSV_1, INPUT_CSV_2]
    df = load_data(input_files)
    print("Data loaded.")
    
    if df is not None:
        df = preprocess_data(df)
        print("Data preprocessed.")
        
        analyze_compensations(df)
        print("Compensation analysis completed.")
    
        analyze_seasonal_patterns(df)
        print("Seasonal pattern analysis completed.")
    
if __name__ == "__main__":
    main()
