import pandas as pd

df = pd.read_csv('saved_files/congestion/congestion_log_20251202_225841.csv')

print("Total trips:", len(df))
print("Mean ratio:", df['congestion_ratio'].mean())
print("Max ratio:", df['congestion_ratio'].max())
