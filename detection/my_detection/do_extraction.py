import os
import numpy as np
import pickle

import data_loader
import board_extractor
import plane_projection
import point_cloud_visualization

frame = 321
file = "data/seq60_00000__%d.bin" % frame
data = data_loader.load_data(file=file)

# visualize
data_copy = data.copy()
data_copy = data_copy[np.where((data_copy[:, 0] < 0) & (data_copy[:, 0] > -10)
                               & (data_copy[:, 1] < 5)
                               & (data_copy[:, 1] > -5)
                               )]
# data_copy[:, 3] *= 256.
# data_copy[:, 3] /= 255.
# print(np.max(data_copy[:, 3]), np.min(data_copy[:, 3]))
# data_copy[:, 3] *= 1.2
# data_copy[:, 3] += 0.1
# print(np.max(data_copy[:, 3]), np.min(data_copy[:, 3]))
# data_copy[:, 3] = np.clip(data_copy[:, 3], 0., 0.99)
# print(np.max(data_copy[:, 3]), np.min(data_copy[:, 3]))
# point_cloud_visualization.vis_arr_by_intensity_at_viewpoint(arr=data_copy, title="0-0-raw data", point_size=-1)

ENABLE_TIMER = False
# extract planes
extract_res_file = "data/extract_results__%d.pkl" % frame
draw_extract = False
if ENABLE_TIMER is False and draw_extract is False and os.path.exists(extract_res_file):
    with open(extract_res_file, "rb") as f:
        ex_res = pickle.load(f)
    print("Extraction Results Loaded from:", extract_res_file)
else:
    ex_res, _ = board_extractor.detect_poles(data,
                                             neighbourthr=0.5, min_point_num=4, dis_thr=0.1, width_thr=20,
                                             fov_up=3.0, fov_down=-20.,
                                             proj_H=64, proj_W=500,
                                             lowest=-1.3, highest=6,
                                             lowthr=2.5, highthr=0.2, totalthr=0.05,
                                             ratiothr=0.4, anglethr=5,
                                             middle_res=draw_extract, visualize=1 if ENABLE_TIMER is False else -1)
    with open(extract_res_file, "wb") as f:
        pickle.dump(ex_res, f)
    print("Extraction Results Saved as:", extract_res_file)

# project plane
hori_angle_resol, vert_angle_resol = 0.1, 0.33

for plane_xyzi in ex_res[:1]:
    plane_projection.handler(xyzi=plane_xyzi,
                             intthr=0.1,
                             hori_angle_resol=hori_angle_resol, vert_angle_resol=vert_angle_resol, pixel_margin=50,
                             dist_thresh=0.1, visualize=1 if ENABLE_TIMER is False else -1)

print()
