"""
SAC Hard vs Soft Rebalancing Flow 비교 시각화
- 저장된 OD flow JSON 파일을 로드하여 OSM Brooklyn 네트워크에 시각화
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import matplotlib.patches as mpatches
import warnings
warnings.filterwarnings('ignore')
import os


def load_od_flows(json_path):
    """OD flow JSON 파일 로드"""
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # OD flows를 tuple key로 변환
    od_flows = {}
    for key, value in data.get('od_flows', {}).items():
        o, d = map(int, key.split('_'))
        od_flows[(o, d)] = value
    
    return od_flows, data


def load_osm_network_and_clusters():
    """OSM 네트워크와 클러스터 정보 로드"""
    import osmnx as ox
    from sklearn.cluster import KMeans
    
    # Load cached network
    G = ox.load_graphml('figures/brooklyn_network.graphml')
    
    # Extract centroids
    nodes = {node: (data['y'], data['x']) for node, data in G.nodes(data=True)}
    centroids = []
    edge_list = []
    for u, v, key, data in G.edges(keys=True, data=True):
        lat1, lon1 = nodes[u]
        lat2, lon2 = nodes[v]
        centroids.append(((lat1 + lat2) / 2, (lon1 + lon2) / 2))
        edge_list.append((u, v, key))
    centroids = np.array(centroids)
    
    # Cluster
    kmeans = KMeans(n_clusters=14, random_state=42, n_init=10)
    edge_labels = kmeans.fit_predict(centroids)
    cluster_centers = kmeans.cluster_centers_
    
    # Simple mapping (latitude order)
    lat_order = np.argsort(cluster_centers[:, 0])
    cluster_to_zone = {int(cluster_idx): int(zone_id) for zone_id, cluster_idx in enumerate(lat_order)}
    
    return G, edge_labels, cluster_centers, cluster_to_zone


def visualize_single_flow(ax, G, edge_labels, cluster_centers, cluster_to_zone, od_flows, title, max_global_flow=None):
    """단일 flow 시각화"""
    import osmnx as ox
    
    zone_to_cluster = {v: k for k, v in cluster_to_zone.items()}
    cmap = plt.cm.get_cmap('tab20', 14)
    colors = [cmap(i) for i in range(14)]
    
    # Edge colors
    edge_colors = []
    for i in range(len(list(G.edges(keys=True)))):
        cluster = edge_labels[i] if i < len(edge_labels) else 0
        zone = cluster_to_zone.get(cluster, 0)
        edge_colors.append(colors[zone])
    
    # Draw road network
    ox.plot_graph(G, ax=ax, node_size=0, edge_color=edge_colors,
                  edge_linewidth=0.3, edge_alpha=0.5, show=False, close=False)
    
    # Draw zone labels
    for cluster_idx, center in enumerate(cluster_centers):
        zone_id = cluster_to_zone.get(cluster_idx, cluster_idx)
        lat, lon = center
        ax.plot(lon, lat, 'o', markersize=18, color=colors[zone_id],
                markeredgecolor='black', markeredgewidth=1.5, zorder=10)
        ax.text(lon, lat, str(zone_id), fontsize=9, fontweight='bold',
                ha='center', va='center', color='white', zorder=11)
    
    # Draw rebalancing flows
    if od_flows:
        max_flow = max_global_flow if max_global_flow else max(od_flows.values())
        
        for (o, d), flow in od_flows.items():
            if o != d and o < 14 and d < 14 and flow > 0:
                if o in zone_to_cluster and d in zone_to_cluster:
                    o_center = cluster_centers[zone_to_cluster[o]]
                    d_center = cluster_centers[zone_to_cluster[d]]
                    
                    # Arrow thickness based on flow
                    linewidth = max(0.5, (flow / max_flow) * 5)
                    alpha = 1.0  # 완전 불투명
                    
                    # Color gradient: light blue (small) -> dark red (large)
                    color_ratio = flow / max_flow
                    arrow_color = (0.2 + 0.7*color_ratio, 0.2*(1-color_ratio), 0.8*(1-color_ratio))
                    
                    arrow = FancyArrowPatch(
                        (o_center[1], o_center[0]),
                        (d_center[1], d_center[0]),
                        arrowstyle='-|>',
                        mutation_scale=8 + linewidth * 1.5,
                        linewidth=linewidth,
                        color=arrow_color,
                        alpha=alpha,
                        zorder=5,
                        connectionstyle="arc3,rad=0.1"
                    )
                    ax.add_patch(arrow)
    
    # Stats
    total_flow = sum(od_flows.values()) if od_flows else 0
    num_pairs = len([k for k, v in od_flows.items() if v > 0]) if od_flows else 0
    ax.set_title(f'{title}\nTotal: {total_flow:.0f} vehicles | OD pairs: {num_pairs}',
                 fontsize=12, fontweight='bold')


def compute_distance_stats(od_flows, cluster_centers, cluster_to_zone):
    """이동 거리 통계 계산"""
    zone_to_cluster = {v: k for k, v in cluster_to_zone.items()}
    
    total_distance = 0
    total_flow = 0
    long_distance_flow = 0  # 2 hops 이상
    
    for (o, d), flow in od_flows.items():
        if o != d and o < 14 and d < 14 and flow > 0:
            if o in zone_to_cluster and d in zone_to_cluster:
                o_center = cluster_centers[zone_to_cluster[o]]
                d_center = cluster_centers[zone_to_cluster[d]]
                distance = np.sqrt((o_center[0] - d_center[0])**2 + (o_center[1] - d_center[1])**2)
                total_distance += distance * flow
                total_flow += flow
                
                # 거리가 상위 33%이면 장거리로 간주
                # (간단한 휴리스틱: hop 수 대신 실제 거리 사용)
    
    avg_distance = total_distance / total_flow if total_flow > 0 else 0
    return total_flow, avg_distance


def main():
    print("=" * 60)
    print("SAC Hard vs Soft Rebalancing Flow 시각화")
    print("=" * 60)
    
    # OD Flow 파일 경로
    hard_json = 'saved_files/SAC_HardLP_nyc_od_flows.json'
    soft_json = 'saved_files/SAC_SoftLP_lam5_nyc_od_flows.json'
    
    # 파일 존재 확인
    if not os.path.exists(hard_json):
        print(f"⚠️ SAC Hard OD flow 파일 없음: {hard_json}")
        print("   테스트를 먼저 실행하세요:")
        print("   python testing.py simulator=macro model=sac simulator.city=nyc_brooklyn model.pretrained_path=ckpt/SAC_HardLP_nyc_t7-12h_ep10000_20260127_193946/ckpt.pth \"model.cplexpath=C:/IBM/ILOG/CPLEX_Studio2211/opl/bin/x64_win64/\"")
        return
    
    if not os.path.exists(soft_json):
        print(f"⚠️ SAC Soft OD flow 파일 없음: {soft_json}")
        print("   테스트를 먼저 실행하세요:")
        print("   python testing.py simulator=macro model=sac simulator.city=nyc_brooklyn model.pretrained_path=ckpt/SAC_SoftLP_lam5_nyc_t7-12h_ep10000_20260127_194646/ckpt.pth \"model.cplexpath=C:/IBM/ILOG/CPLEX_Studio2211/opl/bin/x64_win64/\"")
        return
    
    # 데이터 로드
    print("\n📂 데이터 로드 중...")
    od_hard, data_hard = load_od_flows(hard_json)
    od_soft, data_soft = load_od_flows(soft_json)
    
    print(f"   SAC Hard: {len(od_hard)} OD pairs, Total: {sum(od_hard.values()):.0f}")
    print(f"   SAC Soft: {len(od_soft)} OD pairs, Total: {sum(od_soft.values()):.0f}")
    
    # OSM 네트워크 로드
    print("\n🌐 OSM 네트워크 로드 중...")
    G, edge_labels, cluster_centers, cluster_to_zone = load_osm_network_and_clusters()
    
    # 최대 flow 값 (동일 스케일 비교용)
    max_global_flow = max(max(od_hard.values()) if od_hard else 0, 
                          max(od_soft.values()) if od_soft else 0)
    
    # 시각화
    print("\n🎨 시각화 생성 중...")
    fig, axes = plt.subplots(1, 2, figsize=(22, 11))
    
    visualize_single_flow(axes[0], G, edge_labels, cluster_centers, cluster_to_zone,
                          od_hard, "SAC Hard (No Penalty)", max_global_flow)
    visualize_single_flow(axes[1], G, edge_labels, cluster_centers, cluster_to_zone,
                          od_soft, "SAC Soft (λ=5 Penalty)", max_global_flow)
    
    plt.suptitle('SAC Hard vs Soft: Rebalancing Flow Comparison\n(Arrow thickness = flow magnitude)',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    output_path = 'figures/brooklyn_rebalancing_comparison.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n✅ 저장됨: {output_path}")
    plt.close()
    
    # 비교 통계
    print("\n" + "=" * 60)
    print("비교 통계")
    print("=" * 60)
    
    total_hard, avg_dist_hard = compute_distance_stats(od_hard, cluster_centers, cluster_to_zone)
    total_soft, avg_dist_soft = compute_distance_stats(od_soft, cluster_centers, cluster_to_zone)
    
    reduction_total = ((total_hard - total_soft) / total_hard) * 100 if total_hard > 0 else 0
    reduction_dist = ((avg_dist_hard - avg_dist_soft) / avg_dist_hard) * 100 if avg_dist_hard > 0 else 0
    
    print(f"{'Metric':<25} {'SAC Hard':>12} {'SAC Soft':>12} {'개선':>10}")
    print("-" * 60)
    print(f"{'Total Reb Vehicles':<25} {total_hard:>12.1f} {total_soft:>12.1f} {reduction_total:>9.1f}%")
    print(f"{'Avg Distance':<25} {avg_dist_hard:>12.4f} {avg_dist_soft:>12.4f} {reduction_dist:>9.1f}%")
    print(f"{'Mean Reward ($)':<25} {data_hard.get('mean_reward', 0):>12.1f} {data_soft.get('mean_reward', 0):>12.1f}")
    print(f"{'Mean Reb Cost ($)':<25} {data_hard.get('mean_rebalancing_cost', 0):>12.1f} {data_soft.get('mean_rebalancing_cost', 0):>12.1f}")
    
    print("\n" + "=" * 60)
    print("🎉 완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()
