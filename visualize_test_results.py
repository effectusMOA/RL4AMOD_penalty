"""
테스트 결과 시각화
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

print("=" * 70)
print("SAC 테스트 결과 분석")
print("=" * 70)

# 최신 테스트 결과 찾기
test_dir = Path("saved_files/test_results")
if not test_dir.exists():
    print(f"\n⚠️ 테스트 결과 디렉토리가 없습니다: {test_dir}")
    print("테스트를 먼저 실행해주세요.")
    exit(1)

csv_files = list(test_dir.glob("test_results_*.csv"))
if not csv_files:
    print(f"\n⚠️ CSV 파일이 없습니다: {test_dir}")
    print("테스트를 먼저 실행해주세요.")
    exit(1)

# 최신 파일 선택
latest_csv = max(csv_files, key=lambda x: x.stat().st_mtime)
print(f"\n📁 분석 파일: {latest_csv.name}")

# 데이터 로드
df = pd.read_csv(latest_csv)
print(f"   테스트 에피소드: {len(df)}")

# 통계 출력
print("\n" + "=" * 70)
print("테스트 결과 통계")
print("=" * 70)

print(f"\nReward:")
print(f"  평균: {df['Reward'].mean():.2f}")
print(f"  표준편차: {df['Reward'].std():.2f}")
print(f"  최소: {df['Reward'].min():.2f}")
print(f"  최대: {df['Reward'].max():.2f}")

print(f"\nServed Demand:")
print(f"  평균: {df['Served_Demand'].mean():.2f}")
print(f"  표준편차: {df['Served_Demand'].std():.2f}")

print(f"\nRebalancing Cost:")
print(f"  평균: {df['Rebalancing_Cost'].mean():.2f}")
print(f"  표준편차: {df['Rebalancing_Cost'].std():.2f}")

df['Cost_Ratio'] = df['Rebalancing_Cost'] / df['Served_Demand']
print(f"\nCost/Demand Ratio:")
print(f"  평균: {df['Cost_Ratio'].mean():.4f}")
print(f"  표준편차: {df['Cost_Ratio'].std():.4f}")

# 시각화
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('SAC Test Results', fontsize=16, fontweight='bold')

# 1. Reward
ax1 = axes[0, 0]
ax1.bar(df['Episode'], df['Reward'], alpha=0.7, color='blue')
ax1.axhline(y=df['Reward'].mean(), color='r', linestyle='--', 
            label=f'평균: {df["Reward"].mean():.2f}')
ax1.axhline(y=0, color='k', linestyle='-', alpha=0.3)
ax1.set_xlabel('Episode')
ax1.set_ylabel('Reward')
ax1.set_title('Episode Reward')
ax1.legend()
ax1.grid(True, alpha=0.3, axis='y')

# 2. Served Demand
ax2 = axes[0, 1]
ax2.bar(df['Episode'], df['Served_Demand'], alpha=0.7, color='green')
ax2.axhline(y=df['Served_Demand'].mean(), color='r', linestyle='--',
            label=f'평균: {df["Served_Demand"].mean():.0f}')
ax2.set_xlabel('Episode')
ax2.set_ylabel('Served Demand')
ax2.set_title('Served Demand per Episode')
ax2.legend()
ax2.grid(True, alpha=0.3, axis='y')

# 3. Rebalancing Cost
ax3 = axes[1, 0]
ax3.bar(df['Episode'], df['Rebalancing_Cost'], alpha=0.7, color='red')
ax3.axhline(y=df['Rebalancing_Cost'].mean(), color='darkred', linestyle='--',
            label=f'평균: {df["Rebalancing_Cost"].mean():.0f}')
ax3.set_xlabel('Episode')
ax3.set_ylabel('Rebalancing Cost')
ax3.set_title('Rebalancing Cost per Episode')
ax3.legend()
ax3.grid(True, alpha=0.3, axis='y')

# 4. Cost/Demand Ratio
ax4 = axes[1, 1]
ax4.bar(df['Episode'], df['Cost_Ratio'], alpha=0.7, color='purple')
ax4.axhline(y=df['Cost_Ratio'].mean(), color='darkviolet', linestyle='--',
            label=f'평균: {df["Cost_Ratio"].mean():.3f}')
ax4.axhline(y=1.0, color='k', linestyle='-', alpha=0.3, label='Break-even')
ax4.set_xlabel('Episode')
ax4.set_ylabel('Cost / Demand Ratio')
ax4.set_title('Efficiency Metric')
ax4.legend()
ax4.grid(True, alpha=0.3, axis='y')

plt.tight_layout()

# 저장
output_file = test_dir / f"test_visualization_{latest_csv.stem.split('_')[-1]}.png"
plt.savefig(output_file, dpi=150, bbox_inches='tight')
print(f"\n✅ 그래프 저장: {output_file}")

# 표시
try:
    plt.show()
except:
    print("   (GUI 환경이 아니어서 그래프를 표시할 수 없습니다)")

print("\n" + "=" * 70)
print("💡 성능 평가")
print("=" * 70)

avg_reward = df['Reward'].mean()
avg_ratio = df['Cost_Ratio'].mean()

if avg_reward > 0:
    print(f"✅ 평균 Reward가 양수입니다: {avg_reward:.2f}")
    print("   모델이 수익을 창출하고 있습니다!")
else:
    print(f"⚠️ 평균 Reward가 음수입니다: {avg_reward:.2f}")
    print("   추가 학습이 필요할 수 있습니다.")

if avg_ratio < 1.0:
    print(f"✅ Cost/Demand 비율이 1.0 미만입니다: {avg_ratio:.3f}")
    print("   효율적인 재배치 정책입니다!")
else:
    print(f"⚠️ Cost/Demand 비율이 1.0 이상입니다: {avg_ratio:.3f}")
    print("   재배치 비용이 상대적으로 높습니다.")

# 일관성 평가
reward_cv = df['Reward'].std() / abs(df['Reward'].mean()) if df['Reward'].mean() != 0 else float('inf')
if reward_cv < 0.1:
    print(f"✅ Reward 일관성이 높습니다 (CV: {reward_cv:.3f})")
elif reward_cv < 0.3:
    print(f"⚠️ Reward 변동성이 보통입니다 (CV: {reward_cv:.3f})")
else:
    print(f"❌ Reward 변동성이 높습니다 (CV: {reward_cv:.3f})")
    print("   정책이 불안정할 수 있습니다.")

print("\n" + "=" * 70)
