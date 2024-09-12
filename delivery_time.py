import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Constants
INPUT_CSV_1 = 'shipping_data_1.csv'
INPUT_CSV_2 = 'shipping_data_2.csv'
RESULTS_DIR = 'results'

FILES = [INPUT_CSV_1, INPUT_CSV_2]
COMBINED_RESULTS_FILE = 'consolidated_analysis_results.csv'
CORRELATION_RESULTS_FILE = 'correlation_analysis_results.csv'
ANALYSIS_RESULTS_FILE = 'analysis_results.txt'


def create_results_dir():
    """Create results directory if not exists."""
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)

def load_and_preprocess_data(files):
    """Load and preprocess CSV files."""
    try:
        dfs = [pd.read_csv(file) for file in files]
        df = pd.concat(dfs, ignore_index=True)
        print("CSV files read and concatenated successfully.")
        df['shipped_date'] = pd.to_datetime(df['shipped_date'])
        df['compensated_at_date'] = pd.to_datetime(df['compensated_at_date'], errors='coerce')
        return df
    except Exception as e:
        print(f"Error reading or concatenating CSV files: {e}")
        return None

def calculate_metrics(df):
    """Calculate performance metrics."""
    metrics = {}
    total_shipments = len(df)
    total_compensated_shipments = len(df.dropna(subset=['total_compensation']))

    # Calculate metrics
    metrics['avg_delivery_time'] = df['delivery_time_business_days'].mean()
    expected_delivery_days = 7  # Adjust as necessary
    metrics['on_time_delivery_rate'] = (df['delivery_time_business_days'] <= expected_delivery_days).mean() * 100
    metrics['late_delivery_rate'] = (df['delivery_time_business_days'] > expected_delivery_days).mean() * 100
    metrics['cs_ticket_rate'] = df['has_marketplace_cs_ticket'].mean() * 100
    metrics['compensation_rate'] = df['total_compensation'].notnull().mean() * 100
    metrics['avg_compensation_amount'] = df['total_compensation'].dropna().mean()
    metrics['count_parcels'] = total_shipments
    metrics['shipment_weight'] = (total_shipments / total_compensated_shipments) * 100 if total_compensated_shipments else 0
    df['resolution_time'] = (df['compensated_at_date'] - df['shipped_date']).dt.days
    metrics['resolution_time_avg'] = df['resolution_time'].dropna().mean()
    
    return metrics

def analyze_and_consolidate(df):
    """Analyze and consolidate results by route and sortation center."""
    consolidated_data = []

    # Analyze by Route
    routes = df['route'].unique()
    for route in routes:
        route_df = df[df['route'] == route]
        metrics = calculate_metrics(route_df)
        metrics['type'] = 'Route'
        metrics['identifier'] = route
        consolidated_data.append(metrics)

    # Analyze by Sortation Center
    sortation_centers = df.groupby(['from_sc_code', 'to_sc_code'])
    for (from_sc, to_sc), group_df in sortation_centers:
        metrics = calculate_metrics(group_df)
        metrics['type'] = 'Sortation Center'
        metrics['identifier'] = f"{from_sc} -> {to_sc}"
        consolidated_data.append(metrics)

    # Save consolidated results
    consolidated_df = pd.DataFrame(consolidated_data)
    consolidated_df.to_csv(os.path.join(RESULTS_DIR, COMBINED_RESULTS_FILE), index=False)
    return consolidated_df

def analyze_seasonal_patterns(df):
    """Perform seasonal pattern analysis and create stacked area chart."""
    df['shipped_month_day'] = df['shipped_date'].dt.strftime('%m-%d')
    grouped_df = df.groupby(['shipped_month_day']).agg(
        avg_delivery_time=('delivery_time_business_days', 'mean'),
        avg_compensation_amount=('total_compensation', 'mean')
    ).dropna().reset_index()

    plt.figure(figsize=(12, 6))
    grouped_df.plot(x='shipped_month_day', y=['avg_delivery_time', 'avg_compensation_amount'], figsize=(12, 6))
    plt.xlabel('Month-Day')
    plt.ylabel('Value')
    plt.title('Seasonal Patterns of Delivery Time and Compensation Amount')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, 'seasonal_patterns.png'))
    plt.show()

def analyze_correlation(df):
    """Perform correlation analysis and save results."""
    df['shipped_date_mmdd'] = df['shipped_date'].dt.strftime('%m-%d')
    grouped_df = df.groupby('shipped_date_mmdd').agg(
        avg_delivery_time=('delivery_time_business_days', 'mean'),
        avg_compensation_amount=('total_compensation', 'mean')
    ).dropna().reset_index()

    correlation = grouped_df['avg_delivery_time'].corr(grouped_df['avg_compensation_amount'])
    print(f"Correlation between average delivery time and compensation amount: {correlation:.2f}")

    grouped_df.to_csv(os.path.join(RESULTS_DIR, CORRELATION_RESULTS_FILE), index=False)

    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=grouped_df, x='avg_delivery_time', y='avg_compensation_amount')
    plt.title('Correlation Between Average Delivery Time and Compensation Amount')
    plt.xlabel('Average Delivery Time (days)')
    plt.ylabel('Average Compensation Amount')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, 'correlation_plot.png'))
    plt.show()

def analyze_to_text(df):
    """Perform textual analysis and save results to a file."""
    with open(os.path.join(RESULTS_DIR, ANALYSIS_RESULTS_FILE), 'w') as f:
        average_delivery_time = df['delivery_time_business_days'].mean()
        expected_days = 5
        on_time_delivery_rate = (df['delivery_time_business_days'] <= expected_days).mean()
        compensation_rate = df['total_compensation'].notnull().mean()
        avg_compensation_amount = df['total_compensation'].dropna().mean()
        cs_ticket_rate = df['has_marketplace_cs_ticket'].mean()
        df['resolution_time'] = (df['compensated_at_date'] - df['shipped_date']).dt.days
        resolution_time_avg = df['resolution_time'].dropna().mean()

        results = (
            f"Average Delivery Time: {average_delivery_time:.2f} business days\n"
            f"On-Time Delivery Rate: {on_time_delivery_rate:.2%}\n"
            f"Compensation Rate: {compensation_rate:.2%}\n"
            f"Average Compensation Amount: {avg_compensation_amount:.2f}\n"
            f"Customer Service Ticket Rate: {cs_ticket_rate:.2%}\n"
            f"Average Resolution Time: {resolution_time_avg:.2f} days\n"
        )

        print(results)
        f.write(results)

def main():
    create_results_dir()

    # Load and preprocess data
    df = load_and_preprocess_data(FILES)
    
    if df is not None:
        # Consolidate results
        consolidated_data = analyze_and_consolidate(df)

        # Analyze seasonal patterns
        analyze_seasonal_patterns(df)

        # Perform correlation analysis
        analyze_correlation(df)

        # Analyze to text
        analyze_to_text(df)

if __name__ == "__main__":
    main()
