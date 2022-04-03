from tqdm import tqdm

from data_v2.taffic_signs import TrafficSignsData
from sign_boards import TrafficSignBoard
from lidar_points import LiDARSampling
from encoding_v2_1.encode_v2_1 import encode
from encoding_v2_1.decode_v2_1 import decode
import utils
from simulation.exceptions import *

# sample a traffic sign
data_obj = TrafficSignsData()
data_sample = data_obj.get_sample(category_idx=1, sign_idx=85)
print(data_sample)

# encode the sampled traffic sign
data_sample_encoding = encode(sample=data_sample)
print(data_sample_encoding)
height, width = 600, 100  # milli-meters
data_sample_raw_bar = utils.encoding_2_raw_bar(encoding=data_sample_encoding,
                                               elem_height=height, elem_width=width)

# test draw rectangle
sign_board_obj = TrafficSignBoard(1300, 1300)
sign_board_obj.draw_sign_board(shape="rectangle", rect_height=1200, rect_width=1200)

sign_board_obj.place_encoding(encoding=data_sample_raw_bar)
# sign_board_obj.render().show()
sign_board_obj.render().savefig("./canvas_v2_1.png")

# sample points on the canvas
distance = 50  # meters
hori_angle_resol, vert_angle_resol = 0.1, 0.33
pt_sample_obj = LiDARSampling(canvas=sign_board_obj,
                              hori_angle_resol=hori_angle_resol, vert_angle_resol=vert_angle_resol)
sample_res, sample_res_loc = pt_sample_obj.sample_at_distance(dist=50)
# print(sample_res)

ENABLE_STATS_ANA = False
cnt_success, cnt_suc_full, cnt_suc_not_full_not_tol, cnt_suc_tol, cnt_fail = 0, 0, 0, 0, 0
_iter_obj = range(0, len(sample_res)) if not ENABLE_STATS_ANA else tqdm(range(0, len(sample_res), 10))
for _sample_idx in _iter_obj:
    _sample = sample_res[_sample_idx]
    _sample_loc = sample_res_loc[_sample_idx]
    try:
        _sample_decoded, _sample_decoded_info = decode(
            sign_data_obj=data_obj,
            points=_sample,
            hori_margin=utils.dist_2_margin(dist=distance, angle_resol=hori_angle_resol),
            vert_margin=utils.dist_2_margin(dist=distance, angle_resol=vert_angle_resol),
            height=height, width=width,
            tolerable=True)
        if not ENABLE_STATS_ANA:  # debug printing
            print(_sample_decoded, _sample_decoded_info)
        else:  # statistical analysis
            _is_suc = True
            if _is_suc is True and _sample_decoded["category_1"] is not None:
                _is_suc = (_sample_decoded["category_1"] == data_sample["encoding"]["category"])
            if _is_suc is True and _sample_decoded["category_2"] is not None:
                _is_suc = (_sample_decoded["category_2"] == data_sample["encoding"]["idx"])
            # update counts
            if _is_suc is False:
                cnt_fail += 1
                continue
            cnt_success += 1
            if _sample_decoded_info["is_complete"] is True:
                cnt_suc_full += 1
            if (_sample_decoded_info["is_complete"] is False) and _sample_decoded_info.get("is_tolerated") is None:
                cnt_suc_not_full_not_tol += 1
            if _sample_decoded_info.get("is_tolerated") is True:
                cnt_suc_tol += 1
    except DecodeFailure as err:
        if not ENABLE_STATS_ANA:  # debug printing
            print("Decode Failed for Sample Loc (%d,%d): %s" % (_sample_loc["hori"], _sample_loc["vert"], str(err)))
        else:  # statistical analysis
            cnt_fail += 1
        continue
if ENABLE_STATS_ANA:  # statistical analysis
    print("[ALL] %d\n\t[SUCCESS] %d (full=%d, !full!tol=%d, tolerated=%d)\n\t[FAILURE] %d"
          % (len(sample_res), cnt_success, cnt_suc_full, cnt_suc_not_full_not_tol, cnt_suc_tol, cnt_fail))
print()
