"""
SAC 학습 결과 분석 및 시각화
"""
import torch
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

print("=" * 70)
print("SAC 학습 결과 분석")
print("=" * 70)

# 1. 체크포인트 파일 확인
ckpt_dir = Path("ckpt")
print(f"\n📁 저장된 모델 파일 ({ckpt_dir}):")
print("-" * 70)

for file in sorted(ckpt_dir.glob("*.pth"), key=lambda x: x.stat().st_mtime, reverse=True):
    size_mb = file.stat().st_size / 1024 / 1024
    mtime = file.stat().st_mtime
    from datetime import datetime
    time_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
    print(f"  {file.name:<30} {size_mb:>8.2f} MB   {time_str}")

# 2. 최신 체크포인트 로드
print("\n" + "=" * 70)
print("최신 모델 정보 (SAC_best.pth)")
print("=" * 70)

try:
    checkpoint = torch.load("ckpt/SAC_best.pth", map_location='cpu')
    
    print(f"\n모델 구성:")
    for key in checkpoint.keys():
        if isinstance(checkpoint[key], dict):
            print(f"  - {key}: {len(checkpoint[key])} 항목")
        elif isinstance(checkpoint[key], torch.Tensor):
            print(f"  - {key}: {checkpoint[key].shape}")
        else:
            print(f"  - {key}: {type(checkpoint[key])}")
    
    # Actor 네트워크 파라미터 확인
    if 'actor_state_dict' in checkpoint:
        actor_params = sum(p.numel() for p in checkpoint['actor_state_dict'].values())
        print(f"\nActor 네트워크 파라미터 수: {actor_params:,}")
    
    # Critic 네트워크 파라미터 확인
    if 'critic_state_dict' in checkpoint:
        critic_params = sum(p.numel() for p in checkpoint['critic_state_dict'].values())
        print(f"Critic 네트워크 파라미터 수: {critic_params:,}")
    
except Exception as e:
    print(f"⚠️ 체크포인트 로드 실패: {e}")

# 3. SUMO 로그 확인
print("\n" + "=" * 70)
print("SUMO 시뮬레이션 로그")
print("=" * 70)

sumo_logs = list(Path("saved_files/sumo_output/scenario_lux").glob("*.txt"))
if sumo_logs:
    latest_log = max(sumo_logs, key=lambda x: x.stat().st_mtime)
    print(f"\n최신 로그: {latest_log.name}")
    
    with open(latest_log, 'r') as f:
        lines = f.readlines()
        # 마지막 20줄 출력
        print("\n마지막 20줄:")
        print("-" * 70)
        for line in lines[-20:]:
            print(line.rstrip())
else:
    print("⚠️ SUMO 로그 파일 없음")

print("\n" + "=" * 70)
print("💡 학습 결과 확인 방법")
print("=" * 70)
print("""
1. 모델 파일:
   ✅ ckpt/SAC_best.pth - 최고 성능 모델
   ✅ ckpt/SAC.pth - 최종 모델

2. 테스트 실행:
   python testing.py \\
     simulator=sumo model=sac \\
     model.checkpoint_path="SAC" \\
     model.test_episodes=5 \\
     simulator.time_start=6 simulator.duration=2

3. 학습 곡선 (Weights & Biases):
   - wandb 설정되어 있으면 wandb.ai에서 확인 가능
   - 또는 TensorBoard 사용 가능

4. SUMO 로그:
   saved_files/sumo_output/scenario_lux/sumo_log_*.txt
""")

print("=" * 70)
