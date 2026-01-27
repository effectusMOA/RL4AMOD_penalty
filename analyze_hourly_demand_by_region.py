"""
시간대별/존별 택시 수요 분석
Luxembourg 8개 지역의 시간대별 이동 수요 패턴 분석
"""
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 데이터 로드
with open('src/envs/data/scenario_lux8.json', 'r') as f:
    data = json.load(f)

print("=" * 80)
print("Luxembourg 택시 수요 - 시간대별/존별 분석")
print("=" * 80)

# 기본 정보
num_regions = 8
demand_data = data['demand']
print(f"\n총 지역 수: {num_regions}")
print(f"데이터 시간 범위: 0-23시 (24시간)")

# ========== 1. 시간대별 각 존의 총 Outbound 수요 (출발) ==========
print("\n" + "=" * 80)
print("1. 시간대별 각 존의 총 출발 수요 (Outbound Demand)")
print("=" * 80)

# 시간대별, origin별 수요 집계
hourly_origin_demand = np.zeros((24, num_regions))

for hour in range(24):
    hour_data = demand_data[hour]
    for key, value in hour_data.items():
        if ',' in key:
            o, d = map(int, key.split(','))
            hourly_origin_demand[hour, o] += value

# DataFrame 생성
df_origin = pd.DataFrame(
    hourly_origin_demand,
    columns=[f'Region {i}' for i in range(num_regions)],
    index=[f'{h:02d}:00' for h in range(24)]
)

print("\n시간대별 각 존 출발 수요:")
print(df_origin.to_string())

# ========== 2. 시간대별 각 존의 총 Inbound 수요 (도착) ==========
print("\n" + "=" * 80)
print("2. 시간대별 각 존의 총 도착 수요 (Inbound Demand)")
print("=" * 80)

# 시간대별, destination별 수요 집계
hourly_dest_demand = np.zeros((24, num_regions))

for hour in range(24):
    hour_data = demand_data[hour]
    for key, value in hour_data.items():
        if ',' in key:
            o, d = map(int, key.split(','))
            hourly_dest_demand[hour, d] += value

# DataFrame 생성
df_dest = pd.DataFrame(
    hourly_dest_demand,
    columns=[f'Region {i}' for i in range(num_regions)],
    index=[f'{h:02d}:00' for h in range(24)]
)

print("\n시간대별 각 존 도착 수요:")
print(df_dest.to_string())

# ========== 3. 통계 요약 ==========
print("\n" + "=" * 80)
print("3. 존별 수요 통계")
print("=" * 80)

print("\n각 존의 일일 총 수요 (출발 기준):")
for i in range(num_regions):
    total = df_origin[f'Region {i}'].sum()
    peak_hour = df_origin[f'Region {i}'].idxmax()
    peak_value = df_origin[f'Region {i}'].max()
    print(f"  Region {i}: {total:>8.0f}명 (피크: {peak_hour} - {peak_value:.0f}명)")

print("\n각 존의 Net Flow (도착 - 출발):")
for i in range(num_regions):
    net_flow = df_dest[f'Region {i}'].sum() - df_origin[f'Region {i}'].sum()
    flow_type = "유입 우세" if net_flow > 0 else "유출 우세"
    print(f"  Region {i}: {net_flow:>8.0f}명 ({flow_type})")

# ========== 4. OD Matrix by Hour ==========
print("\n" + "=" * 80)
print("4. 대표 시간대 OD Matrix")
print("=" * 80)

# 피크 시간대 OD matrix
peak_hours = [7, 12, 17]  # 출근, 점심, 퇴근

for hour in peak_hours:
    print(f"\n{hour:02d}:00 시 OD Matrix:")
    od_matrix = np.zeros((num_regions, num_regions))
    hour_data = demand_data[hour]
    
    for key, value in hour_data.items():
        if ',' in key:
            o, d = map(int, key.split(','))
            od_matrix[o, d] = value
    
    df_od = pd.DataFrame(
        od_matrix,
        columns=[f'D{i}' for i in range(num_regions)],
        index=[f'O{i}' for i in range(num_regions)]
    )
    print(df_od.to_string())

# ========== 5. 시각화 ==========
print("\n" + "=" * 80)
print("5. 시각화 생성 중...")
print("=" * 80)

fig, axes = plt.subplots(3, 2, figsize=(16, 14))
fig.suptitle('Luxembourg 택시 수요 분석 (시간대별/존별)', fontsize=16, fontweight='bold')

# 1. 출발 수요 (Heatmap)
ax1 = axes[0, 0]
sns.heatmap(hourly_origin_demand.T, 
            xticklabels=[f'{h:02d}' for h in range(24)],
            yticklabels=[f'R{i}' for i in range(num_regions)],
            cmap='YlOrRd', ax=ax1, cbar_kws={'label': '수요 (명)'})
ax1.set_title('출발 수요 (Outbound) - Heatmap')
ax1.set_xlabel('시간 (Hour)')
ax1.set_ylabel('지역 (Region)')

