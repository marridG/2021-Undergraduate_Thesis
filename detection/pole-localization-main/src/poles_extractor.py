import numpy as np
from numba import jit


def detect_poles(xyz, neighbourthr=0.5, min_point_num=3, dis_thr=0.08, width_thr=10, fov_up=30.67, fov_down=-10.67,
                 proj_H=32, proj_W=250, lowest=0.1, highest=6, lowthr=1.5, highthr=0.7, totalthr=0.6):
    range_data, proj_vertex, _ = range_projection(xyz,
                                                  fov_up=fov_up,
                                                  fov_down=fov_down,
                                                  proj_H=proj_H,
                                                  proj_W=proj_W,
                                                  max_range=50,
                                                  cut_z=True,
                                                  low=lowest,
                                                  high=highest)

    height = range_data.shape[0]
    width = range_data.shape[1]

    # === 1 === generate clusters
    open_set = gen_open_set(range_data, height, width)
    open_set = np.array(open_set)

    clusters = gen_clusters(open_set, range_data, height, width, min_point_num=min_point_num, dis_thr=dis_thr)

    # === 2 === filter out some clusters by: ratio, smaller distance points ratio
    clusters_list = []
    for cluster in clusters:
        clusters_list.append(cluster.tolist())

    clusters_copy = list(clusters_list)
    for cluster in clusters_copy:  # <list< of "shape" (n,2)
        # calculate the height:width ratio
        cluster.sort()  # sort by each element's height (dim1 idx) to extract min&max height
        min_height = cluster[0][0]
        max_height = cluster[len(cluster) - 1][0]
        cluster.sort(key=takeSecond)  # sort by each element's width (dim2 idx) to extract min&max width
        min_width = cluster[0][1]
        max_width = cluster[len(cluster) - 1][1]
        ratio = (max_height - min_height + 1) / (max_width - min_width + 1)

        # count "smaller distance points" in the cluster
        delate = 0
        dela = False
        for index in cluster:  # <list> of len=2
            index[0] = int(index[0])
            index[1] = int(index[1])
            # search for all the "smaller distance points" in the cluster if either its left or right adjacent point
            #   meet all requirements:
            #       (0) has a distance in the range image and lies outside the cluster
            #       (1) has a smaller distance than it (in the cluster)
            if (range_data[index[0], index[1] + 1] != -1) and (not [index[0], index[1] + 1] in cluster) \
                    and range_data[index[0]][index[1]] > range_data[index[0], index[1] + 1]:
                dela = True
            if (range_data[index[0], index[1] - 1] != -1) and (not [index[0], index[1] - 1] in cluster) \
                    and range_data[index[0]][index[1]] > range_data[index[0], index[1] - 1]:
                dela = True
            if dela:
                delate += 1
                dela = False

        if ratio < 1.0 or delate > 0.3 * len(cluster) or (max_width - min_width + 1) > width_thr:
            clusters_list.remove(cluster)

    # === 3 === filter out some clusters by:
    poleparams = np.empty([0, 3])
    for cluster in clusters_list:
        x = []
        y = []
        z = []
        for index in cluster:
            index[0] = int(index[0])
            index[1] = int(index[1])
            x.append(proj_vertex[index[0]][index[1]][0])
            y.append(proj_vertex[index[0]][index[1]][1])
            z.append(proj_vertex[index[0]][index[1]][2])

        high = max(z)
        low = min(z)
        if high > highthr and low < lowthr and (high - low) > totalthr:
            if fit_circle(x, y) != None:
                average_x, average_y, R_1 = fit_circle(x, y)
                fine_thr = R_1 + 0.1
                scan_x = xyz[:, 0]
                scan_y = xyz[:, 1]
                scan_z = xyz[:, 2]

                high = min(high, 3.0)

                current_vertex_fine = xyz[(scan_x > (average_x - fine_thr)) & (scan_x < (average_x + fine_thr)) & (
                        scan_y < (average_y + fine_thr)) & (scan_y > (average_y - fine_thr)) & (scan_z < high) & (
                                                  scan_z > low)]
                x = []
                y = []
                for i in range(current_vertex_fine.shape[0]):
                    x.append(current_vertex_fine[i, 0])
                    y.append(current_vertex_fine[i, 1])
                if len(x) >= 6:
                    if fit_circle(x, y) != None:
                        xc_1, yc_1, R_1 = fit_circle(x, y)
                        if R_1 > 0.02 and R_1 < 0.4:
                            neighbour = xyz[(((scan_x > (average_x - fine_thr - neighbourthr)) & (
                                    scan_x < (average_x - fine_thr))) | ((scan_x > (average_x + fine_thr)) & (
                                    scan_x < (average_x + fine_thr + neighbourthr)))) & (((scan_y > (
                                    average_y + fine_thr - neighbourthr)) & (scan_y < (average_y - fine_thr))) | ((
                                                                                                                          scan_y > (
                                                                                                                          average_y + fine_thr)) & (
                                                                                                                          scan_y < (
                                                                                                                          average_y + fine_thr + neighbourthr)))) & (
                                                    scan_z < high) & (scan_z > low)]
                            if neighbour.shape[0] < 0.15 * current_vertex_fine.shape[0]:
                                poleparams = np.vstack([poleparams, [xc_1, yc_1, R_1]])

    return poleparams


