"""
Lambda 변형 모델 Test 결과 비교 (OD Flow JSON 기반)
- HARD, λ=3, 4, 4.5, 5, 6, 7, 8, 9, 10 총 10가지 모델 비교
- saved_files/{checkpoin_name}_od_flows.json 파일에서 메트릭 로드
"""

import os
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# 체크포인트 이름 목록 (lambda 오름차순)
FILES = [
    ("λ=3", "SAC_SoftLP_lam3_nyc_od_flows.json"),
    ("λ=4", "SAC_SoftLP_lam4_nyc_od_flows.json"),
    ("λ=5", "SAC_SoftLP_lam5_nyc_od_flows.json"),
    ("λ=6", "SAC_SoftLP_lam6_nyc_od_flows.json"),
    ("λ=7", "SAC_SoftLP_lam7_nyc_od_flows.json"),
    ("λ=8", "SAC_SoftLP_lam8_nyc_od_flows.json"),
    ("λ=9", "SAC_SoftLP_lam9_nyc_od_flows.json"),
    ("λ=10", "SAC_SoftLP_lam10_nyc_od_flows.json"),
    ("HARD", "SAC_HardLP_nyc_od_flows.json")
]

def load_json(filename):
    path = os.path.join("saved_files", filename)
    if not os.path.exists(path):
        return None
    with open(path, 'r') as f:
        return json.load(f)

def main():
    print("=" * 80)
    print("Lambda Test Result Comparison")
    print("=" * 80)
    
    results = []
    
    # 데이터 로드
    for label, filename in FILES:
        data = load_json(filename)
        if data:
            print(f"✅ {label:<6} loaded")
            results.append({
                "Label": label,
                "Reward": data.get("mean_reward", 0),
                "Served": data.get("mean_served_demand", 0),
                "RebCost": data.get("mean_rebalancing_cost", 0)
            })
        else:
            print(f"❌ {label:<6} file not found: {filename}")
    
    if not results:
        print("No data found!")
        return

    # 테이블 출력
    print("\n" + "=" * 80)
    print(f"{'Model':<10} {'Reward':>12} {'ServedDemand':>14} {'RebCost':>12} {'Reb/Reward':>12}")
    print("-" * 80)
    
    for r in results:
        ratio = (r["RebCost"] / r["Reward"] * 100) if r["Reward"] > 0 else 0
        print(f"{r['Label']:<10} {r['Reward']:>12.1f} {r['Served']:>14.1f} {r['RebCost']:>12.1f} {ratio:>11.1f}%")
    print("=" * 80)
    
    # 그래프 그리기
    labels = [r["Label"] for r in results]
    rewards = [r["Reward"] for r in results]
    served = [r["Served"] for r in results]
    reb_costs = [r["RebCost"] for r in results]
    
    x = np.arange(len(labels))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(16, 8))
    
    # 막대 순서: Reward(좌, 파랑), Served(중, 초록), RebCost(우, 빨강)
    rects1 = ax.bar(x - width, rewards, width, label='Reward', color='#3498DB')
    rects2 = ax.bar(x, served, width, label='Served Demand', color='#2ECC71')
    rects3 = ax.bar(x + width, reb_costs, width, label='Reb Cost', color='#E74C3C')
    
    ax.set_ylabel('Value ($)')
    ax.set_title('Test Performance Comparison across Lambda Variants')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    ax.grid(True, axis='y', alpha=0.3)
    
    # 값 표시 함수
    def autolabel(rects, fontsize=8):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height/1000:.1f}k',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=fontsize)

    autolabel(rects1)
    autolabel(rects2)
    autolabel(rects3)

    plt.tight_layout()
    output_path = "figures/lambda_test_comparison.png"
    plt.savefig(output_path, dpi=300)
    print(f"\nSaved graph to {output_path}")
    plt.close()

if __name__ == "__main__":
    main()
