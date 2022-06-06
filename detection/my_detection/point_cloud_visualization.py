import os
import open3d
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import cm

WINDOW_WIDTH = 1728
WINDOW_HEIGHT = 972
SETTING_FILE = "./utils/camera_option.json"


def load_view_point(pcd, title):
    vis = open3d.visualization.Visualizer()
    vis.create_window(window_name=title, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
    ctr = vis.get_view_control()
    param = open3d.io.read_pinhole_camera_parameters(SETTING_FILE)
    vis.add_geometry(pcd)

    # vis.get_render_option().load_from_json('renderoption.json')
    # 可视化参数
    opt = vis.get_render_option()
    # opt.background_color = np.asarray([0, 0, 0])
    # opt.point_size = 1
    # opt.show_coordinate_frame = True

    ctr.convert_from_pinhole_camera_parameters(param)
    vis.run()
    vis.destroy_window()


def vis_arr(arr: np.ndarray):
    assert 2 == len(arr.shape)
    assert 3 <= arr.shape[1]
    arr = arr[:, :3]

    # 创建窗口对象
    vis = open3d.visualization.Visualizer()
    # 设置窗口标题
    vis.create_window(window_name="kitti")
    # 设置点云大小
    vis.get_render_option().point_size = 1
    # 设置颜色背景为黑色
    opt = vis.get_render_option()
    opt.background_color = np.asarray([0, 0, 0])

    # 创建点云对象
    pcd = open3d.geometry.PointCloud()
    # 将点云数据转换为Open3d可以直接使用的数据类型
    pcd.points = open3d.utility.Vector3dVector(arr)
    # 设置点的颜色为白色
    pcd.paint_uniform_color([1, 1, 1])
    # 将点云加入到窗口中
    vis.add_geometry(pcd)

    vis.run()
    vis.destroy_window()


def vis_arr_with_label(arr: np.ndarray, label: np.ndarray, title: str = "part of cloud"):
    """
    visualize the point cloud data with labels
    :param arr:             shape (n,3) or (n,4)
    :param label:           shape (n,)
    :param title:           title of the visualization window
    :return:
    """
    assert 2 == len(arr.shape)
    assert 3 <= arr.shape[1]
    assert arr.shape[0] == label.shape[0]

    arr = arr[:, :3]
    max_label = np.max(label)

    # 颜色
    colors = plt.get_cmap("tab20")(label / (max_label if max_label > 0 else 1))

    pt1 = open3d.geometry.PointCloud()
    pt1.points = open3d.utility.Vector3dVector(arr)
    pt1.colors = open3d.utility.Vector3dVector(colors[:, :3])

    # pt1.estimate_normals(search_param=open3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
    # pt1.estimate_normals()
    # open3d.visualization.draw_geometries([pt1], title, width=500, height=500)

    load_view_point(pcd=pt1, title=title)


def vis_arr_with_color(arr: np.ndarray, colors, title: str = "part of cloud", **kwargs):
    """
    visualize the point cloud data with labels
    """
    assert 2 == len(arr.shape)
    assert 3 <= arr.shape[1]
    assert arr.shape[0] == colors.shape[0]

    arr = arr[:, :3]

    # # 颜色
    # colors = plt.get_cmap("tab20")(label / (max_label if max_label > 0 else 1))

    pt1 = open3d.geometry.PointCloud()
    pt1.points = open3d.utility.Vector3dVector(arr)
    pt1.colors = open3d.utility.Vector3dVector(colors[:, :3])

    # pt1.estimate_normals(search_param=open3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
    # pt1.estimate_normals()
    # open3d.visualization.draw_geometries([pt1], title, width=500, height=500, **kwargs)

    load_view_point(pcd=pt1, title=title)


def vis_arr_by_intensity_at_viewpoint(arr: np.ndarray, view_file: str = "utils/camera_option.json",
                                      title: str = "point cloud", **kwargs):
    # visualize
    arr_xyz = arr[:, :3]
    arr_i = arr[:, 3]
    arr_i *= 256.
    arr_i /= 255.
    arr_i *= (1. / .55)
    arr_i = np.clip(arr_i, 0., 1)

    pcd = open3d.geometry.PointCloud()
    pcd.points = open3d.utility.Vector3dVector(arr_xyz)

    cmap = cm.get_cmap('jet')
    colors = cmap(arr_i)
    pcd_colors = colors[:, :3]  # remove alpha
    if kwargs.get("intensity_color", True) is True:
        pcd.colors = open3d.utility.Vector3dVector(pcd_colors)
    else:
        pcd.paint_uniform_color([0.16, 0.5, 0.72])

    fig = plt.figure()
    drawn = plt.scatter(range(arr.shape[0]), arr_i, color=colors)
    cb = fig.colorbar(drawn)  # , extend='both', shrink=1, label="Temperature", pad=0.01)
    # plt.colorbar(drawn)  # , ticks=[0, 0.25, 0.5, 0.75, 1])
    plt.savefig("utils/pt_cloud_color_bar/color-bar-window=%s.png" % title, dpi=200)

    vis = open3d.visualization.Visualizer()
    vis.create_window(window_name=title, width=1728, height=972)
    ctr = vis.get_view_control()
    param = open3d.io.read_pinhole_camera_parameters(view_file)
    vis.add_geometry(pcd)
    opt = vis.get_render_option()
    if kwargs.get("point_size", 10) > 0:
        opt.point_size = 10
    ctr.convert_from_pinhole_camera_parameters(param)
    vis.run()
    vis.destroy_window()


def vis_bin(file: str = "data/seq60_00000.bin"):
    # reference: https://zhuanlan.zhihu.com/p/483414760
    assert os.path.exists(file)
    assert ".bin" == os.path.splitext(file)[1]
    raw_point = np.fromfile("data/seq60_00000.bin", dtype=np.float32).reshape(-1, 4)  # N*[x,y,z,intensity]
    print(raw_point.shape)

    vis_arr(arr=raw_point[:, :3])


def vis_pcd(file: str = "data/0001.pcd"):
    # reference: https://zhuanlan.zhihu.com/p/461993991
    assert os.path.exists(file)
    assert ".pcd" == os.path.splitext(file)[1]

    # read
    pcd = open3d.io.read_point_cloud(filename=file)
    print(pcd)
    # visualize
    open3d.visualization.draw_geometries([pcd])


if "__main__" == __name__:
    vis_pcd()
    vis_bin()