@jit(nopython=True)
def gen_open_set(range_data, height, width):
    open_set = []
    for i in range(1, height - 1):
        for j in range(1, width - 1):
            if range_data[i][j] != -1:
                open_set.append([i, j])
    return open_set


@jit(nopython=True)
def in_array(set, index):
    for i in range(set.shape[0]):
        if set[i][0] == index[0] and set[i][1] == index[1]:
            return True
    return False


@jit(nopython=True)
def gen_clusters(open_set, range_data, height, width, min_point_num=3, dis_thr=0.08):
    """

    :param open_set:
    :param range_data:
    :param height:
    :param width:
    :param min_point_num:
    :param dis_thr:
    :return:                        <list>of<np.ndarray>s, each, shaped (n,2), as a cluster of n points in the image
    """
    clusters = []
    while open_set.shape[0] > 0:
        # create a new cluster
        cluster = np.zeros((0, 2))
        current_index = open_set[0]  # the current p, of shape (2,)
        open_set = np.delete(open_set, [0, 1]).reshape((-1, 2))  # remove the assigned p (idx=0 item)
        cluster = np.append(cluster, current_index).reshape((-1, 2))  # add p to the cluster
        near_set = np.zeros((0, 2), dtype=np.int64)  # init the empty set of neighbours for p

        # further init p's neighbours by all its valid bottom/right adjacent points (why not left?)
        # check p's bottom adjacent point: whether is p's neighbour
        if (current_index[0] + 1 < height) \
                and (in_array(open_set, np.array([current_index[0] + 1, current_index[1]]))) \
                and abs(range_data[current_index[0]][current_index[1]]
                        - range_data[current_index[0] + 1][current_index[1]]) < dis_thr:
            near_set = np.append(near_set, [current_index[0] + 1, current_index[1]]).reshape((-1, 2))
        # check p's right adjacent point: whether is p's neighbour
        if (current_index[1] + 1 < width) \
                and (in_array(open_set, np.array([current_index[0], current_index[1] + 1]))) \
                and abs(range_data[current_index[0]][current_index[1]]
                        - range_data[current_index[0]][current_index[1] + 1]) < dis_thr:
            near_set = np.append(near_set, [current_index[0], current_index[1] + 1]).reshape((-1, 2))

        while len(near_set) > 0:
            near_index = near_set[0]  # select and handle one of p's neighbour
            near_set = np.delete(near_set, [0, 1]).reshape((-1, 2))  # remove the selected one from p's neighbour set
            for i in range(open_set.shape[0]):  # remove the selected one from the open set
                if open_set[i][0] == near_index[0] and open_set[i][1] == near_index[1]:
                    open_set = np.delete(open_set, [2 * i, 2 * i + 1]).reshape((-1, 2))
                    break
            cluster = np.append(cluster, near_index).reshape((-1, 2))  # add the selected one to p's cluster

            # check candidate neighbours (bottom, right, left) of the selected p's neighbour
            #   if all requirements are met:
            #       (0) valid indices in the range image;
            #       (1) in open set; (2) not in the current cluster; (3) not already added as a neighbour
            #   if so, the point is added to p's neighbour set
            # bottom neighbour
            if (near_index[0] + 1 < height) \
                    and (in_array(open_set, np.array([near_index[0] + 1, near_index[1]]))) \
                    and (not in_array(cluster, np.array([near_index[0] + 1, near_index[1]]))) \
                    and (not in_array(near_set, np.array([near_index[0] + 1, near_index[1]]))) \
                    and (abs(range_data[near_index[0]][near_index[1]]
                             - range_data[near_index[0] + 1][near_index[1]]) < dis_thr):
                near_set = np.append(near_set, [near_index[0] + 1, near_index[1]]).reshape((-1, 2))
            # right neighbour
            if (near_index[1] + 1 < width) \
                    and (in_array(open_set, np.array([near_index[0], near_index[1] + 1]))) \
                    and (not in_array(cluster, np.array([near_index[0], near_index[1] + 1]))) \
                    and (not in_array(near_set, np.array([near_index[0], near_index[1] + 1]))) \
                    and (abs(range_data[near_index[0]][near_index[1]]
                             - range_data[near_index[0]][near_index[1] + 1]) < dis_thr):
                near_set = np.append(near_set, [near_index[0], near_index[1] + 1]).reshape((-1, 2))
            # left neighbour
            if (near_index[1] - 1 >= 0) \
                    and (in_array(open_set, np.array([near_index[0], near_index[1] - 1]))) \
                    and (not in_array(cluster, np.array([near_index[0], near_index[1] - 1]))) \
                    and (not in_array(near_set, np.array([near_index[0], near_index[1] - 1]))) \
                    and (abs(range_data[near_index[0]][near_index[1]]
                             - range_data[near_index[0]][near_index[1] - 1]) < dis_thr):
                near_set = np.append(near_set, [near_index[0], near_index[1] - 1]).reshape((-1, 2))

        if cluster.shape[0] > min_point_num:
            clusters.append(cluster)

    return clusters


