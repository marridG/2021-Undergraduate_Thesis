import os
import numpy as np
import struct
import open3d
import time

from open3d import visualization


def read_bin_velodyne(path):
    pc_list = []
    with open(path, 'rb') as f:
        content = f.read()
        pc_iter = struct.iter_unpack('ffff', content)
        for idx, point in enumerate(pc_iter):
            pc_list.append([point[0], point[1], point[2]])
    return np.asarray(pc_list, dtype=np.float32)


def save_view_point(pcd, filename):
    vis = visualization.Visualizer()
    vis.create_window(window_name='pcd', width=1728, height=972)
    vis.add_geometry(pcd)

    vis.get_render_option().load_from_json('renderoption.json')
    vis.run()  # user changes the view and press "q" to terminate
    param = vis.get_view_control().convert_to_pinhole_camera_parameters()
    open3d.io.write_pinhole_camera_parameters(filename, param)
    # vis.destroy_window()


def load_view_point(pcd, filename):
    vis = visualization.Visualizer()
    vis.create_window(window_name='pcd', width=1728, height=972)
    ctr = vis.get_view_control()
    param = open3d.io.read_pinhole_camera_parameters(filename)
    vis.add_geometry(pcd)
    vis.get_render_option().load_from_json('renderoption.json')
    ctr.convert_from_pinhole_camera_parameters(param)
    vis.run()
    vis.destroy_window()


if __name__ == "__main__":
    example = read_bin_velodyne("../data/seq60_00000.bin")  # 传入自己当前的pcd文件
    pcd = open3d.geometry.PointCloud()
    pcd.points = open3d.utility.Vector3dVector(example)
    save_view_point(pcd, "BV_1440.json")  # 保存好得json文件位置
    load_view_point(pcd, "camera_option.json")  # 加载修改时较后的pcd文件
