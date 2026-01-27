import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# CSV 읽기
df = pd.read_csv('saved_files/congestion/congestion_log_20251202_225841.csv')

print('📊 ========== 혼잡도 분석 결과 ==========\n')
print(f'총 리밸런싱 트립 수: {len(df)}')
print(f'혼잡 트립 (>20% 지연): {df["is_congested"].sum()} ({df["is_congested"].mean()*100:.1f}%)')
print(f'평균 혼잡도 비율: {df["congestion_ratio"].mean():.2f}x')
print(f'최대 혼잡도 비율: {df["congestion_ratio"].max():.2f}x')
print(f'평균 지연 시간: {(df["actual_time"] - df["predicted_time"]).mean():.1f}분\n')

# 가장 혼잡한 경로 Top 10
print('\n가장 혼잡한 경로 Top 10:')
edge_stats = df.groupby('edge').agg({
    'congestion_ratio': ['mean', 'max', 'count']
}).reset_index()
edge_stats.columns = ['edge', 'avg_ratio', 'max_ratio', 'count']
edge_stats = edge_stats[edge_stats['count'] >= 5]  # 5회 이상만
edge_stats = edge_stats.sort_values('avg_ratio', ascending=False).head(10)
for idx, row in edge_stats.iterrows():
    print(f" {row['edge']}: 평균 {row['avg_ratio']:.2f}x, 최대 {row['max_ratio']:.2f}x (n={int(row['count'])})")

# congestion_ratio별 분포
print('\n\n혼잡도 분포:')
bins = [0, 0.5, 1.0, 1.2, 1.5, 2.0, 10.0]
labels = ['<0.5x (빠름)', '0.5-1.0x (정상)', '1.0-1.2x (약간 혼잡)', '1.2-1.5x (혼잡)', '1.5-2.0x (매우 혼잡)', '>2.0x (극심한 혼잡)']
df['ratio_category'] = pd.cut(df['congestion_ratio'], bins=bins, labels=labels)
print(df['ratio_category'].value_counts().sort_index())

# 시간대별 혼잡도
print('\n\n시간대별 혼잡도 추이:')
df['time_group'] = (df['departure_time'] // 5) * 5
time_stats = df.groupby('time_group').agg({
    'congestion_ratio': 'mean',
    'is_congested': ['mean', 'count']
})
print(time_stats)

# 간단한 통계
print('\n\n추가 통계:')
print(f'- 실제 시간이 예상보다 빠른 경우: {(df["congestion_ratio"] < 1).sum()}회 ({(df["congestion_ratio"] < 1).mean()*100:.1f}%)')
print(f'- 실제 시간이 예상과 동일한 경우: {(df["congestion_ratio"] == 1).sum()}회 ({(df["congestion_ratio"] == 1).mean()*100:.1f}%)')
print(f'- 실제 시간이 예상보다 느린 경우: {(df["congestion_ratio"] > 1).sum()}회 ({(df["congestion_ratio"] > 1).mean()*100:.1f}%)')

print('\n=========================================')
