
import json
import matplotlib.pyplot as plt
import glob
import re
import pandas as pd
import numpy as np

def load_results(filepath):
    import os
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data

def main():
    # 1. Load Data
    pattern = "saved_files/SAC_SoftLP_lam*_nyc_od_flows.json"
    soft_files = glob.glob(pattern)
    hard_file = "saved_files/SAC_HardLP_nyc_od_flows.json"
    
    results = []
    
    # Hard SAC (Baseline)
    hard_data = load_results(hard_file)
    if hard_data:
        results.append({
            "Lambda_Val": 999, # Placeholder for sorting, will serve as 'Hard'
            "Label": "Hard",
            "Reward": hard_data['mean_reward'],
            "Served": hard_data['mean_served_demand'],
            "Cost": hard_data['mean_rebalancing_cost'],
            "RebFlow": hard_data.get('total_rebalancing_vehicles', 0),
        })

    print(f"DEBUG: Found {len(soft_files)} soft files.")
    for f in soft_files:
        print(f" - {f}")

    # Soft SAC
    for fpath in soft_files:
        match = re.search(r'lam([\d.]+)_', fpath)
        if match:
            lam_val = float(match.group(1))
            data = load_results(fpath)
            if data:
                results.append({
                    "Lambda_Val": lam_val,
                    "Label": str(lam_val),
                    "Reward": data.get('mean_reward', 0),
                    "Served": data.get('mean_served_demand', 0),
                    "Cost": data.get('mean_rebalancing_cost', 0),
                    "RebFlow": data.get('total_rebalancing_vehicles', 0),
                })
        else:
             print(f"DEBUG: No regex match for {fpath}")
    
    df = pd.DataFrame(results)
    df = df.sort_values(by="Lambda_Val")
    
    print("\nDEBUG: DataFrame content:")
    print(df[['Label', 'Lambda_Val', 'Reward', 'Cost']])
    
    # Calculate Efficiency ($/veh)
    df['AvgCostPerVeh'] = df.apply(lambda x: x['Cost'] / x['RebFlow'] if x['RebFlow'] > 0 else 0, axis=1)

    # Separate Hard from numerical Lambdas for plotting
    df_soft = df[df['Label'] != 'Hard'].copy()
    if not df[df['Label'] == 'Hard'].empty:
        df_hard = df[df['Label'] == 'Hard'].iloc[0]
    else:
        print("WARNING: Hard baseline not found!")
        df_hard = df_soft.iloc[0] # Fallback to avoid crash

    # Plotting
    fig, axes = plt.subplots(1, 3, figsize=(24, 6))
    
    # Plot 1: Reward (Left) & Served Demand (Right)
    ax1 = axes[0]
    lns1 = ax1.plot(df_soft['Lambda_Val'], df_soft['Reward'], 'b-o', label='Reward ($)')
    ax1.axhline(y=df_hard['Reward'], color='b', linestyle='--', alpha=0.5, label='Hard Reward')
    ax1.set_xlabel('Lambda')
    ax1.set_ylabel('Reward ($)', color='b')
    ax1.tick_params(axis='y', labelcolor='b')
    ax1.grid(True, alpha=0.3)

    ax2 = ax1.twinx()
    lns2 = ax2.plot(df_soft['Lambda_Val'], df_soft['Served'], 'g-s', label='Served Demand')
    ax2.axhline(y=df_hard['Served'], color='g', linestyle='--', alpha=0.5, label='Hard Served')
    ax2.set_ylabel('Served Demand', color='g')
    ax2.tick_params(axis='y', labelcolor='g')

    # Legend
    lns = lns1 + lns2
    labs = [l.get_label() for l in lns]
    ax1.legend(lns, labs, loc='center right')
    ax1.set_title('Reward & Served Demand vs Lambda')

    # Plot 2: Reb Cost (Left) & Reb Flow (Right)
    ax3 = axes[1]
    lns3 = ax3.plot(df_soft['Lambda_Val'], df_soft['Cost'], 'r-o', label='Reb. Cost ($)')
    ax3.axhline(y=df_hard['Cost'], color='r', linestyle='--', alpha=0.5, label='Hard Cost')
    ax3.set_xlabel('Lambda')
    ax3.set_ylabel('Rebalancing Cost ($)', color='r')
    ax3.tick_params(axis='y', labelcolor='r')
    ax3.grid(True, alpha=0.3)

    ax4 = ax3.twinx()
    lns4 = ax4.plot(df_soft['Lambda_Val'], df_soft['RebFlow'], 'm-s', label='Reb. Flow (veh)')
    ax4.axhline(y=df_hard['RebFlow'], color='m', linestyle='--', alpha=0.5, label='Hard Flow')
    ax4.set_ylabel('Rebalancing Flow (veh)', color='m')
    ax4.tick_params(axis='y', labelcolor='m')

    # Legend
    lns = lns3 + lns4
    labs = [l.get_label() for l in lns]
    ax3.legend(lns, labs, loc='center right')
    ax3.set_title('Rebalancing Cost & Flow vs Lambda')

    # Plot 3: Avg Cost per Vehicle (Efficiency)
    ax5 = axes[2]
    lns5 = ax5.plot(df_soft['Lambda_Val'], df_soft['AvgCostPerVeh'], 'k-D', label='Avg Cost ($/veh)')
    ax5.axhline(y=df_hard['AvgCostPerVeh'], color='k', linestyle='--', alpha=0.5, label='Hard Efficiency')
    ax5.set_xlabel('Lambda')
    ax5.set_ylabel('Avg Reb. Cost per Vehicle ($)', color='k')
    ax5.tick_params(axis='y', labelcolor='k')
    ax5.grid(True, alpha=0.3)
    ax5.legend(loc='upper right')
    ax5.set_title('Efficiency: Avg Cost per Rebalancing Vehicle\n(Lower is Better)')

    plt.suptitle('Figure 3: Lambda Sensitivity Analysis', fontsize=16)
    plt.tight_layout()
    
    out_path = 'figures/figure3.png'
    plt.savefig(out_path, dpi=300)
    print(f"✅ Saved figure to {out_path}")

if __name__ == "__main__":
    main()
