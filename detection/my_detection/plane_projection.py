import time
import numpy as np
import open3d
from matplotlib import pyplot as plt
from sklearn import linear_model

from simulation.utils import dist_2_margin
import point_cloud_visualization


def display_inlier_outlier(cloud, ind):
    # copied from: http://www.open3d.org/docs/release/tutorial/geometry/pointcloud_outlier_removal.html
    inlier_cloud = cloud.select_by_index(ind)
    outlier_cloud = cloud.select_by_index(ind, invert=True)

    # print("Showing outliers (red) and inliers (gray): ")
    outlier_cloud.paint_uniform_color([1, 0, 0])
    inlier_cloud.paint_uniform_color([0.8, 0.8, 0.8])
    open3d.visualization.draw_geometries([inlier_cloud, outlier_cloud],
                                         # zoom=0.3412,
                                         # front=[0.4257, -0.2125, -0.8795],
                                         # lookat=[2.6172, 2.0475, 1.532],
                                         # up=[-0.0694, -0.9768, 0.2024]
                                         )


def project_onto_plane(pcd: open3d.geometry.PointCloud, p_a, p_b, p_c, p_d, x0=0, y0=0, z0=0):
    # copied from: https://blog.ekbana.com/planar-and-spherical-projections-of-a-point-cloud-d796db76563e
    source, A, B, C, D, x0, y0, z0 = pcd, p_a, p_b, p_c, p_d, x0, y0, z0
    x1 = np.asarray(source.points)[:, 0]
    y1 = np.asarray(source.points)[:, 1]
    z1 = np.asarray(source.points)[:, 2]
    x0 = x0 * np.ones(x1.size)
    y0 = y0 * np.ones(y1.size)
    z0 = z0 * np.ones(z1.size)
    r = np.power(np.square(x1 - x0) + np.square(y1 - y0) + np.square(z1 - z0), 0.5)
    a = (x1 - x0) / r
    b = (y1 - y0) / r
    c = (z1 - z0) / r
    t = -1 * (A * np.asarray(source.points)[:, 0] + B * np.asarray(source.points)[:, 1] + C * np.asarray(source.points)[
                                                                                              :, 2] + D)
    t = t / (a * A + b * B + c * C)
    np.asarray(source.points)[:, 0] = x1 + a * t
    np.asarray(source.points)[:, 1] = y1 + b * t
    np.asarray(source.points)[:, 2] = z1 + c * t
    return source


def project_onto_plane_arr(arr, p_a, p_b, p_c, p_d, x0=0, y0=0, z0=0):
    # modified from: https://blog.ekbana.com/planar-and-spherical-projections-of-a-point-cloud-d796db76563e
    source, A, B, C, D, x0, y0, z0 = arr.copy(), p_a, p_b, p_c, p_d, x0, y0, z0
    x1 = source[:, 0]
    y1 = source[:, 1]
    z1 = source[:, 2]
    x0 = x0 * np.ones(x1.size)
    y0 = y0 * np.ones(y1.size)
    z0 = z0 * np.ones(z1.size)
    r = np.power(np.square(x1 - x0) + np.square(y1 - y0) + np.square(z1 - z0), 0.5)
    a = (x1 - x0) / r
    b = (y1 - y0) / r
    c = (z1 - z0) / r
    t = -1 * (A * source[:, 0] + B * source[:, 1] + C * source[:, 2] + D)
    t = t / (a * A + b * B + c * C)
    arr[:, 0] = x1 + a * t
    arr[:, 1] = y1 + b * t
    arr[:, 2] = z1 + c * t
    return arr


def dist_point_2_plane(x, y, z, p_a, p_b, p_c, p_d):
    x1, y1, z1, a, b, c, d = x, y, z, p_a, p_b, p_c, p_d

    d = abs((a * x1 + b * y1 + c * z1 + d))
    e = np.sqrt(a * a + b * b + c * c)
    res = d / e
    return res