# 2. 도착 수요 (Heatmap)
ax2 = axes[0, 1]
sns.heatmap(hourly_dest_demand.T,
            xticklabels=[f'{h:02d}' for h in range(24)],
            yticklabels=[f'R{i}' for i in range(num_regions)],
            cmap='YlGnBu', ax=ax2, cbar_kws={'label': '수요 (명)'})
ax2.set_title('도착 수요 (Inbound) - Heatmap')
ax2.set_xlabel('시간 (Hour)')
ax2.set_ylabel('지역 (Region)')

# 3. 출발 수요 (Line Plot)
ax3 = axes[1, 0]
for i in range(num_regions):
    ax3.plot(range(24), hourly_origin_demand[:, i], 
             marker='o', label=f'Region {i}', linewidth=2)
ax3.set_title('시간대별 출발 수요 추이')
ax3.set_xlabel('시간 (Hour)')
ax3.set_ylabel('수요 (명)')
ax3.legend(loc='upper right', fontsize=8)
ax3.grid(True, alpha=0.3)
ax3.set_xticks(range(0, 24, 2))

# 4. 전체 수요 (Stacked Area)
ax4 = axes[1, 1]
ax4.stackplot(range(24), *[hourly_origin_demand[:, i] for i in range(num_regions)],
              labels=[f'R{i}' for i in range(num_regions)],
              alpha=0.7)
ax4.set_title('시간대별 총 출발 수요 (누적)')
ax4.set_xlabel('시간 (Hour)')
ax4.set_ylabel('누적 수요 (명)')
ax4.legend(loc='upper left', fontsize=8)
ax4.grid(True, alpha=0.3)
ax4.set_xticks(range(0, 24, 2))

# 5. 존별 일일 총 수요 (Bar)
ax5 = axes[2, 0]
daily_totals = df_origin.sum().values
ax5.bar(range(num_regions), daily_totals, color='steelblue', alpha=0.7)
ax5.set_title('존별 일일 총 출발 수요')
ax5.set_xlabel('지역 (Region)')
ax5.set_ylabel('일일 총 수요 (명)')
ax5.set_xticks(range(num_regions))
ax5.set_xticklabels([f'R{i}' for i in range(num_regions)])
ax5.grid(True, alpha=0.3, axis='y')

# 6. Net Flow (Bar)
ax6 = axes[2, 1]
net_flows = df_dest.sum().values - df_origin.sum().values
colors = ['green' if x > 0 else 'red' for x in net_flows]
ax6.bar(range(num_regions), net_flows, color=colors, alpha=0.7)
ax6.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
ax6.set_title('존별 Net Flow (도착 - 출발)')
ax6.set_xlabel('지역 (Region)')
ax6.set_ylabel('Net Flow (명)')
ax6.set_xticks(range(num_regions))
ax6.set_xticklabels([f'R{i}' for i in range(num_regions)])
ax6.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
output_file = 'saved_files/demand_analysis_hourly_by_region.png'
plt.savefig(output_file, dpi=150, bbox_inches='tight')
print(f"✅ 그래프 저장: {output_file}")

# ========== 6. CSV 저장 ==========
print("\n" + "=" * 80)
print("6. 데이터 CSV 저장")
print("=" * 80)

# 출발 수요
outbound_file = 'saved_files/demand_outbound_hourly.csv'
df_origin.to_csv(outbound_file)
print(f"✅ 출발 수요 저장: {outbound_file}")

# 도착 수요
inbound_file = 'saved_files/demand_inbound_hourly.csv'
df_dest.to_csv(inbound_file)
print(f"✅ 도착 수요 저장: {inbound_file}")

# 통계 요약
summary_file = 'saved_files/demand_summary.txt'
with open(summary_file, 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("Luxembourg 택시 수요 통계 요약\n")
    f.write("=" * 80 + "\n\n")
    
    f.write("존별 일일 총 수요 (출발 기준):\n")
    for i in range(num_regions):
        total = df_origin[f'Region {i}'].sum()
        peak_hour = df_origin[f'Region {i}'].idxmax()
        peak_value = df_origin[f'Region {i}'].max()
        f.write(f"  Region {i}: {total:>8.0f}명 (피크: {peak_hour} - {peak_value:.0f}명)\n")
    
    f.write("\n존별 Net Flow (도착 - 출발):\n")
    for i in range(num_regions):
        net_flow = net_flows[i]
        flow_type = "유입 우세" if net_flow > 0 else "유출 우세"
        f.write(f"  Region {i}: {net_flow:>8.0f}명 ({flow_type})\n")
    
    f.write("\n일일 총 수요: {:.0f}명\n".format(df_origin.sum().sum()))
    f.write("=" * 80 + "\n")

print(f"✅ 통계 요약 저장: {summary_file}")

print("\n" + "=" * 80)
print("분석 완료!")
print("=" * 80)
