"""
학습 결과 상세 분석
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 데이터 로드
df = pd.read_csv("saved_files/training_logs/training_metrics_20251127_033354.csv")

print("=" * 80)
print("SAC 학습 결과 분석")
print("=" * 80)

# 크래시 분석
completed_episodes = df[df['Steps_Completed'] == 301]
crashed_episodes = df[df['Steps_Completed'] < 301]

print(f"\n📊 에피소드 통계:")
print(f"  총 에피소드: {len(df)}")
print(f"  완료된 에피소드: {len(completed_episodes)} ({len(completed_episodes)/len(df)*100:.1f}%)")
print(f"  크래시 에피소드: {len(crashed_episodes)} ({len(crashed_episodes)/len(df)*100:.1f}%)")

# 완료된 에피소드만 분석
print(f"\n📈 완료된 에피소드 성능:")
print(f"  평균 Reward: {completed_episodes['Reward'].mean():.2f}")
print(f"  최고 Reward: {completed_episodes['Reward'].max():.2f} (Episode {completed_episodes['Reward'].idxmax()+1})")
print(f"  최저 Reward: {completed_episodes['Reward'].min():.2f}")
print(f"  평균 Served Demand: {completed_episodes['Served_Demand'].mean():.2f}")
print(f"  평균 Rebalancing Cost: {completed_episodes['Rebalancing_Cost'].mean():.2f}")

# Cost/Demand 비율
completed_episodes['Cost_Ratio'] = completed_episodes['Rebalancing_Cost'] / completed_episodes['Served_Demand']
print(f"  평균 Cost/Demand Ratio: {completed_episodes['Cost_Ratio'].mean():.3f}")

# 학습 추세 (완료된 에피소드만)
first_half = completed_episodes.iloc[:len(completed_episodes)//2]
second_half = completed_episodes.iloc[len(completed_episodes)//2:]

print(f"\n📊 학습 진행 (완료 에피소드 기준):")
print(f"  전반부 평균 Reward: {first_half['Reward'].mean():.2f}")
print(f"  후반부 평균 Reward: {second_half['Reward'].mean():.2f}")
print(f"  개선도: {second_half['Reward'].mean() - first_half['Reward'].mean():.2f}")

# 양수 Reward 에피소드
positive_rewards = completed_episodes[completed_episodes['Reward'] > 0]
print(f"\n✅ 양수 Reward 에피소드: {len(positive_rewards)}개")
if len(positive_rewards) > 0:
    print(f"  Episode 번호: {list(positive_rewards.index + 1)}")
    print(f"  평균 Reward: {positive_rewards['Reward'].mean():.2f}")

# 시각화
fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle('SAC Training Analysis (155 Episodes)', fontsize=16, fontweight='bold')

# 1. Reward (전체)
ax1 = axes[0, 0]
ax1.scatter(df.index + 1, df['Reward'], c=['red' if x < 301 else 'blue' for x in df['Steps_Completed']], 
            alpha=0.5, s=30)
# 완료 에피소드만 moving average
window = 10
completed_idx = completed_episodes.index
completed_ma = completed_episodes['Reward'].rolling(window=window, min_periods=1).mean()
ax1.plot(completed_idx + 1, completed_ma, 'g-', linewidth=2, label=f'완료 에피소드 MA({window})')
ax1.axhline(y=0, color='k', linestyle='--', alpha=0.3)
ax1.set_xlabel('Episode')
ax1.set_ylabel('Reward')
ax1.set_title('Episode Reward (Blue=완료, Red=크래시)')
ax1.legend()
ax1.grid(True, alpha=0.3)

# 2. Cost/Demand Ratio (완료만)
ax2 = axes[0, 1]
ax2.scatter(completed_episodes.index + 1, completed_episodes['Cost_Ratio'], 
            alpha=0.6, s=30, c='blue')
ratio_ma = completed_episodes['Cost_Ratio'].rolling(window=window, min_periods=1).mean()
ax2.plot(completed_idx + 1, ratio_ma, 'g-', linewidth=2, label=f'MA({window})')
ax2.axhline(y=1.0, color='r', linestyle='--', alpha=0.5, label='Break-even')
ax2.set_xlabel('Episode')
ax2.set_ylabel('Cost / Demand Ratio')
ax2.set_title('Efficiency (완료 에피소드만)')
ax2.legend()
ax2.grid(True, alpha=0.3)

# 3. Steps Completed Distribution
ax3 = axes[1, 0]
bins = [0, 50, 100, 150, 200, 250, 301]
ax3.hist(df['Steps_Completed'], bins=bins, edgecolor='black', alpha=0.7)
ax3.axvline(x=301, color='g', linestyle='--', linewidth=2, label='Target (301)')
ax3.set_xlabel('Steps Completed')
ax3.set_ylabel('Frequency')
ax3.set_title('Episode Length Distribution')
ax3.legend()
ax3.grid(True, alpha=0.3, axis='y')

# 4. 완료 vs 크래시 Reward 비교
ax4 = axes[1, 1]
data_to_plot = [completed_episodes['Reward'], crashed_episodes['Reward']]
labels = [f'완료\n(n={len(completed_episodes)})', f'크래시\n(n={len(crashed_episodes)})']
bp = ax4.boxplot(data_to_plot, labels=labels, patch_artist=True)
bp['boxes'][0].set_facecolor('lightblue')
bp['boxes'][1].set_facecolor('lightcoral')
ax4.axhline(y=0, color='k', linestyle='--', alpha=0.3)
ax4.set_ylabel('Reward')
ax4.set_title('Reward Distribution by Episode Type')
ax4.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
output_file = "saved_files/training_logs/detailed_analysis.png"
plt.savefig(output_file, dpi=150, bbox_inches='tight')
print(f"\n✅ 상세 분석 그래프 저장: {output_file}")

# 개선 추세 분석
print("\n" + "=" * 80)
print("🎯 학습 품질 평가")
print("=" * 80)

# 완료 에피소드만으로 추세 분석
if len(completed_episodes) >= 20:
    first_20 = completed_episodes.iloc[:20]
    last_20 = completed_episodes.iloc[-20:]
    
    print(f"\n초기 20개 완료 에피소드:")
    print(f"  평균 Reward: {first_20['Reward'].mean():.2f}")
    print(f"  평균 Cost/Demand: {first_20['Cost_Ratio'].mean():.3f}")
    
    print(f"\n최근 20개 완료 에피소드:")
    print(f"  평균 Reward: {last_20['Reward'].mean():.2f}")
    print(f"  평균 Cost/Demand: {last_20['Cost_Ratio'].mean():.3f}")
    
    reward_improvement = last_20['Reward'].mean() - first_20['Reward'].mean()
    ratio_improvement = first_20['Cost_Ratio'].mean() - last_20['Cost_Ratio'].mean()
    
    print(f"\n개선도:")
    print(f"  Reward: {reward_improvement:+.2f}")
    print(f"  Cost/Demand 감소: {ratio_improvement:+.3f}")

print("\n" + "=" * 80)
print("💡 진단 및 권장사항")
print("=" * 80)

crash_rate = len(crashed_episodes) / len(df)
avg_reward_completed = completed_episodes['Reward'].mean()
avg_ratio = completed_episodes['Cost_Ratio'].mean()

print(f"\n현재 상태:")
if crash_rate > 0.4:
    print(f"  ❌ 크래시율: {crash_rate*100:.1f}% (매우 높음)")
elif crash_rate > 0.2:
    print(f"  ⚠️ 크래시율: {crash_rate*100:.1f}% (높음)")
else:
    print(f"  ✅ 크래시율: {crash_rate*100:.1f}% (양호)")

if avg_reward_completed > 0:
    print(f"  ✅ 평균 Reward: {avg_reward_completed:.2f} (양수)")
elif avg_reward_completed > -5000:
    print(f"  ⚠️ 평균 Reward: {avg_reward_completed:.2f} (약간 음수)")
else:
    print(f"  ❌ 평균 Reward: {avg_reward_completed:.2f} (큰 음수)")

if avg_ratio < 1.0:
    print(f"  ✅ Cost/Demand: {avg_ratio:.3f} (효율적)")
elif avg_ratio < 1.1:
    print(f"  ⚠️ Cost/Demand: {avg_ratio:.3f} (보통)")
else:
    print(f"  ❌ Cost/Demand: {avg_ratio:.3f} (비효율적)")

print("\n권장 조치:")
if crash_rate > 0.3:
    print("  1. 🔧 시뮬레이션 시간 단축 (duration=3 또는 2)")
    print("  2. 🔧 택시 수 감소 (acc_init=60-70)")
    print("  3. 🔧 time_start=6 또는 7로 변경")

if len(positive_rewards) > 0:
    print(f"  4. ✅ 학습이 진행 중입니다! ({len(positive_rewards)}개 양수 에피소드)")
    print("  5. 💡 더 많은 에피소드 학습 권장 (200-300)")
else:
    print("  4. ⚠️ 하이퍼파라미터 조정 필요")
    print("     - beta 증가 (재배치 비용 완화)")
    print("     - learning rate 조정")

print("\n" + "=" * 80)
