
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
    
    # Calculate Trip Margin (Served - Cost would be incorrect; Served IS the margin already in this data)
    # In this context: Served = Trip Margin (p-c)*x, Reward = Profit = Served - RebCost
    df['TripMargin'] = df['Served']  # Served Demand is actually Trip Margin in our formulation
    
    # Calculate Efficiency (Flow/Cost) - Higher is better
    df['Efficiency'] = df.apply(lambda x: x['RebFlow'] / x['Cost'] if x['Cost'] > 0 else 0, axis=1)

    # Separate Hard from numerical Lambdas for plotting
    df_soft = df[df['Label'] != 'Hard'].copy()
    if not df[df['Label'] == 'Hard'].empty:
        df_hard = df[df['Label'] == 'Hard'].iloc[0]
    else:
        print("WARNING: Hard baseline not found!")
        df_hard = df_soft.iloc[0]

    # Plotting: 3 subplots for clarity
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    
    # =============================================
    # Plot (a): Profit, Trip Margin, Rebalancing Cost
    # =============================================
    ax1 = axes[0]
    
    # Primary Y-axis: Reward & Trip Margin (similar scale)
    ln1 = ax1.plot(df_soft['Lambda_Val'], df_soft['Reward'], 'b-o', linewidth=2, markersize=8, label='Profit')
    ln2 = ax1.plot(df_soft['Lambda_Val'], df_soft['TripMargin'], 'g-s', linewidth=2, markersize=8, label='Trip Margin')
    ax1.axhline(y=df_hard['Reward'], color='b', linestyle='--', alpha=0.4)
    ax1.axhline(y=df_hard['TripMargin'], color='g', linestyle='--', alpha=0.4)
    ax1.set_xlabel('Lambda', fontsize=12)
    ax1.set_ylabel('Revenue / Profit ($)', fontsize=12, color='b')
    ax1.tick_params(axis='y', labelcolor='b')
    ax1.grid(True, alpha=0.3)
    
    # Secondary Y-axis: Rebalancing Cost
    ax1b = ax1.twinx()
    ln3 = ax1b.plot(df_soft['Lambda_Val'], df_soft['Cost'], 'r-^', linewidth=2, markersize=8, label='Reb. Cost')
    ax1b.axhline(y=df_hard['Cost'], color='r', linestyle='--', alpha=0.4)
    ax1b.set_ylabel('Rebalancing Cost ($)', fontsize=12, color='r')
    ax1b.tick_params(axis='y', labelcolor='r')
    
    lns = ln1 + ln2 + ln3
    labs = [l.get_label() for l in lns]
    ax1.legend(lns, labs, loc='best', fontsize=10)
    ax1.set_title('(a) Profit, Trip Margin & Reb. Cost', fontsize=13)
    
    # =============================================
    # Plot (b): Rebalancing Cost & Flow
    # =============================================
    ax2 = axes[1]
    
    ln4 = ax2.plot(df_soft['Lambda_Val'], df_soft['Cost'], 'r-o', linewidth=2, markersize=8, label='Reb. Cost ($)')
    ax2.axhline(y=df_hard['Cost'], color='r', linestyle='--', alpha=0.4)
    ax2.set_xlabel('Lambda', fontsize=12)
    ax2.set_ylabel('Rebalancing Cost ($)', fontsize=12, color='r')
    ax2.tick_params(axis='y', labelcolor='r')
    ax2.grid(True, alpha=0.3)
    
    ax2b = ax2.twinx()
    ln5 = ax2b.plot(df_soft['Lambda_Val'], df_soft['RebFlow'], 'm-s', linewidth=2, markersize=8, label='Reb. Flow (veh)')
    ax2b.axhline(y=df_hard['RebFlow'], color='m', linestyle='--', alpha=0.4)
    ax2b.set_ylabel('Rebalancing Flow (veh)', fontsize=12, color='m')
    ax2b.tick_params(axis='y', labelcolor='m')
    
    lns = ln4 + ln5
    labs = [l.get_label() for l in lns]
    ax2.legend(lns, labs, loc='best', fontsize=10)
    ax2.set_title('(b) Rebalancing Cost & Flow', fontsize=13)
    
    # =============================================
    # Plot (c): Efficiency (standalone)
    # =============================================
    ax3 = axes[2]
    
    ax3.plot(df_soft['Lambda_Val'], df_soft['Efficiency'], 'k-D', linewidth=2, markersize=8, label='Efficiency (veh/$)')
    ax3.axhline(y=df_hard['Efficiency'], color='k', linestyle='--', alpha=0.5, label='Hard Baseline')
    ax3.set_xlabel('Lambda', fontsize=12)
    ax3.set_ylabel('Efficiency (veh/$)', fontsize=12)
    ax3.grid(True, alpha=0.3)
    ax3.legend(loc='best', fontsize=10)
    ax3.set_title('(c) Efficiency: Flow / Cost\n(Higher = Better)', fontsize=13)

    plt.suptitle('Figure 3: Lambda Sensitivity Analysis', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    out_path = 'figures/figure3.png'
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    print(f"✅ Saved figure to {out_path}")

if __name__ == "__main__":
    main()

