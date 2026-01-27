import pandas as pd

df = pd.read_csv('saved_files/congestion/congestion_log_20251202_225841.csv')

edge_stats = df.groupby('edge').agg({
    'congestion_ratio': 'mean',
    'edge': 'count'
}).rename(columns={'edge': 'trip_count', 'congestion_ratio': 'avg_ratio'})

significant = edge_stats[edge_stats['trip_count'] >= 5]
correlation = significant['trip_count'].corr(significant['avg_ratio'])

with open('correlation_result.txt', 'w') as f:
    f.write(f"Correlation: {correlation}\n")
    f.write("\nTop 10 Congested:\n")
    for edge, row in significant.nlargest(10, 'avg_ratio').iterrows():
        f.write(f"{edge}: {row['avg_ratio']:.2f}x, trips={row['trip_count']}\n")
    f.write("\nTop 10 Frequent:\n")
    for edge, row in significant.nlargest(10, 'trip_count').iterrows():
        f.write(f"{edge}: {row['trip_count']} trips, avg={row['avg_ratio']:.2f}x\n")

print("Done")
