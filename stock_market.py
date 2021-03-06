# Main Code, startdate: 29.6.2018
# Nicolas Andree, adapted from Scikit Learn website example
# with an updated data interface (read from file, insead of google finance which is not working anymore)
# Thus changes to original code: 
# (1) imported data from file as google finance not working anymore
# (2) Using plt.cm.nipy_spectral instead of plt.cm.spectral, which is outdated
# For example using as source data the NYSE daily stock prices from 1962 - 1984 
# Results:
# Cluster 1: comme
# Cluster 2: espey
# Cluster 3: arco, exxon, mobil, tex
# Cluster 4: fisch
# Cluster 5: ahp, alcoa, amerb, coke, dow, dupont, ford, ge, gm, gte, gulf, hp, ibm, inger, jnj, kodak, luken, merck, mmm, morris, pandg, schlum, sears
# Cluster 6: iroqu
# Cluster 7: kimbc
# Cluster 8: kinar
# Cluster 9: meico
# Cluster 10: pills
# Cluster 11: sherw
# 
# Conclusion: the algorithm does not work as nicely on this dataset, as it only identifies 'single stock'-clusters,
# the oil stocks and puts all the remaining bulk of stocks in one cluster

import sys
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from six.moves.urllib.request import urlopen
from six.moves.urllib.parse import urlencode
from sklearn import cluster, covariance, manifold
import matplotlib.pyplot as plt


df1 = pd.read_csv("C:/Users/Nicolas/Documents/R/python/nyse.csv")
#remove unnamed date column
df1 = df1.loc[:, ~df1.columns.str.contains('^Unnamed')]
df1_diff = df1.diff()
names = list(df1.columns.values)
x = np.nan_to_num(df1_diff)

# using only two stocks for some testing (no clustering possible for two however)
# test = names[0:1]
# test.append(names[1])
# names = test
# ahp_diff = df1.ahp.diff()
# ahp_diff = ahp_diff[np.logical_not(np.isnan(ahp_diff))]
# #plt.plot(ahp_diff)
# alcoa_diff = df1.alcoa.diff()
# alcoa_diff = alcoa_diff[np.logical_not(np.isnan(alcoa_diff))]

# list2 = [names[0], names[1]]
# x = np.column_stack([ahp_diff, alcoa_diff])
# x = x[np.logical_not(np.isnan(x))]

names = np.asarray(names)
variation = x
# #############################################################################
# Learn a graphical structure from the correlations
edge_model = covariance.GraphLassoCV()
# standardize the time series: using correlations rather than covariance
# is more efficient for structure recovery
X = variation.copy()
X /= X.std(axis=0)
edge_model.fit(X)

# #############################################################################
# Cluster using affinity propagation

_, labels = cluster.affinity_propagation(edge_model.covariance_)
n_labels = labels.max()

for i in range(n_labels + 1):
    print('Cluster %i: %s' % ((i + 1), ', '.join(names[labels == i])))

# #############################################################################
# #############################################################################
# Find a low-dimension embedding for visualization: find the best position of
# the nodes (the stocks) on a 2D plane

# We use a dense eigen_solver to achieve reproducibility (arpack is
# initiated with random vectors that we don't control). In addition, we
# use a large number of neighbors to capture the large-scale structure.
node_position_model = manifold.LocallyLinearEmbedding(
    n_components=2, eigen_solver='dense', n_neighbors=6)

embedding = node_position_model.fit_transform(X.T).T

# #############################################################################
# Visualization
plt.figure(1, facecolor='w', figsize=(10, 8))
plt.clf()
ax = plt.axes([0., 0., 1., 1.])
plt.axis('off')

# Display a graph of the partial correlations
partial_correlations = edge_model.precision_.copy()
d = 1 / np.sqrt(np.diag(partial_correlations))
partial_correlations *= d
partial_correlations *= d[:, np.newaxis]
non_zero = (np.abs(np.triu(partial_correlations, k=1)) > 0.02)

# Plot the nodes using the coordinates of our embedding
plt.scatter(embedding[0], embedding[1], s=100 * d ** 2, c=labels,
            cmap=plt.cm.nipy_spectral )

# Plot the edges
start_idx, end_idx = np.where(non_zero)
# a sequence of (*line0*, *line1*, *line2*), where::
#            linen = (x0, y0), (x1, y1), ... (xm, ym)
segments = [[embedding[:, start], embedding[:, stop]]
            for start, stop in zip(start_idx, end_idx)]
values = np.abs(partial_correlations[non_zero])
lc = LineCollection(segments,
                    zorder=0, cmap=plt.cm.hot_r,
                    norm=plt.Normalize(0, .7 * values.max()))
lc.set_array(values)
lc.set_linewidths(15 * values)
ax.add_collection(lc)

# Add a label to each node. The challenge here is that we want to
# position the labels to avoid overlap with other labels
for index, (name, label, (x, y)) in enumerate(
        zip(names, labels, embedding.T)):

    dx = x - embedding[0]
    dx[index] = 1
    dy = y - embedding[1]
    dy[index] = 1
    this_dx = dx[np.argmin(np.abs(dy))]
    this_dy = dy[np.argmin(np.abs(dx))]
    if this_dx > 0:
        horizontalalignment = 'left'
        x = x + .002
    else:
        horizontalalignment = 'right'
        x = x - .002
    if this_dy > 0:
        verticalalignment = 'bottom'
        y = y + .002
    else:
        verticalalignment = 'top'
        y = y - .002
    plt.text(x, y, name, size=10,
             horizontalalignment=horizontalalignment,
             verticalalignment=verticalalignment,
             bbox=dict(facecolor='w',
                       edgecolor=plt.cm.nipy_spectral(label / float(n_labels)),
                       alpha=.6))

plt.xlim(embedding[0].min() - .15 * embedding[0].ptp(),
         embedding[0].max() + .10 * embedding[0].ptp(),)
plt.ylim(embedding[1].min() - .03 * embedding[1].ptp(),
         embedding[1].max() + .03 * embedding[1].ptp())

plt.show()
