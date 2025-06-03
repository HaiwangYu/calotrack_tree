import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from util import *
from sklearn.metrics import adjusted_rand_score
from util import *


bin_edges = np.linspace(0, 5, 26)  # Define bin edges
total_matched_hist = np.zeros(len(bin_edges) - 1, dtype=int)
total_all_hist = np.zeros(len(bin_edges) - 1, dtype=int)
binned_aris = [ [] for _ in range(len(bin_edges) - 1)]

integrated_pt_bins = np.array([0.5, 1.0, 1000.0])  # Example bin edges for pT
integrated_pt_matched_hist = np.zeros(len(integrated_pt_bins) - 1, dtype=int)
integrated_pt_all_hist = np.zeros(len(integrated_pt_bins) - 1, dtype=int)

dummy_pt_bin_edges = np.linspace(0, 1000, 2)  # a dummy bin to include all particles
unbinned_aris = [ [] for _ in range(len(dummy_pt_bin_edges) - 1)]

# Loop to read and process files from event_0 to event_10
for ievent in range(0, 1000):
    print (f"Processing event {ievent}...")
    # fname = f'2025-05-13-pp-1k-cut/data_event_{ievent}.h5'
    # fname = f'2025-05-20-pp-1k-nocut/data_event_{ievent}.h5'
    fname = f'2025-05-20-pp-10k-mincut/data_event_{ievent}.h5'
    with pd.HDFStore(fname, mode='r') as store:
        clusters = store['clusters']      # Saved as fixed format
        seeds = store['seeds']            # Saved as fixed format
        particles = store['particles']    # Saved as fixed format

        print(f"Number of particles: {len(particles)}")
        particles = particles[particles['cids'].apply(len) > 5]
        print(f"|nclus| > 20: {len(particles)}")
        particles = particles[particles['eta'].apply(abs) < 1.1]
        print(f"|eta| < 1.1: {len(particles)}")
        # particles = particles[particles['vz'].apply(abs) < 10]
        # print(f"|vz| < 10: {len(particles)}")
        # particles = particles[particles['ptid']>0]
        # print(f"ptid > 0: {len(particles)}")

        ncommon = 30  # change to your desired threshold
        matched_pt = match_particles_to_seeds_optimized(particles, seeds, ncommon)
        all_pt = particles['pt'].tolist()

        matched_hist, _ = np.histogram(matched_pt, bins=bin_edges)
        all_hist, _ = np.histogram(all_pt, bins=bin_edges)
        total_matched_hist += matched_hist
        total_all_hist += all_hist
        print(f"Event {ievent}: All {len(all_pt)} matched: {len(matched_pt)}\n")

        matched_hist, _ = np.histogram(matched_pt, bins=integrated_pt_bins)
        all_hist, _ = np.histogram(all_pt, bins=integrated_pt_bins)
        integrated_pt_matched_hist += matched_hist
        integrated_pt_all_hist += all_hist
        print(f"Event {ievent}: All {len(integrated_pt_all_hist)} matched: {len(integrated_pt_matched_hist)}\n")

        # Calculate ARI
        cid_to_index = {cid: index for index, cid in enumerate(clusters['cid'])}
        cid_to_pt = cid_to_pt_mapping(particles)
        groupids_particle = get_group_ids(particles, clusters.shape[0], cid_to_index, cid_to_pt, bin_edges)
        # print(f"groupids_particle {groupids_particle}")
        groupids_seed = get_group_ids(seeds, clusters.shape[0], cid_to_index, cid_to_pt, bin_edges)
        # print(f"groupids_seed {groupids_seed}")
        for ibin in range(len(bin_edges) - 1):
            ari = adjusted_rand_score(groupids_particle[ibin], groupids_seed[ibin])
            binned_aris[ibin].append(ari)
            # print(f"ievent {ievent}, bin {ibin}: ARI = {ari:.4f}")
        
        groupids_particle = get_group_ids(particles, clusters.shape[0], cid_to_index, cid_to_pt, dummy_pt_bin_edges)
        groupids_seed = get_group_ids(seeds, clusters.shape[0], cid_to_index, cid_to_pt, dummy_pt_bin_edges)
        # print(f"groupids_particle {groupids_particle}")
        # print(f"groupids_seed {groupids_seed}")
        for ibin in range(len(dummy_pt_bin_edges) - 1):
            ari = adjusted_rand_score(groupids_particle[ibin], groupids_seed[ibin])
            unbinned_aris[ibin].append(ari)
            print(f"ievent {ievent}, bin {ibin}: unbinned ARI = {ari:.4f}")

print("Total Matched histogram:", total_matched_hist)
print("Total All histogram:", total_all_hist)

print("Integrated pT Matched histogram:", integrated_pt_matched_hist)
print("Integrated pT All histogram:", integrated_pt_all_hist)

# Calculate average ARI for each bin
avg_aris = [np.mean(bin_aris) if bin_aris else 0 for bin_aris in binned_aris]
std_aris = [np.std(bin_aris) if len(bin_aris) > 1 else 0 for bin_aris in binned_aris]
print("avg_aris:", avg_aris)

# Calculate average and std for unbinned ARI
unbinned_avg_aris = [np.mean(bin_aris) if bin_aris else 0 for bin_aris in unbinned_aris]
unbinned_std_aris = [np.std(bin_aris) if len(bin_aris) > 1 else 0 for bin_aris in unbinned_aris]
print("unbinned_avg_aris", unbinned_avg_aris)


# Get bin centers for plotting
bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

# Plot average ARI by pT bin
plt.figure(figsize=(10, 6))
plt.errorbar(bin_centers, avg_aris, yerr=std_aris, marker='o', linestyle='-', capsize=3)
plt.xlabel('pT (GeV/c)')
plt.ylabel('Average Adjusted Rand Index')
plt.title('Clustering Quality (ARI) vs. Particle pT')
plt.grid(True, alpha=0.3)
plt.savefig('ari_vs_pt.png')
plt.show()

# Plotting the histograms
plot_eff((total_all_hist, bin_edges), (total_matched_hist, bin_edges))