import pandas as pd

# Constants
INPUT_CSV_1 = 'shipping_data_1.csv'
INPUT_CSV_2 = 'shipping_data_2.csv'
ORIGINAL_COST_PER_PARCEL = 6.81  # in EUR
RESULTS_FILE = 'new_cost_per_parcel_analysis.csv'

def calculate_metrics(df, volume_increase_per_day):
    metrics = {}

    # Calculate total shipments
    total_shipments = len(df)
    
    # Current average delivery time
    avg_delivery_time = df['delivery_time_business_days'].mean()
    
    # Improved average delivery time by 10%
    improved_avg_delivery_time = avg_delivery_time * 0.90
    
    # Delivery time reduction
    delivery_time_reduction = avg_delivery_time - improved_avg_delivery_time
    
    # Volume increase based on scenario
    volume_increase_percentage = delivery_time_reduction * volume_increase_per_day * 100
    new_total_volume = total_shipments * (1 + (volume_increase_percentage / 100))
    
    # Calculate total cost (assuming the original cost per parcel)
    original_total_cost = total_shipments * ORIGINAL_COST_PER_PARCEL
    new_cost_per_parcel = original_total_cost / new_total_volume
    
    metrics['average_volume_increase_per_day'] = volume_increase_per_day
    metrics['original_avg_delivery_time'] = avg_delivery_time
    metrics['improved_avg_delivery_time'] = improved_avg_delivery_time
    metrics['original_total_volume'] = total_shipments
    metrics['new_total_volume'] = new_total_volume
    metrics['original_total_cost'] = original_total_cost
    metrics['new_cost_per_parcel'] = new_cost_per_parcel
    metrics['volume_increase_percentage'] = volume_increase_percentage
    metrics['delivery_time_reduction'] = delivery_time_reduction
    
    return metrics

def main():
    # Read CSV files and concatenate them
    dfs = [pd.read_csv(file) for file in [INPUT_CSV_1, INPUT_CSV_2]]
    df = pd.concat(dfs, ignore_index=True)
    
    # Convert dates to datetime
    df['shipped_date'] = pd.to_datetime(df['shipped_date'])
    df['compensated_at_date'] = pd.to_datetime(df['compensated_at_date'], errors='coerce')
    
    # Scenarios
    scenarios = {
        'pessimistic': 0.01,
        'neutral': 0.05,
        'optimistic': 0.08
    }
    
    # Calculate metrics for each scenario
    results = []
    for scenario, volume_increase_per_day in scenarios.items():
        metrics = calculate_metrics(df, volume_increase_per_day)
        metrics['scenario'] = scenario
        results.append(metrics)
    
    # Create DataFrame and save to CSV
    results_df = pd.DataFrame(results)
    results_df.to_csv(RESULTS_FILE, index=False)
    
    # Print the results
    print(results_df)

if __name__ == "__main__":
    main()