def handler(xyzi, dist_thresh=0.05,
            intthr=0.3,
            hori_angle_resol=0.1, vert_angle_resol=0.33, pixel_margin=50,
            visualize=-1, validate=True):
    toc1 = time.perf_counter()

    xyz = xyzi[:, :3]

    if False:
        _xyz_off_board = xyz[np.where(xyz[:, 0] < -10)]
        _xyz_on_board = xyz[np.where(xyz[:, 0] > -10)]
        _pcd_off = open3d.geometry.PointCloud(points=open3d.utility.Vector3dVector(_xyz_off_board))
        _pcd_on = open3d.geometry.PointCloud(points=open3d.utility.Vector3dVector(_xyz_on_board))

        # print("Showing outliers (red) and inliers (gray): ")
        _pcd_off.paint_uniform_color([1, 1, 0])  # yellow
        _pcd_on.paint_uniform_color([1, 0, 0])  # red

        vis = open3d.visualization.Visualizer()
        vis.create_window(window_name="On-Off Board Points", width=1728, height=972)
        ctr = vis.get_view_control()
        param = open3d.io.read_pinhole_camera_parameters("utils/camera-plate.json")
        vis.add_geometry(_pcd_off)
        vis.add_geometry(_pcd_on)
        opt = vis.get_render_option()
        opt.point_size = 10
        ctr.convert_from_pinhole_camera_parameters(param)
        vis.run()
        vis.destroy_window()
        np.save("points_xyz_off_board.npy", _xyz_off_board)
        np.save("points_xyz_on_board.npy", _xyz_on_board)
        print(end="")

    if -1 < visualize <= 1:
        # open3d.visualization.draw_geometries([open3d.geometry.PointCloud(points=open3d.utility.Vector3dVector(xyz))])
        point_cloud_visualization.vis_arr_by_intensity_at_viewpoint(arr=xyzi, title="1-raw plate",
                                                                    view_file="utils/camera-plate.json",
                                                                    intensity_color=True)
        # viewer = open3d.visualization.Visualizer()
        # viewer.create_window(window_name="Raw Points")
        # viewer.add_geometry(xyzi2pc(xyz=xyzi[:, :3], intensities=intensity2color(xyzi[:, 3])))
        # opt = viewer.get_render_option()
        # opt.show_coordinate_frame = True
        # viewer.run()
        # viewer.destroy_window()

    # np.save("points.npy", xyz)

    # === 1 === fit a plane
    # reference: http://www.open3d.org/docs/latest/tutorial/Basic/pointcloud.html#Plane-segmentation
    # doc: http://www.open3d.org/docs/latest/python_api/open3d.geometry.PointCloud.html?highlight=segment_plane#open3d.geometry.PointCloud.segment_plane
    pcd = open3d.geometry.PointCloud(points=open3d.utility.Vector3dVector(xyz))
    plane_model, inliers = pcd.segment_plane(distance_threshold=dist_thresh,
                                             ransac_n=3,
                                             num_iterations=1000)
    [plane_a, plane_b, plane_c, plane_d] = plane_model
    print("Plane Fit as: %fx + %fy + %fz + %f = 0" % (plane_a, plane_b, plane_c, plane_d))
    pcd_proc = pcd.select_by_index(inliers)
    xyzi_fit = xyzi[inliers]  # 3d points, shape (n,4); identity assured (see below)
    if validate:  # check whether points from `pcd_rmv` are identical with those in `xyzi_rmv`
        _pts_pcd = np.asarray(pcd_proc.points)  # .tolist()
        _pts_ori = xyzi_fit[:, :3]  # .tolist()
        print("[after Plane Fit Removal] Pts from PCD == Pts from Raw Data Sliced by Inliers' Indices:",
              np.array_equal(_pts_pcd, _pts_ori))

    # if -1 < visualize <= 2:
    #     # open3d.visualization.draw_geometries([open3d.geometry.PointCloud(points=open3d.utility.Vector3dVector(xyz))])
    #     point_cloud_visualization.vis_arr_by_intensity_at_viewpoint(arr=xyzi_fit, title="1.5-fit plane",
    #                                                                 view_file="utils/camera-plate.json",
    #                                                                 intensity_color=True)

    XY = xyz[:, :]
    Z = xyz[:, 2]
    ransac = linear_model.RANSACRegressor(
        linear_model.LinearRegression(),
        residual_threshold=0.1
    )
    ransac.fit(XY, Z)
    coeff = ransac.estimator_.coef_
    print(coeff)
    intercept = ransac.estimator_.intercept_
    print(intercept)

    # === 2 === remove outliers
    # reference: http://www.open3d.org/docs/release/tutorial/geometry/pointcloud_outlier_removal.html
    # doc: http://www.open3d.org/docs/release/python_api/open3d.geometry.PointCloud.html?highlight=remove_statistical_outlier#open3d.geometry.PointCloud.remove_statistical_outlier
    pcd_rmv, _pcd_inlier_idx = pcd_proc.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)
    xyzi_rmv = xyzi_fit[_pcd_inlier_idx]  # 3d points, shape (n,4); identity assured (see below)
    if validate:  # check whether points from `pcd_rmv` are identical with those in `xyzi_rmv`
        _pts_pcd = np.asarray(pcd_rmv.points)  # .tolist()
        _pts_ori = xyzi_rmv[:, :3]  # .tolist()
        print("[after Removal] Pts from PCD == Pts from Raw Data Sliced by Inliers' Indices:",
              np.array_equal(_pts_pcd, _pts_ori))

    if -1 < visualize <= 2:
        point_cloud_visualization.vis_arr_by_intensity_at_viewpoint(arr=xyzi_rmv, title="2-after removal",
                                                                    view_file="utils/camera-plate.json",
                                                                    intensity_color=True)
        # viewer = open3d.visualization.Visualizer()
        # viewer.create_window(window_name="After Removal Sliced from Raw Points")
        # viewer.add_geometry(xyzi2pc(xyz=xyzi_rmv[:, :3], intensities=xyzi_rmv[:, 3]))
        # opt = viewer.get_render_option()
        # opt.show_coordinate_frame = True
        # viewer.run()
        # viewer.destroy_window()
        inlier_cloud = pcd_rmv.select_by_index(_pcd_inlier_idx)
        outlier_cloud_1 = pcd.select_by_index(inliers, invert=True)
        outlier_cloud_2 = pcd_proc.select_by_index(_pcd_inlier_idx, invert=True)

        # print("Showing outliers (red) and inliers (gray): ")
        outlier_cloud_1.paint_uniform_color([1, 1, 0])  # yellow
        outlier_cloud_2.paint_uniform_color([1, 0, 0])  # red
        inlier_cloud.paint_uniform_color([0.8, 0.8, 0.8])  # grey

        vis = open3d.visualization.Visualizer()
        vis.create_window(window_name="Point Removals", width=1728, height=972)
        ctr = vis.get_view_control()
        param = open3d.io.read_pinhole_camera_parameters("utils/camera-plate.json")
        vis.add_geometry(inlier_cloud)
        vis.add_geometry(outlier_cloud_1)
        vis.add_geometry(outlier_cloud_2)
        opt = vis.get_render_option()
        opt.point_size = 10
        ctr.convert_from_pinhole_camera_parameters(param)
        vis.run()
        vis.destroy_window()

    # === 3 === project onto the fit plane
    xyzi_rmv_proj = project_onto_plane_arr(arr=xyzi_rmv, p_a=plane_a, p_b=plane_b, p_c=plane_c, p_d=plane_d,
                                           x0=0, y0=0, z0=0)  # 3d-like 2d points, shape (n,4)
    if validate:
        _pcd_rmv_proj = project_onto_plane(pcd=pcd_rmv, p_a=plane_a, p_b=plane_b, p_c=plane_c, p_d=plane_d,
                                           x0=0, y0=0, z0=0)
        _pts_pcd = np.asarray(_pcd_rmv_proj.points)
        _pts_ori = xyzi_rmv_proj[:, :3]
        print("[after Projection] Pts by PCD == Pts by Array:", np.array_equal(_pts_pcd, _pts_ori))
    xyi_rmv_proj = xyzi[:, [0, 1, 3]]  # remove z-axis, shape (n,3)

    if -1 < visualize <= 3:
        point_cloud_visualization.vis_arr_by_intensity_at_viewpoint(arr=xyzi_rmv_proj, title="3-after projection",
                                                                    view_file="utils/camera-plate.json",
                                                                    intensity_color=True)
        # viewer = open3d.visualization.Visualizer()
        # viewer.create_window(window_name="After Projection")
        # viewer.add_geometry(xyzi2pc(xyz=xyzi_rmv_proj[:, :3], intensities=xyzi_rmv_proj[:, 3]))
        # opt = viewer.get_render_option()
        # opt.show_coordinate_frame = True
        # viewer.run()
        # viewer.destroy_window()
        # open3d.visualization.draw_geometries([xyzi2pc(xyz=xyzi_rmv_proj[:, :3], intensities=xyzi_rmv_proj[:, 3])],
        #                                      window_name="After Projection")

    # === 4 === thresh to binary
    xyi_rmv_proj_bin = xyi_rmv_proj.copy()
    xyi_rmv_proj_bin[np.where(xyi_rmv_proj[:, 2] > intthr), 2] = 1
    xyi_rmv_proj_bin[np.where(xyi_rmv_proj[:, 2] <= intthr), 2] = 0

    if -1 < visualize <= 4:
        fig = plt.figure()
        # === subplot 1: raw points + fit plane
        # raw points
        ax1 = fig.add_subplot(111, projection='3d')
        # ax1.scatter(xyz[:, 0], xyz[:, 1], xyz[:, 2], s=10, c="red", marker='.')
        ax1.set_xlabel('x'), ax1.set_ylabel('y'), ax1.set_zlabel('z')
        # normal vector of the fit plane
        plane_norm = np.array([plane_a, plane_b, plane_c])  # already normed
        x_start, y_start, z_start = np.mean(xyz[:, 0]), np.mean(xyz[:, 1]), np.mean(xyz[:, 2])
        plot_norm_len = 5
        ax1.quiver(x_start, y_start, z_start,
                   x_start + plane_norm[0] * plot_norm_len,
                   y_start + plane_norm[1] * plot_norm_len,
                   z_start + plane_norm[2] * plot_norm_len,
                   arrow_length_ratio=0.1)
        # fit plane
        # xx = np.arange(np.min(xyz[:, 0]), np.max(xyz[:, 0]), 0.05)  # (min,max)=(-3.586, -3.383)
        # yy = np.arange(np.min(xyz[:, 1]), np.max(xyz[:, 1]), 0.05)  # (min,max)=(0.087, 0.611)
        xx = xyz[:, 0]
        yy = xyz[:, 1]
        X, Y = np.meshgrid(xx, yy)
        Z = (plane_a * X + plane_b * Y + plane_d) * 1. / plane_c
        # z = lambda x, y: (-ransac.estimator_.intercept_ - ransac.estimator_.coef_[0] * x
        #                   - ransac.estimator_.coef_[1] * y) / ransac.estimator_.coef_[2]
        # Z = z(X, Y)
        print(X[0][:10])
        print(Y[0][:10])
        print(xyz[:, 2][:10])
        print(Z[0][:10])
        ax1.plot_surface(X, Y, Z, color="lightgrey", alpha=0.2)  # ,cmap='rainbow')
        plt.show()

    # === 5 === splat into grids
    dist = dist_point_2_plane(x=0, y=0, z=0, p_a=plane_a, p_b=plane_b, p_c=plane_c, p_d=plane_d)  # in m
    hori_margin = dist_2_margin(dist=dist, angle_resol=hori_angle_resol)  # in mm
    vert_margin = dist_2_margin(dist=dist, angle_resol=vert_angle_resol)  # in mm
    print("Margins at Distance=%f(m) are: vert=%d(mm), hori=%d(mm)" % (dist, vert_margin, hori_margin))

    scan_x = xyi_rmv_proj_bin[:, 0]  # in meters
    scan_y = xyi_rmv_proj_bin[:, 1]  # in meters
    scan_i = xyi_rmv_proj_bin[:, 2]
    scan_x_min = np.min(scan_x)
    scan_y_min = np.min(scan_y)

    proj_x = np.round((scan_x - scan_x_min) * 1000. / vert_margin).astype(int)
    proj_y = np.round((scan_y - scan_y_min) * 1000. / hori_margin).astype(int)
    proj_x -= np.min(proj_x)
    proj_y -= np.min(proj_y)
    # proj_x = np.round((scan_x - scan_x_min) * 1000.).astype(int)
    # proj_y = np.round((scan_y - scan_y_min) * 1000.).astype(int)
    # binary intensity for each pixel (-1 is no data)
    xyi_rmv_proj_bin_grid = np.full((np.max(proj_y) + 1, np.max(proj_x) + 1), -1, dtype=int)
    xyi_rmv_proj_bin_grid[proj_y, proj_x] = scan_i

    np.save("plot_binary/binary.npy", xyi_rmv_proj_bin_grid)

    toc2 = time.perf_counter()
    print("project + binarization:", toc2 - toc1)

    return None


def intensity2color(intensity):
    return np.tile(np.reshape(intensity * 0.8, [-1, 1]), [1, 3])


def xyzi2pc(xyz, intensities=None):
    pc = open3d.geometry.PointCloud()
    pc.points = open3d.utility.Vector3dVector(xyz)
    if intensities is not None:
        pc.colors = open3d.utility.Vector3dVector(intensity2color(intensities / 255.0))
    return pc
