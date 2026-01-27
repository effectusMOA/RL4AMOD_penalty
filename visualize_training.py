"""
SAC 학습 곡선 시각화
"""
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

print("=" * 70)
print("SAC 학습 곡선 분석 및 시각화")
print("=" * 70)

# 최신 학습 로그 찾기
log_dir = Path("saved_files/training_logs")
if not log_dir.exists():
    print(f"\n⚠️ 로그 디렉토리가 없습니다: {log_dir}")
    print("학습을 먼저 실행해주세요.")
    exit(1)

csv_files = list(log_dir.glob("training_metrics_*.csv"))
if not csv_files:
    print(f"\n⚠️ CSV 파일이 없습니다: {log_dir}")
    print("학습을 먼저 실행해주세요.")
    exit(1)

# 최신 파일 선택
latest_csv = max(csv_files, key=lambda x: x.stat().st_mtime)
print(f"\n📁 분석 파일: {latest_csv.name}")

# 데이터 로드
df = pd.read_csv(latest_csv)
print(f"   총 에피소드: {len(df)}")
print(f"   컬럼: {list(df.columns)}")

# 통계 요약
print("\n" + "=" * 70)
print("학습 통계 요약")
print("=" * 70)
print(f"\n{df.describe()}")

# 시각화
fig, axes = plt.subplots(2, 2, figsize=(15, 10))
fig.suptitle('SAC Training Metrics', fontsize=16, fontweight='bold')

# 1. Reward
ax1 = axes[0, 0]
ax1.plot(df['Episode'], df['Reward'], 'b-', alpha=0.3, label='Raw')
# Moving average
window = min(5, len(df))
if len(df) >= window:
    df['Reward_MA'] = df['Reward'].rolling(window=window).mean()
    ax1.plot(df['Episode'], df['Reward_MA'], 'b-', linewidth=2, label=f'MA({window})')
ax1.set_xlabel('Episode')
ax1.set_ylabel('Reward')
ax1.set_title('Episode Reward')
ax1.legend()
ax1.grid(True, alpha=0.3)

# 2. Served Demand
ax2 = axes[0, 1]
ax2.plot(df['Episode'], df['Served_Demand'], 'g-', alpha=0.3, label='Raw')
if len(df) >= window:
    df['Demand_MA'] = df['Served_Demand'].rolling(window=window).mean()
    ax2.plot(df['Episode'], df['Demand_MA'], 'g-', linewidth=2, label=f'MA({window})')
ax2.set_xlabel('Episode')
ax2.set_ylabel('Served Demand')
ax2.set_title('Served Demand per Episode')
ax2.legend()
ax2.grid(True, alpha=0.3)

# 3. Rebalancing Cost
ax3 = axes[1, 0]
ax3.plot(df['Episode'], df['Rebalancing_Cost'], 'r-', alpha=0.3, label='Raw')
if len(df) >= window:
    df['Cost_MA'] = df['Rebalancing_Cost'].rolling(window=window).mean()
    ax3.plot(df['Episode'], df['Cost_MA'], 'r-', linewidth=2, label=f'MA({window})')
ax3.set_xlabel('Episode')
ax3.set_ylabel('Rebalancing Cost')
ax3.set_title('Rebalancing Cost per Episode')
ax3.legend()
ax3.grid(True, alpha=0.3)

# 4. Cost/Demand Ratio
ax4 = axes[1, 1]
df['Cost_Ratio'] = df['Rebalancing_Cost'] / df['Served_Demand'].replace(0, np.nan)
ax4.plot(df['Episode'], df['Cost_Ratio'], 'purple', alpha=0.3, label='Raw')
if len(df) >= window:
    df['Ratio_MA'] = df['Cost_Ratio'].rolling(window=window).mean()
    ax4.plot(df['Episode'], df['Ratio_MA'], 'purple', linewidth=2, label=f'MA({window})')
ax4.set_xlabel('Episode')
ax4.set_ylabel('Cost / Demand Ratio')
ax4.set_title('Efficiency Metric (Lower is Better)')
ax4.legend()
ax4.grid(True, alpha=0.3)
ax4.axhline(y=1.0, color='k', linestyle='--', alpha=0.5, label='Break-even')

plt.tight_layout()

# 저장
output_file = log_dir / f"training_curves_{latest_csv.stem.split('_')[-1]}.png"
plt.savefig(output_file, dpi=150, bbox_inches='tight')
print(f"\n✅ 그래프 저장: {output_file}")

# 표시 (선택적)
try:
    plt.show()
except:
    print("   (GUI 환경이 아니어서 그래프를 표시할 수 없습니다)")

print("\n" + "=" * 70)
print("주요 지표")
print("=" * 70)
print(f"초기 Reward:  {df['Reward'].iloc[0]:>12.2f}")
print(f"최종 Reward:  {df['Reward'].iloc[-1]:>12.2f}")
print(f"최고 Reward:  {df['Reward'].max():>12.2f} (Episode {df['Reward'].idxmax()+1})")
print(f"평균 Reward:  {df['Reward'].mean():>12.2f}")
print()
print(f"평균 Served Demand:     {df['Served_Demand'].mean():>12.2f}")
print(f"평균 Rebalancing Cost:  {df['Rebalancing_Cost'].mean():>12.2f}")
print(f"평균 Cost/Demand Ratio: {df['Cost_Ratio'].mean():>12.2f}")

print("\n" + "=" * 70)
