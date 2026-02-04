"""
Lambda 변형 모델 비교 - CSV만 사용
"""

import os
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

CHECKPOINTS = {
    "HARD": "ckpt/SAC_HardLP_nyc_t7-12h_ep10000_20260127_193946",
    "lam3": "ckpt/SAC_SoftLP_lam3_nyc_t7-12h_ep10000_20260202_155553",
    "lam4": "ckpt/SAC_SoftLP_lam4_nyc_t7-12h_ep10000_20260202_155549",
    "lam4.5": "ckpt/SAC_SoftLP_lam4.5_nyc_t7-12h_ep10000_20260202_155852",
    "lam5": "ckpt/SAC_SoftLP_lam5_nyc_t7-12h_ep10000_20260127_194646",
    "lam6": "ckpt/SAC_SoftLP_lam6_nyc_t7-12h_ep10000_20260202_155650",
}

def load_csv(path):
    log_path = os.path.join(path, "training_log.csv")
    if not os.path.exists(log_path):
        return None
    data = {"reward": [], "served_demand": [], "rebalancing_cost": []}
    with open(log_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data["reward"].append(float(row["reward"]))
            data["served_demand"].append(float(row["served_demand"]))
            data["rebalancing_cost"].append(float(row["rebalancing_cost"]))
    return data

def main():
    print("=" * 60)
    print("Lambda Comparison")
    print("=" * 60)
    
    logs = {}
    for label, path in CHECKPOINTS.items():
        data = load_csv(path)
        if data:
            logs[label] = data
            print(f"OK {label}: {len(data['reward'])} episodes")
        else:
            print(f"NOT FOUND: {label}")
    
    if not logs:
        print("No data!")
        return
    
    print("\n" + "=" * 80)
    print("Final Performance (Last 500 episodes avg)")
    print("=" * 80)
    print(f"{'Model':<12} {'Reward':>12} {'ServedDemand':>14} {'RebCost':>12}")
    print("-" * 80)
    
    results = []
    for label, data in logs.items():
        n = min(500, len(data["reward"]))
        reward = sum(data["reward"][-n:]) / n
        served = sum(data["served_demand"][-n:]) / n
        reb = sum(data["rebalancing_cost"][-n:]) / n
        print(f"{label:<12} {reward:>12.1f} {served:>14.1f} {reb:>12.1f}")
        results.append((label, reward, served, reb))
    
    # Plot - 3 bars per model
    fig, ax = plt.subplots(figsize=(14, 7))
    
    labels = [r[0] for r in results]
    rewards = [r[1] for r in results]
    served = [r[2] for r in results]
    reb_costs = [r[3] for r in results]
    
    x = list(range(len(labels)))
    width = 0.25
    
    bars1 = ax.bar([i - width for i in x], rewards, width, label='Reward', color='#3498DB')
    bars2 = ax.bar([i for i in x], served, width, label='Served Demand', color='#2ECC71')
    bars3 = ax.bar([i + width for i in x], reb_costs, width, label='Reb Cost', color='#E74C3C')
    
    ax.set_xlabel("Model")
    ax.set_ylabel("Value ($)")
    ax.set_title("Lambda Comparison: Final Performance")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig("figures/lambda_comparison.png", dpi=300)
    print(f"\nSaved: figures/lambda_comparison.png")
    plt.close()
    
    print("Done!")

if __name__ == "__main__":
    main()
