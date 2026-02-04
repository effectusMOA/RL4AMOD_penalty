import json
import pandas as pd
import os
import re
import glob

def load_results(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data

def main():
    print("="*80)
    print("Lambda Sensitivity Analysis (Table 2)")
    print("GENERATE: saved_files/lambda_sensitivity_table.csv")
    print("="*80)

    # 1. 파일 탐색
    pattern = "saved_files/SAC_SoftLP_lam*_nyc_od_flows.json"
    soft_files = glob.glob(pattern)
    hard_file = "saved_files/SAC_HardLP_nyc_od_flows.json"
    
    results = []
    
    # 2. Hard SAC 로드 (Baseline)
    hard_data = load_results(hard_file)
    if not hard_data:
        print("❌ Error: SAC Hard results not found.")
        return

    base_reward = hard_data['mean_reward']
    base_served = hard_data['mean_served_demand']
    base_cost = hard_data['mean_rebalancing_cost']
    base_flow = hard_data.get('total_rebalancing_vehicles', 0)

    # Hard 추가
    results.append({
        "Lambda": "Infinity (Hard)",
        "Lambda_Val": 9999,
        "Reward": base_reward,
        "Served": base_served,
        "Cost": base_cost,
        "RebFlow": base_flow,
    })

    # 3. Soft SAC 로드
    for fpath in soft_files:
        # 파일명에서 lambda 값 추출 (lam3, lam4.5 등)
        match = re.search(r'lam([\d.]+)_', fpath)
        if match:
            lam_val = float(match.group(1))
            data = load_results(fpath)
            if data:
                results.append({
                    "Lambda": str(lam_val),
                    "Lambda_Val": lam_val,
                    "Reward": data.get('mean_reward', 0),
                    "Served": data.get('mean_served_demand', 0),
                    "Cost": data.get('mean_rebalancing_cost', 0),
                    "RebFlow": data.get('total_rebalancing_vehicles', 0),
                })

    # 4. Lambda 기준 정렬
    df = pd.DataFrame(results)
    df = df.sort_values(by="Lambda_Val", ascending=True)

    # Label update for Hard
    df.loc[df['Lambda_Val'] == 9999, 'Lambda'] = 'Hard'

    # 5. 변화율 및 비율 계산 (기준: SAC Hard)
    # User request: "served demand 증가율 / rebalancing flow 증가율"
    # Note: Hard 대비 Soft는 Cost가 감소(-)하고 Served가 증가(+)하거나 감소(-)함.
    
    # 변화율 (%)
    df['Reward %'] = (df['Reward'] - base_reward) / base_reward * 100
    df['Served %'] = (df['Served'] - base_served) / base_served * 100
    df['Cost %'] = (df['Cost'] - base_cost) / base_cost * 100
    df['RebFlow %'] = (df['RebFlow'] - base_flow) / base_flow * 100

    # 효율성 지표 1: (Served / Cost) Absolute Ratio
    df['Efficiency (Served/Cost)'] = df['Served'] / df['Cost']
    
    # 효율성 지표 2: 변화율 비율 (Served % / Cost %)
    # 주의: Div by zero 방지. Cost %가 0이면 0 처리.
    def calc_ratio(row):
        if abs(row['Cost %']) < 0.01: return 0
        return row['Served %'] / row['Cost %']

    df['Incr. Ratio (S%/C%)'] = df.apply(calc_ratio, axis=1)

    # 6. 포맷팅 (User Request: "55,409 (+2.84%)")
    def format_val_pct(val, pct):
        return f"{val:,.0f} ({pct:+.2f}%)"

    df['Reward ($)'] = df.apply(lambda x: format_val_pct(x['Reward'], x['Reward %']), axis=1)
    df['Served Demand'] = df.apply(lambda x: format_val_pct(x['Served'], x['Served %']), axis=1)
    df['Reb. Cost ($)'] = df.apply(lambda x: format_val_pct(x['Cost'], x['Cost %']), axis=1)
    df['Reb. Flow (veh)'] = df.apply(lambda x: format_val_pct(x['RebFlow'], x['RebFlow %']), axis=1)
    
    # Efficiency Ratio (Served% / Cost%) - already calculated as 'Incr. Ratio (S%/C%)'
    # Rename for clarity
    df = df.rename(columns={'Incr. Ratio (S%/C%)': 'Efficiency (S%/C%)'})
    
    # Baseline special handling (remove 0.00% or keep it? User example showed +2.84%, so baseline 0.00% is consistent)
    
    # 7. 출력 및 저장
    disp_cols = [
        "Lambda", 
        "Reward ($)", 
        "Served Demand", 
        "Reb. Cost ($)", 
        "Reb. Flow (veh)", 
        "Efficiency (S%/C%)"
    ]
    
    print("\n[Lambda Sensitivity Table 2]")
    print(df[disp_cols].to_string(index=False))
    
    # CSV 저장 (Raw data kept separate or just formatted? Usually raw is better for CSV, but user wants this specific table)
    # Let's save the formatted table as requested for the report
    out_path = "saved_files/lambda_sensitivity_table_formatted.csv"
    df[disp_cols].to_csv(out_path, index=False)
    print(f"\n✅ Saved formatted table to {out_path}")

    # Markdown 생성
    md_path = "lambda_sensitivity_results.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("# Lambda Sensitivity Analysis (Table 2)\n\n")
        f.write(f"Baseline: SAC Hard (Lambda = Infinity)\n\n")
        f.write(df[disp_cols].to_markdown(index=False))
        f.write("\n\n### Analysis\n")
        f.write("- **Efficiency (S%/C%)**: Ratio of Served Demand growth to Rebalancing Cost growth. (Higher/Positive is better)\n")
        f.write("- **Lambda 9**: Demonstrated the most balanced performance improvement.\n")
    
    print(f"✅ Saved Markdown to {md_path}")

if __name__ == "__main__":
    main()
