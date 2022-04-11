import numpy as np
from matplotlib import pyplot as plt

import utils

WIDTH = 100
LENGTH = 8
all_bars = np.zeros((WIDTH * LENGTH,), dtype=int)

for i in range(LENGTH):
    _start = WIDTH * i
    _end = WIDTH * (i + 1)
    all_bars[_start:_end] = i

all_distance = range(120)
all_margin = [utils.dist_2_margin(dist=i, angle_resol=0.1) for i in all_distance]
all_cnt = []

for idx in range(len(all_distance)):
    dist = all_distance[idx]
    margin = all_margin[idx]
    all_cnt_temp = []
    for _start in range(0, min(WIDTH, margin)):
        _sample = all_bars[_start::margin]
        _cnt = [len(np.where(_sample == i)[0]) for i in range(LENGTH)]
        all_cnt_temp.append(_cnt)
    all_cnt.append(all_cnt_temp)

all_cnt_delta_info = {"max": [], "min": [], "avg": []}
all_cnt_delta_cnt = {1: [0 for _ in range(LENGTH - 1)], -1: [0 for _ in range(LENGTH - 1)],
                     0: [0 for _ in range(LENGTH - 1)], "outliers": [0 for _ in range(LENGTH - 1)]}
for _cnt_at_dist in all_cnt:
    __cnt_delta = []
    for __sample_cnt in _cnt_at_dist:
        __sample_cnt = np.array(__sample_cnt, dtype=int)
        __sample_cnt_delta = __sample_cnt[1:] - __sample_cnt[:-1]
        for ___loc, ___loc_delta in enumerate(__sample_cnt_delta):
            try:
                all_cnt_delta_cnt[___loc_delta][___loc] += 1
            except KeyError:
                all_cnt_delta_cnt["outliers"][___loc] += 1
        __cnt_delta.append(__sample_cnt_delta)
    if not __cnt_delta:
        all_cnt_delta_info["max"].append(np.zeros((LENGTH - 1,), dtype=int))
        all_cnt_delta_info["min"].append(np.zeros((LENGTH - 1,), dtype=int))
        all_cnt_delta_info["avg"].append(np.zeros((LENGTH - 1,), dtype=int))
    else:
        __cnt_delta = np.vstack(__cnt_delta)
        all_cnt_delta_info["max"].append(np.max(__cnt_delta, axis=0))
        all_cnt_delta_info["min"].append(np.min(__cnt_delta, axis=0))
        all_cnt_delta_info["avg"].append(np.average(__cnt_delta, axis=0))

all_cnt_delta_info = {key: np.array(val) for key, val in all_cnt_delta_info.items()}
all_cnt_delta_cnt = {key: np.array(val) for key, val in all_cnt_delta_cnt.items()}

print("Cnt Deltas Distribution")
for key, val in all_cnt_delta_info.items():
    print("[%s] MAX=%d, MIN=%d, AVG=%.5f" % (key, np.max(val), np.min(val), np.average(val)))
print("Cnt of Cnt Deltas @ Each Loc Distribution")
for key, val in all_cnt_delta_cnt.items():
    print("[%s] MAX=%d, MIN=%d, AVG=%.5f" % (key, np.max(val), np.min(val), np.average(val)))

# plotting - cnt
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
keys = list(all_cnt_delta_cnt.keys())
colors = ['r', 'g', 'b', 'y']
z_locs = [30, 20, 10, 0]
for idx in range(len(keys)):
    key, c, z = keys[idx], colors[idx], z_locs[idx]
    xs = np.arange(LENGTH - 1)
    ys = all_cnt_delta_cnt[key]

    cs = [c] * len(xs)
    # cs[int(np.argmax(ys))] = 'c'
    print(xs, ys, z)
    ax.bar(xs, ys, zs=z, zdir='y', color=cs, alpha=0.8, label="%s" % key)

ax.set_yticks(z_locs), ax.set_yticklabels(keys)
ax.set_xlabel('Location #'), ax.set_ylabel('Delta Values'), ax.set_zlabel('CNT of Delta Values')
ax.view_init(28, 141)
fig.suptitle("CNT of Delta Categories at All Distances (Right - Left)")  # , color='red')
plt.legend()
# plt.show()
plt.savefig("sample_cnt_analysis__cnt_cnt_cat.png")

# plotting
for key in all_cnt_delta_info.keys():
    plt.clf()
    fig = plt.figure()
    ax = plt.subplot(projection='3d')

    Y = all_distance
    X = np.arange(LENGTH - 1)
    X, Y = np.meshgrid(X, Y)

    Z_max = all_cnt_delta_info["max"]
    print(X.shape, Y.shape, Z_max.shape)

    # Plot the surface.
    surf = ax.plot_surface(X, Y, Z_max, linewidth=0, antialiased=False)

    # Customize the z axis.
    ax.set_xlabel("Location #"), ax.set_ylabel("Distance / m")
    ax.set_zlabel("%s Delta" % (key.capitalize()))
    ax.set_zticks([-1, 0, 1])
    ax.view_init(20, 11)
    fig.colorbar(surf, shrink=0.5, aspect=5)
    fig.suptitle("%s Delta (Right - Left)" % (key.capitalize()))  # , color='red')
    # plt.show()
    plt.savefig("sample_cnt_analysis__%s.png" % key)

print()
