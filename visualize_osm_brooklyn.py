"""
OSM 기반 NYC Brooklyn 도로 네트워크 시각화 (v3 - 개선된 버전)
- GNN 토폴로지 연결 + 이동시간 행렬 동시 고려
- 두 제약조건을 모두 만족하는 최적 클러스터-존 매핑
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import warnings
warnings.filterwarnings('ignore')
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import cdist
from itertools import permutations

def check_dependencies():
    """필요한 패키지 확인"""
    missing = []
    try:
        import osmnx
    except ImportError:
        missing.append('osmnx')
    try:
        from sklearn.cluster import KMeans
    except ImportError:
        missing.append('scikit-learn')
    
    if missing:
        print(f"⚠️ 필요한 패키지가 없습니다: {missing}")
        return False
    return True

def download_brooklyn_network(use_cache=True):
    """OpenStreetMap에서 Brooklyn 도로 네트워크 로드"""
    import osmnx as ox
    
    cache_file = 'figures/brooklyn_network.graphml'
    
    if use_cache:
        try:
            import os
            if os.path.exists(cache_file):
                print("📂 캐시된 네트워크 로딩...")
                return ox.load_graphml(cache_file)
        except Exception as e:
            print(f"캐시 로딩 실패: {e}")
    
    print("🌐 Brooklyn 도로망 다운로드 중...")
    G = ox.graph_from_place("Brooklyn, New York City, New York, USA", 
                            network_type='drive', simplify=True)
    import os
    os.makedirs('figures', exist_ok=True)
    ox.save_graphml(G, cache_file)
    return G


def extract_edge_centroids(G):
    """도로 링크 중심점 추출"""
    nodes = {node: (data['y'], data['x']) for node, data in G.nodes(data=True)}
    centroids = []
    edge_list = []
    
    for u, v, key, data in G.edges(keys=True, data=True):
        lat1, lon1 = nodes[u]
        lat2, lon2 = nodes[v]
        centroids.append(((lat1 + lat2) / 2, (lon1 + lon2) / 2))
        edge_list.append((u, v, key))
    
    return np.array(centroids), edge_list


def cluster_edges_kmeans(centroids, n_clusters=14):
    """K-means 클러스터링"""
    from sklearn.cluster import KMeans
    
    print(f"🔄 K-means 클러스터링 ({n_clusters}개 존)...")
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(centroids)
    return labels, kmeans.cluster_centers_


def load_scenario_data():
    """시나리오 데이터 로드"""
    with open('src/envs/data/macro/scenario_nyc_brooklyn.json', 'r') as f:
        return json.load(f)


def build_gnn_adjacency(scenario_data):
    """
    GNN 토폴로지 그래프에서 인접 행렬 구축
    """
    topology = scenario_data.get('topology_graph', [])
    n_zones = 14
    adj = np.zeros((n_zones, n_zones), dtype=int)
    
    for edge in topology:
        adj[edge['i'], edge['j']] = 1
    
    print(f"📊 GNN 토폴로지: {len(topology)}개 엣지")
    return adj


def build_travel_time_matrix(scenario_data):
    """존 간 평균 이동 시간 행렬 생성"""
    import pandas as pd
    
    df = pd.DataFrame(scenario_data['demand'])
    avg_tt = df.groupby(['origin', 'destination'])['travel_time'].mean().reset_index()
    
    n_zones = 14
    tt_matrix = np.full((n_zones, n_zones), np.inf)
    
    for _, row in avg_tt.iterrows():
        o, d = int(row['origin']), int(row['destination'])
        if o < n_zones and d < n_zones:
            tt_matrix[o, d] = row['travel_time']
    
    # 대칭화
    for i in range(n_zones):
        for j in range(i+1, n_zones):
            min_tt = min(tt_matrix[i, j], tt_matrix[j, i])
            if min_tt != np.inf:
                tt_matrix[i, j] = min_tt
                tt_matrix[j, i] = min_tt
    
    np.fill_diagonal(tt_matrix, 0)
    return tt_matrix


def build_cluster_adjacency(cluster_centers, threshold_percentile=25):
    """
    클러스터 중심 간 거리로 인접 구조 추정
    - 가까운 클러스터끼리 인접한 것으로 간주
    """
    n_clusters = len(cluster_centers)
    distances = cdist(cluster_centers, cluster_centers, metric='euclidean')
    
    # 자기 자신 제외하고 threshold 계산
    mask = ~np.eye(n_clusters, dtype=bool)
    threshold = np.percentile(distances[mask], threshold_percentile)
    
    adj = (distances < threshold) & mask
    return adj.astype(int), distances


def compute_mapping_cost(mapping, gnn_adj, cluster_adj, tt_matrix, cluster_distances):
    """
    주어진 매핑의 비용 계산
    
    비용 = α * (GNN 인접성 불일치) + β * (이동시간 패턴 불일치)
    """
    n = len(mapping)
    
    # 1. GNN 인접성 비용: 연결된 존들이 인접한 클러스터에 매핑되었는지
    adj_cost = 0
    for zone_i in range(n):
        for zone_j in range(n):
            if gnn_adj[zone_i, zone_j] == 1:  # GNN에서 연결된 존
                cluster_i = mapping[zone_i]
                cluster_j = mapping[zone_j]
                if cluster_adj[cluster_i, cluster_j] != 1:  # 클러스터가 인접하지 않으면 패널티
                    adj_cost += 1
    
    # 2. 이동시간 패턴 비용: 존 간 이동시간과 클러스터 간 거리의 상관관계
    tt_cost = 0
    tt_norm = tt_matrix.copy()
    tt_norm[tt_norm == np.inf] = np.nanmax(tt_matrix[tt_matrix < np.inf]) * 2 if np.any(tt_matrix < np.inf) else 100
    tt_norm = tt_norm / (tt_norm.max() + 1e-10)
    
    dist_norm = cluster_distances / (cluster_distances.max() + 1e-10)
    
    for zone_i in range(n):
        for zone_j in range(n):
            if zone_i != zone_j:
                cluster_i = mapping[zone_i]
                cluster_j = mapping[zone_j]
                tt_cost += abs(tt_norm[zone_i, zone_j] - dist_norm[cluster_i, cluster_j])
    
    # 가중치 조합
    alpha = 10.0  # GNN 연결 가중치 (더 중요)
    beta = 1.0   # 이동시간 가중치
    
    total_cost = alpha * adj_cost + beta * tt_cost
    return total_cost, adj_cost, tt_cost


def optimize_mapping_greedy(gnn_adj, cluster_adj, tt_matrix, cluster_distances, max_iterations=1000):
    """
    Greedy + Local Search로 최적 매핑 찾기
    """
    import random
    n = 14
    
    print("🔍 최적 매핑 탐색 중...")
    
    # 초기 매핑: 무작위
    best_mapping = list(range(n))
    random.shuffle(best_mapping)
    best_cost, _, _ = compute_mapping_cost(best_mapping, gnn_adj, cluster_adj, tt_matrix, cluster_distances)
    
    # 다중 시작점
    for start in range(20):
        current_mapping = list(range(n))
        random.shuffle(current_mapping)
        current_cost, _, _ = compute_mapping_cost(current_mapping, gnn_adj, cluster_adj, tt_matrix, cluster_distances)
        
        # Local search: 2-opt swap
        improved = True
        iterations = 0
        
        while improved and iterations < max_iterations:
            improved = False
            iterations += 1
            
            for i in range(n):
                for j in range(i+1, n):
                    # Swap zone i and zone j's cluster assignments
                    new_mapping = current_mapping.copy()
                    new_mapping[i], new_mapping[j] = new_mapping[j], new_mapping[i]
                    
                    new_cost, _, _ = compute_mapping_cost(new_mapping, gnn_adj, cluster_adj, tt_matrix, cluster_distances)
                    
                    if new_cost < current_cost:
                        current_mapping = new_mapping
                        current_cost = new_cost
                        improved = True
                        break
                if improved:
                    break
        
        if current_cost < best_cost:
            best_cost = current_cost
            best_mapping = current_mapping.copy()
    
    # zone_id -> cluster_id 매핑 생성
    zone_to_cluster = {zone: cluster for zone, cluster in enumerate(best_mapping)}
    cluster_to_zone = {cluster: zone for zone, cluster in enumerate(best_mapping)}
    
    final_cost, adj_cost, tt_cost = compute_mapping_cost(best_mapping, gnn_adj, cluster_adj, tt_matrix, cluster_distances)
    
    print(f"✅ 최적 매핑 완료:")
    print(f"   - 총 비용: {final_cost:.2f}")
    print(f"   - GNN 인접성 불일치: {adj_cost}")
    print(f"   - 이동시간 패턴 비용: {tt_cost:.2f}")
    
    return cluster_to_zone


def visualize_network_with_zones(G, edge_labels, cluster_centers, cluster_to_zone, gnn_adj, od_flows, output_path='figures/brooklyn_osm_zones_v3.png'):
    """시각화"""
    import osmnx as ox
    import matplotlib.patches as mpatches
    
    print("🎨 시각화 생성 중...")
    
    fig, ax = plt.subplots(figsize=(16, 14))
    
    cmap = plt.cm.get_cmap('tab20', 14)
    colors = [cmap(i) for i in range(14)]
    
    edge_colors = []
    for i, (u, v, key) in enumerate(G.edges(keys=True)):
        cluster = edge_labels[i] if i < len(edge_labels) else 0
        zone = cluster_to_zone.get(cluster, 0)
        edge_colors.append(colors[zone])
    
    ox.plot_graph(G, ax=ax, node_size=0, edge_color=edge_colors, 
                  edge_linewidth=0.5, edge_alpha=0.7, show=False, close=False)
    
    # 존 라벨 표시
    for cluster_idx, center in enumerate(cluster_centers):
        zone_id = cluster_to_zone.get(cluster_idx, cluster_idx)
        lat, lon = center
        ax.plot(lon, lat, 'o', markersize=25, color=colors[zone_id], 
                markeredgecolor='black', markeredgewidth=2, zorder=10)
        ax.text(lon, lat, str(zone_id), fontsize=11, fontweight='bold',
                ha='center', va='center', color='white', zorder=11)
    
    # GNN 연결 표시 (파란색 실선)
    zone_to_cluster = {v: k for k, v in cluster_to_zone.items()}
    for zone_i in range(14):
        for zone_j in range(zone_i+1, 14):
            if gnn_adj[zone_i, zone_j] == 1 or gnn_adj[zone_j, zone_i] == 1:
                if zone_i in zone_to_cluster and zone_j in zone_to_cluster:
                    c_i = cluster_centers[zone_to_cluster[zone_i]]
                    c_j = cluster_centers[zone_to_cluster[zone_j]]
                    ax.plot([c_i[1], c_j[1]], [c_i[0], c_j[0]], 
                            'b-', linewidth=1.5, alpha=0.5, zorder=4)
    
    # OD Flow 화살표 (상위 10개, 빨간색)
    sorted_flows = sorted(od_flows.items(), key=lambda x: x[1], reverse=True)[:10]
    for (origin, dest), flow in sorted_flows:
        if origin != dest and origin < 14 and dest < 14:
            if origin in zone_to_cluster and dest in zone_to_cluster:
                o_center = cluster_centers[zone_to_cluster[origin]]
                d_center = cluster_centers[zone_to_cluster[dest]]
                arrow = FancyArrowPatch(
                    (o_center[1], o_center[0]), (d_center[1], d_center[0]),
                    arrowstyle='-|>', mutation_scale=12,
                    linewidth=max(1, np.log1p(flow) * 0.5),
                    color='red', alpha=0.7, zorder=6)
                ax.add_patch(arrow)
    
    legend_patches = [mpatches.Patch(color=colors[i], label=f'Zone {i}') for i in range(14)]
    legend_patches.append(mpatches.Patch(color='blue', label='GNN Edge'))
    legend_patches.append(mpatches.Patch(color='red', label='Top OD Flow'))
    ax.legend(handles=legend_patches, loc='upper left', ncol=2, fontsize=8)
    
    ax.set_title('NYC Brooklyn Road Network\nOptimized Zone Mapping (GNN Topology + Travel Time)', 
                 fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ 저장됨: {output_path}")
    plt.close()
    
    return output_path


def main():
    print("=" * 60)
    print("OSM Brooklyn 시각화 v3")
    print("GNN 토폴로지 + 이동시간 동시 고려")
    print("=" * 60)
    
    if not check_dependencies():
        return
    
    # 1. 도로 네트워크 로드
    G = download_brooklyn_network(use_cache=True)
    print(f"📊 네트워크: {G.number_of_nodes()} 노드, {G.number_of_edges()} 엣지")
    
    # 2. 클러스터링
    centroids, edge_list = extract_edge_centroids(G)
    labels, cluster_centers = cluster_edges_kmeans(centroids, n_clusters=14)
    
    # 3. 시나리오 데이터 로드
    scenario_data = load_scenario_data()
    
    # 4. GNN 인접 행렬
    gnn_adj = build_gnn_adjacency(scenario_data)
    
    # 5. 이동시간 행렬
    tt_matrix = build_travel_time_matrix(scenario_data)
    
    # 6. 클러스터 인접 구조
    cluster_adj, cluster_distances = build_cluster_adjacency(cluster_centers)
    
    # 7. 최적 매핑 탐색
    cluster_to_zone = optimize_mapping_greedy(gnn_adj, cluster_adj, tt_matrix, cluster_distances)
    
    print("\n📍 최종 매핑 결과:")
    for c, z in sorted(cluster_to_zone.items(), key=lambda x: x[1]):
        print(f"   클러스터 {c} → 존 {z}")
    
    # 8. OD 흐름
    import pandas as pd
    df = pd.DataFrame(scenario_data['demand'])
    od_flows = df.groupby(['origin', 'destination'])['demand'].sum().to_dict()
    
    # 9. 시각화
    output_path = visualize_network_with_zones(
        G, labels, cluster_centers, cluster_to_zone, gnn_adj, od_flows
    )
    
    print("=" * 60)
    print("🎉 완료!")
    print("=" * 60)
    return output_path


if __name__ == "__main__":
    main()
