import sys
import os
if 'SUMO_HOME' in os.environ:
    sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
import sumolib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans

print("Loading SUMO network...")
# Load SUMO network
net_file = 'src/envs/data/lux/input/lust_meso.net.xml'
net = sumolib.net.readNet(net_file)


print("Getting network boundary...")
# Get network boundary
boundary = net.getBBoxXY()
print(f"Network boundary: {boundary}")

# Get all edges
edges = list(net.getEdges())
print(f"Total edges: {len(edges)}")

# Sample edge coordinates for clustering (use edge centers)
print("Extracting edge coordinates...")
edge_coords = []
edge_objects = []
for edge in edges:
    # Skip internal edges
    if edge.getFunction() == 'internal':
        continue
    # Get edge center
    shape = edge.getShape()
    if len(shape) > 0:
        # Use midpoint of edge
        mid_idx = len(shape) // 2
        coord = shape[mid_idx]
        edge_coords.append(coord)
        edge_objects.append(edge)

edge_coords = np.array(edge_coords)
print(f"Sampled {len(edge_coords)} edges for clustering")

# Perform K-means clustering (8 regions)
print("Performing K-means clustering (8 regions)...")
n_regions = 8
kmeans = KMeans(n_clusters=n_regions, random_state=10, n_init=10)
labels = kmeans.fit_predict(edge_coords)
centroids = kmeans.cluster_centers_

print(f"Cluster centroids:\n{centroids}")

# Create visualization
fig, axes = plt.subplots(1, 2, figsize=(18, 8))
fig.suptitle('Zone Clustering Visualization (Luxembourg SUMO Network)', fontsize=14, fontweight='bold')

# ======== Plot 1: All edges colored by cluster ========
ax1 = axes[0]
scatter = ax1.scatter(edge_coords[:, 0], edge_coords[:, 1], 
                     c=labels, cmap='tab10', alpha=0.5, s=2)
# Plot centroids
ax1.scatter(centroids[:, 0], centroids[:, 1], 
           c='red', marker='*', s=500, edgecolors='black', linewidths=2,
           label='Zone Centers')
# Add zone numbers
for i, centroid in enumerate(centroids):
    ax1.text(centroid[0], centroid[1], str(i), 
            fontsize=20, fontweight='bold', ha='center', va='center',
            color='white', bbox=dict(boxstyle='circle', facecolor='red', alpha=0.8))

ax1.set_xlabel('X Coordinate (m)', fontsize=11)
ax1.set_ylabel('Y Coordinate (m)', fontsize=11)
ax1.set_title('All Network Edges Clustered into 8 Zones', fontsize=12, fontweight='bold')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)
ax1.set_aspect('equal')

# ======== Plot 2: Voronoi-style zone boundaries ========
ax2 = axes[1]

# Create a grid for Voronoi visualization
x_min, y_min = edge_coords.min(axis=0)
x_max, y_max = edge_coords.max(axis=0)
x_range = x_max - x_min
y_range = y_max - y_min

# Add padding
padding = 0.1
x_min -= x_range * padding
x_max += x_range * padding
y_min -= y_range * padding
y_max += y_range * padding

# Create mesh grid
grid_resolution = 200
xx, yy = np.meshgrid(np.linspace(x_min, x_max, grid_resolution),
                     np.linspace(y_min, y_max, grid_resolution))
grid_points = np.c_[xx.ravel(), yy.ravel()]

# Predict cluster for each grid point
grid_labels = kmeans.predict(grid_points)
grid_labels = grid_labels.reshape(xx.shape)

# Plot Voronoi regions
contour = ax2.contourf(xx, yy, grid_labels, levels=np.arange(-0.5, n_regions, 1), 
                       cmap='tab10', alpha=0.6)
ax2.contour(xx, yy, grid_labels, levels=np.arange(-0.5, n_regions, 1),
           colors='black', linewidths=1.5, alpha=0.4)

# Plot centroids
ax2.scatter(centroids[:, 0], centroids[:, 1], 
           c='red', marker='*', s=500, edgecolors='black', linewidths=2)

# Add zone numbers with labels
for i, centroid in enumerate(centroids):
    ax2.text(centroid[0], centroid[1], f'Zone {i}', 
            fontsize=14, fontweight='bold', ha='center', va='center',
            color='white', bbox=dict(boxstyle='round,pad=0.5', facecolor='darkred', alpha=0.9))

ax2.set_xlabel('X Coordinate (m)', fontsize=11)
ax2.set_ylabel('Y Coordinate (m)', fontsize=11)
ax2.set_title('Zone Boundaries (Voronoi Diagram)', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.set_aspect('equal')

plt.tight_layout()
plt.savefig('saved_files/congestion/zone_clustering_map.png', dpi=300, bbox_inches='tight')
print("\nSaved: saved_files/congestion/zone_clustering_map.png")

# ======== Print zone statistics ========
print("\n" + "="*80)
print("ZONE STATISTICS")
print("="*80)

for i in range(n_regions):
    zone_edges = np.sum(labels == i)
    centroid = centroids[i]
    print(f"\nZone {i}:")
    print(f"  Centroid: ({centroid[0]:.1f}, {centroid[1]:.1f})")
    print(f"  Number of edges: {zone_edges}")
    
# Calculate zone distances
print("\n" + "="*80)
print("INTER-ZONE DISTANCES (meters)")
print("="*80)
print("\nDistance matrix (Zone i -> Zone j):")
print("     ", end="")
for j in range(n_regions):
    print(f"  {j:>6}", end="")
print()

for i in range(n_regions):
    print(f"Zone {i}:", end="")
    for j in range(n_regions):
        dist = np.linalg.norm(centroids[i] - centroids[j])
        print(f"  {dist:>6.0f}", end="")
    print()

print("\n" + "="*80)
print("VISUALIZATION SAVED")
print("="*80)
print("File: saved_files/congestion/zone_clustering_map.png")
print("\nLeft panel: All network edges colored by zone")
print("Right panel: Zone boundaries (Voronoi diagram)")
print("="*80)
