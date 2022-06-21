import time
import numpy as np
from numba import jit
import open3d
from matplotlib import pyplot as plt

import point_cloud_visualization


def detect_poles(xyz, neighbourthr=0.5, min_point_num=3, dis_thr=0.08, width_thr=10, fov_up=30.67, fov_down=-10.67,
                 proj_H=32, proj_W=250, lowest=0.1, highest=6, lowthr=1.5, highthr=0.7, totalthr=0.6,
                 ratiothr=0.1, anglethr=10.,
                 middle_res: bool = False, visualize: int = -1):
    results = {
        "range_data": None,
        "cluster": {"pt_cloud": None, "pt_cloud_label": None},
        "cluster_filter_1": {"pt_cloud": None, "pt_cloud_label": None},
        "cluster_filter_2": {"pt_cloud": None, "pt_cloud_label": None},
        "cluster_filter_3": {"pt_cloud": None, "pt_cloud_label": None},
    }

    toc1 = time.perf_counter()
    range_data, proj_vertex, proj_idx, xyzi_z_cut, proj_xyzi = range_projection(
        xyz, fov_up=fov_up, fov_down=fov_down,
        proj_H=proj_H, proj_W=proj_W,
        max_range=50,
        cut_z=True,
        low=lowest, high=highest)
    results["range_data"] = range_data
    print("Range Projection Finished. Projected into", range_data.shape)
    # np.save("range_data.npy", range_data)
    # exit()

    height = range_data.shape[0]
    width = range_data.shape[1]

    # === 1 === generate clusters
    open_set = gen_open_set(range_data, height, width)
    open_set = np.array(open_set)

    clusters = gen_clusters(open_set, range_data, height, width, min_point_num=min_point_num, dis_thr=dis_thr)
    print("Raw Clustering Finished with %d Clusters" % len(clusters))
    toc2 = time.perf_counter()
    print("cluster:", toc2 - toc1)
    toc1 = time.perf_counter()

    # === 1 visualize
    if middle_res:
        mid_pt_cloud = np.zeros((0, 3))  # x,y,z location only
        mid_pt_cloud_xyzi = np.zeros((0, 4))  # x,y,z,i
        mid_pt_cloud_label = np.zeros((0,))  # labels
        for _cluster_idx, _cluster in enumerate(clusters):  # <int>, <np.ndarray> (shape=(n,2), dtype=float64)
            for __range_img_index in _cluster:  # <np.ndarray> (shape=(n,2), dtype=float64)
                __range_img_index = [int(__range_img_index[0]), int(__range_img_index[1])]
                __xyzi = proj_vertex[__range_img_index[0]][__range_img_index[1]]
                mid_pt_cloud = np.append(mid_pt_cloud, __xyzi[:3]).reshape(-1, 3)
                for ___xyzi in proj_xyzi[__range_img_index[0]][__range_img_index[1]]:
                    mid_pt_cloud_xyzi = np.append(mid_pt_cloud_xyzi, ___xyzi).reshape(-1, 4)
                mid_pt_cloud_label = np.append(mid_pt_cloud_label, _cluster_idx)
        results["cluster"]["pt_cloud"] = mid_pt_cloud
        results["cluster"]["pt_cloud_label"] = mid_pt_cloud_label
        if -1 < visualize <= 1:
            point_cloud_visualization.vis_arr_with_label(arr=mid_pt_cloud, label=mid_pt_cloud_label,
                                                         title="Point Cloud after Raw Clustering")
            point_cloud_visualization.vis_arr_by_intensity_at_viewpoint(
                arr=mid_pt_cloud_xyzi, title="0-1-Point Cloud after Raw Clustering",
                view_file="utils/camera-plate.json", intensity_color=True)

    # === 2 === [ROUND 1] filter out some clusters by: ratio, smaller distance points ratio
    clusters_list = []  # result for round 1 filtering
    for cluster in clusters:
        clusters_list.append(cluster.tolist())

    res_mid_cluster_list = []
    res_mid_cluster_label = []
    _res_mid_cluster_labels = {"ratio&small": 0, "z&circle": 1, "plane": 2}
    clusters_copy = list(clusters_list)
    for cluster in clusters_copy:  # <list> of "shape" (n,2)
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

        # if ratio < 1.0 or delate > 0.3 * len(cluster) or (max_width - min_width + 1) > width_thr:
        if ratio < 1.0 - ratiothr or ratio > 1.0 + ratiothr or \
                delate > 0.05 * len(cluster) or (max_width - min_width + 1) > width_thr:
            clusters_list.remove(cluster)
            if middle_res:
                res_mid_cluster_list.append(cluster)
                res_mid_cluster_label.append(_res_mid_cluster_labels["ratio&small"])

    print("Round 1 Cluster Filtering Finished. Clusters: %d => %d (%d filtered)"
          % (len(clusters), len(clusters_list), len(clusters) - len(clusters_list)))

    # === 2 visualize
    if middle_res:
        mid_pt_cloud = np.zeros((0, 3))  # x,y,z location only
        mid_pt_cloud_xyzi = np.zeros((0, 4))  # x,y,z,i
        mid_pt_cloud_label = np.zeros((0,))  # labels
        for _cluster_idx, _cluster in enumerate(clusters_list):  # <int>, <np.ndarray> (shape=(n,2), dtype=float64)
            for __range_img_index in _cluster:  # <np.ndarray> (shape=(n,2), dtype=float64)
                __range_img_index = [int(__range_img_index[0]), int(__range_img_index[1])]
                __xyzi = proj_vertex[__range_img_index[0]][__range_img_index[1]]
                mid_pt_cloud = np.append(mid_pt_cloud, __xyzi[:3]).reshape(-1, 3)
                for ___xyzi in proj_xyzi[__range_img_index[0]][__range_img_index[1]]:
                    mid_pt_cloud_xyzi = np.append(mid_pt_cloud_xyzi, ___xyzi).reshape(-1, 4)
                mid_pt_cloud_label = np.append(mid_pt_cloud_label, _cluster_idx)
        results["cluster_filter_1"]["pt_cloud"] = mid_pt_cloud
        results["cluster_filter_1"]["pt_cloud_label"] = mid_pt_cloud_label
        if -1 < visualize <= 2:
            point_cloud_visualization.vis_arr_with_label(arr=mid_pt_cloud, label=mid_pt_cloud_label,
                                                         title="Point Cloud after Round 1 Cluster Filtering")
            point_cloud_visualization.vis_arr_by_intensity_at_viewpoint(
                arr=mid_pt_cloud_xyzi, title="0-2-Point Cloud after Round 1 Cluster Filtering",
                view_file="utils/camera-plate.json", intensity_color=True)

    # === 3 === filter out some clusters by: z_min/max, circle
    clusters_list_filter_2 = list(clusters_list)  # result for round 2 filtering
    clusters_list_copy = list(clusters_list)
    # poleparams = np.empty([0, 3])
    for cluster in clusters_list_copy:
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
        if fit_circle(x, y) != None:
            average_x, average_y, R_1 = fit_circle(x, y)
            fine_thr = R_1 + 0.1
            scan_x = xyz[:, 0]
            scan_y = xyz[:, 1]
            scan_z = xyz[:, 2]

            high = min(high, 3.0)

            current_vertex_fine = xyz[
                (scan_x > (average_x - fine_thr)) & (scan_x < (average_x + fine_thr))
                & (scan_y < (average_y + fine_thr)) & (scan_y > (average_y - fine_thr))
                & (scan_z < high) & (scan_z > low)
                ]
            x = []
            y = []
            for i in range(current_vertex_fine.shape[0]):
                x.append(current_vertex_fine[i, 0])
                y.append(current_vertex_fine[i, 1])
            if len(x) >= 6:
                if fit_circle(x, y) != None:
                    xc_1, yc_1, R_1 = fit_circle(x, y)
                    if R_1 > 0.02 and R_1 < 0.4:
                        neighbour = xyz[
                            (
                                    (
                                            (scan_x > (average_x - fine_thr - neighbourthr))
                                            & (scan_x < (average_x - fine_thr))
                                    )
                                    | (
                                            (scan_x > (average_x + fine_thr))
                                            & (scan_x < (average_x + fine_thr + neighbourthr))
                                    )
                            )
                            & (
                                    (
                                            (scan_y > (average_y + fine_thr - neighbourthr))
                                            & (scan_y < (average_y - fine_thr))
                                    )
                                    | (
                                            (scan_y > (average_y + fine_thr))
                                            & (scan_y < (average_y + fine_thr + neighbourthr))
                                    )
                            )
                            & (scan_z < high) & (scan_z > low)
                            ]
                        if neighbour.shape[0] < 0.15 * current_vertex_fine.shape[0]:
                            # poleparams = np.vstack([poleparams, [xc_1, yc_1, R_1]])
                            pass
                        else:
                            clusters_list_filter_2.remove(cluster)
                            if middle_res:
                                res_mid_cluster_list.append(cluster)
                                res_mid_cluster_label.append(_res_mid_cluster_labels["z&circle"])

    print("Round 2 Cluster Filtering Finished. Clusters: %d => %d (%d filtered)"
          % (len(clusters_list), len(clusters_list_filter_2), len(clusters_list) - len(clusters_list_filter_2)))

    # === 3 visualize
    if middle_res:
        mid_pt_cloud = np.zeros((0, 3))  # x,y,z location only
        mid_pt_cloud_xyzi = np.zeros((0, 4))  # x,y,z,i
        mid_pt_cloud_label = np.zeros((0,))  # labels
        for _cluster_idx, _cluster in enumerate(
                clusters_list_filter_2):  # <int>, <np.ndarray> (shape=(n,2), dtype=float64)
            for __range_img_index in _cluster:  # <np.ndarray> (shape=(n,2), dtype=float64)
                __range_img_index = [int(__range_img_index[0]), int(__range_img_index[1])]
                __xyzi = proj_vertex[__range_img_index[0]][__range_img_index[1]]
                mid_pt_cloud = np.append(mid_pt_cloud, __xyzi[:3]).reshape(-1, 3)
                for ___xyzi in proj_xyzi[__range_img_index[0]][__range_img_index[1]]:
                    mid_pt_cloud_xyzi = np.append(mid_pt_cloud_xyzi, ___xyzi).reshape(-1, 4)
                mid_pt_cloud_label = np.append(mid_pt_cloud_label, _cluster_idx)
        results["cluster_filter_2"]["pt_cloud"] = mid_pt_cloud
        results["cluster_filter_2"]["pt_cloud_label"] = mid_pt_cloud_label
        if -1 < visualize <= 3:
            point_cloud_visualization.vis_arr_with_label(arr=mid_pt_cloud, label=mid_pt_cloud_label,
                                                         title="Point Cloud after Round 2 Cluster Filtering")
            point_cloud_visualization.vis_arr_by_intensity_at_viewpoint(
                arr=mid_pt_cloud_xyzi, title="0-3-Point Cloud after Round 2 Cluster Filtering",
                view_file="utils/camera-plate.json", intensity_color=True)

    # === 4 === filter out some clusters by: angle between normal vectors and the horizontal surface
    clusters_list_filter_3 = list(clusters_list_filter_2)  # result for round 3 filtering
    clusters_list_copy = list(clusters_list_filter_2)
    for cluster in clusters_list_copy:
        cluster_pt_cloud_points = np.zeros((0, 3))
        for index in cluster:
            index = [int(index[0]), int(index[1])]
            __xyzi = proj_vertex[index[0]][index[1]]
            cluster_pt_cloud_points = np.append(cluster_pt_cloud_points, __xyzi[:3]).reshape(-1, 3)

        pt_cloud_obj = open3d.geometry.PointCloud(points=open3d.utility.Vector3dVector(cluster_pt_cloud_points))
        # doc: http://www.open3d.org/docs/release/python_api/open3d.geometry.PointCloud.html#open3d.geometry.PointCloud.estimate_normals
        pt_cloud_obj.estimate_normals()
        normal_vectors = np.asarray(pt_cloud_obj.normals)  # shape (n,3), seem to be normed, i.e., norm = 1
        normal_vectors_normed = normal_vectors / np.linalg.norm(normal_vectors, axis=1, keepdims=True)  # shape (n,3)
        # reference: https://stackoverflow.com/questions/2827393/angles-between-two-n-dimensional-vectors-in-python
        angle_to_hori = np.arccos(
            np.clip(np.dot(normal_vectors_normed, np.array([0, 0, 1])), -1.0, 1.0))  # shape (n,3), in radian, [0, PI]
        angle_to_hori = angle_to_hori / np.pi * 180.  # shape (n,3), in degrees
        angle_to_hori_mean = np.mean(angle_to_hori)

        if 90. - anglethr <= angle_to_hori_mean <= 90. + anglethr:
            pass
        else:
            clusters_list_filter_3.remove(cluster)
            if middle_res:
                res_mid_cluster_list.append(cluster)
                res_mid_cluster_label.append(_res_mid_cluster_labels["plane"])

    print("Round 3 Cluster Filtering Finished. Clusters: %d => %d (%d filtered)"
          % (len(clusters_list_filter_2), len(clusters_list_filter_3),
             len(clusters_list_filter_2) - len(clusters_list_filter_3)))

    # === 4 visualize
    if middle_res:
        mid_pt_cloud = np.zeros((0, 3))  # x,y,z location only
        mid_pt_cloud_xyzi = np.zeros((0, 4))  # x,y,z,i
        mid_pt_cloud_label = np.zeros((0,))  # labels
        for _cluster_idx, _cluster in enumerate(
                clusters_list_filter_3):  # <int>, <np.ndarray> (shape=(n,2), dtype=float64)
            for __range_img_index in _cluster:  # <np.ndarray> (shape=(n,2), dtype=float64)
                __range_img_index = [int(__range_img_index[0]), int(__range_img_index[1])]
                __xyzi = proj_vertex[__range_img_index[0]][__range_img_index[1]]  # intensity is 1
                mid_pt_cloud = np.append(mid_pt_cloud, __xyzi[:3]).reshape(-1, 3)
                for ___xyzi in proj_xyzi[__range_img_index[0]][__range_img_index[1]]:
                    mid_pt_cloud_xyzi = np.append(mid_pt_cloud_xyzi, ___xyzi).reshape(-1, 4)
                mid_pt_cloud_label = np.append(mid_pt_cloud_label, _cluster_idx)
        results["cluster_filter_3"]["pt_cloud"] = mid_pt_cloud
        results["cluster_filter_3"]["pt_cloud_label"] = mid_pt_cloud_label
        if -1 < visualize <= 4:
            point_cloud_visualization.vis_arr_with_label(arr=mid_pt_cloud, label=mid_pt_cloud_label,
                                                         title="Point Cloud after Round 3 Cluster Filtering")
            point_cloud_visualization.vis_arr_by_intensity_at_viewpoint(
                arr=mid_pt_cloud_xyzi, title="0-4-Point Cloud after Round 3 Cluster Filtering",
                view_file="utils/camera-plate.json", intensity_color=True)

    # all visualize
    if middle_res:
        mid_pt_cloud = np.zeros((0, 3))  # x,y,z location only
        mid_pt_cloud_colors = np.zeros((0, 4))  # labels
        _cnt_groups = len(_res_mid_cluster_labels.keys())
        _candidate_colors = plt.get_cmap("Pastel2")(np.arange(_cnt_groups) / 1. / _cnt_groups)[::-1,
                            :]  # Set2 or Pastel2
        _candidate_colors[:, -1] = 0.3  # alpha
        _remain_color = np.array([1., 0., 0., 1.])
        # add removed clusters
        for _cluster, _cluster_label in zip(
                res_mid_cluster_list, res_mid_cluster_label):  # <np.ndarray> (shape=(n,2), dtype=float64), <int>
            for __range_img_index in _cluster:  # <np.ndarray> (shape=(n,2), dtype=float64)
                __range_img_index = [int(__range_img_index[0]), int(__range_img_index[1])]
                __xyzi = proj_vertex[__range_img_index[0]][__range_img_index[1]]
                mid_pt_cloud = np.append(mid_pt_cloud, __xyzi[:3]).reshape(-1, 3)
                mid_pt_cloud_colors = np.append(mid_pt_cloud_colors, _candidate_colors[_cluster_label]).reshape(-1, 4)
        # add result clusters
        for _cluster in clusters_list_filter_3:  # <np.ndarray> (shape=(n,2), dtype=float64)
            for __range_img_index in _cluster:  # <np.ndarray> (shape=(n,2), dtype=float64)
                __range_img_index = [int(__range_img_index[0]), int(__range_img_index[1])]
                __xyzi = proj_vertex[__range_img_index[0]][__range_img_index[1]]
                mid_pt_cloud = np.append(mid_pt_cloud, __xyzi[:3]).reshape(-1, 3)
                mid_pt_cloud_colors = np.append(mid_pt_cloud_colors, _remain_color).reshape(-1, 4)
        point_cloud_visualization.vis_arr_with_color(arr=mid_pt_cloud, colors=mid_pt_cloud_colors,
                                                     title="Point Cloud Filtering Result")

    # construct clusters of points with xyzi for return
    res_cluster_points = []  # <list>of<np.ndarray>, each of shape (n,4)
    for _cluster in clusters_list_filter_3:  # <np.ndarray> (shape=(n,2), dtype=float64)
        pt_xyzi = np.zeros((0, 4), dtype=np.float32)  # dtype=np.float64
        for __range_img_index in _cluster:  # <np.ndarray> (shape=(n,2), dtype=float64)
            # __range_img_index = [int(__range_img_index[0]), int(__range_img_index[1])]
            # __raw_pt_cloud_index = proj_idx[__range_img_index[0]][__range_img_index[1]]
            # __xyzi = xyzi_z_cut[__raw_pt_cloud_index]
            # # __xyzi = proj_vertex[__range_img_index[0]][__range_img_index[1]]
            # pt_xyzi = np.append(pt_xyzi, __xyzi).reshape(-1, 4)
            __range_img_index = [int(__range_img_index[0]), int(__range_img_index[1])]
            for ___xyzi in proj_xyzi[__range_img_index[0]][__range_img_index[1]]:
                pt_xyzi = np.append(pt_xyzi, ___xyzi).reshape(-1, 4)
        res_cluster_points.append(pt_xyzi)

    toc2 = time.perf_counter()
    print("cluster filter:", toc2 - toc1)
    toc1 = time.perf_counter()

    return res_cluster_points, results


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

    # proj_dup_cnt = np.zeros((proj_H, proj_W), dtype=int)
    # for _proj_y, _proj_x in zip(proj_y, proj_x):
    #     proj_dup_cnt[_proj_y, _proj_x] += 1
    # np.save("tests/points_proj_dup_cnt.npy", proj_dup_cnt)
    proj_all_vertex = [[[] for _ in range(proj_W)] for _ in range(proj_H)]
    current_vertex_reordered = current_vertex[order]
    for _vertex_idx in range(current_vertex.shape[0]):
        _proj_y, _proj_x = proj_y[_vertex_idx], proj_x[_vertex_idx]
        _vertex_xyzi = current_vertex_reordered[_vertex_idx]
        proj_all_vertex[_proj_y][_proj_x].append(_vertex_xyzi)

    proj_range[proj_y, proj_x] = depth
    proj_vertex[proj_y, proj_x] = np.array([scan_x, scan_y, scan_z, np.ones(len(scan_x))]).T
    proj_idx[proj_y, proj_x] = indices

    # res = {"proj_range": proj_range, "proj_vertex": proj_vertex, "proj_idx": proj_idx}
    return proj_range, proj_vertex, proj_idx, current_vertex, proj_all_vertex


def fit_circle(x, y):
    x_m = sum(x) / len(x)
    y_m = sum(y) / len(y)
    u = x - x_m
    v = y - y_m
    # linear system defining the center in reduced coordinates (uc, vc):
    #    Suu * uc +  Suv * vc = (Suuu + Suvv)/2
    #    Suv * uc +  Svv * vc = (Suuv + Svvv)/2
    Suv = sum(u * v)
    Suu = sum(u ** 2)
    Svv = sum(v ** 2)
    Suuv = sum(u ** 2 * v)
    Suvv = sum(u * v ** 2)
    Suuu = sum(u ** 3)
    Svvv = sum(v ** 3)

    # Solving the linear system
    A = np.array([[Suu, Suv], [Suv, Svv]])
    B = np.array([Suuu + Suvv, Svvv + Suuv]) / 2.0

    if np.linalg.det(A) != 0:
        uc, vc = np.linalg.solve(A, B)
        xc_1 = x_m + uc
        yc_1 = y_m + vc
        # Calculation of all distances from the center (xc_1, yc_1)
        Ri_1 = np.sqrt((x - xc_1) ** 2 + (y - yc_1) ** 2)
        R_1 = np.mean(Ri_1)
        return xc_1, yc_1, R_1

    return None