def takeSecond(elem):
    return elem[1]


def range_projection(current_vertex, fov_up=10.67, fov_down=-30.67, proj_H=32, proj_W=900, max_range=50, cut_z=True,
                     low=0.1, high=6):
    """ Project a pointcloud into a spherical projection, range image.
        Args:
        current_vertex: raw point clouds
        Returns: 
        proj_range: projected range image with depth, each pixel contains the corresponding depth
        proj_vertex: each pixel contains the corresponding point (x, y, z, 1)
        proj_idx: each pixel contains the corresponding index of the point in the raw point cloud
    """
    # laser parameters
    fov_up = fov_up / 180.0 * np.pi  # field of view up in radians
    fov_down = fov_down / 180.0 * np.pi  # field of view down in radians
    fov = abs(fov_down) + abs(fov_up)  # get field of view total in radians

    # get depth of all points
    depth = np.linalg.norm(current_vertex[:, :3], 2, axis=1)

    if cut_z:
        z = current_vertex[:, 2]
        current_vertex = current_vertex[
            (depth > 0) & (depth < max_range) & (z < high) & (z > low)]  # get rid of [0, 0, 0] points
        depth = depth[(depth > 0) & (depth < max_range) & (z < high) & (z > low)]
    else:
        current_vertex = current_vertex[(depth > 0) & (depth < max_range)]  # get rid of [0, 0, 0] points
        depth = depth[(depth > 0) & (depth < max_range)]

    # get scan components
    scan_x = current_vertex[:, 0]
    scan_y = current_vertex[:, 1]
    scan_z = current_vertex[:, 2]

    # get angles of all points
    yaw = -np.arctan2(scan_y, scan_x)
    pitch = np.arcsin(scan_z / depth)

    # get projections in image coords
    proj_x = 0.5 * (yaw / np.pi + 1.0)  # in [0.0, 1.0]
    proj_y = 1.0 - (pitch + abs(fov_down)) / fov  # in [0.0, 1.0]

    # scale to image size using angular resolution
    proj_x *= proj_W  # in [0.0, W]
    proj_y *= proj_H  # in [0.0, H]

    # round and clamp for use as index
    proj_x = np.floor(proj_x)
    proj_x = np.minimum(proj_W - 1, proj_x)
    proj_x = np.maximum(0, proj_x).astype(np.int32)  # in [0,W-1]

    proj_y = np.floor(proj_y)
    proj_y = np.minimum(proj_H - 1, proj_y)
    proj_y = np.maximum(0, proj_y).astype(np.int32)  # in [0,H-1]

    # order in decreasing depth
    order = np.argsort(depth)[::-1]
    depth = depth[order]
    proj_y = proj_y[order]
    proj_x = proj_x[order]

    scan_x = scan_x[order]
    scan_y = scan_y[order]
    scan_z = scan_z[order]

    indices = np.arange(depth.shape[0])
    indices = indices[order]

    proj_range = np.full((proj_H, proj_W), -1,
                         dtype=np.float32)  # [H,W] range (-1 is no data)
    proj_vertex = np.full((proj_H, proj_W, 4), -1,
                          dtype=np.float32)  # [H,W] index (-1 is no data)
    proj_idx = np.full((proj_H, proj_W), -1,
                       dtype=np.int32)  # [H,W] index (-1 is no data)

    proj_range[proj_y, proj_x] = depth
    proj_vertex[proj_y, proj_x] = np.array([scan_x, scan_y, scan_z, np.ones(len(scan_x))]).T
    proj_idx[proj_y, proj_x] = indices

    res = {"proj_range": proj_range, "proj_vertex": proj_vertex, "proj_idx": proj_idx}
    return proj_range, proj_vertex, proj_idx
