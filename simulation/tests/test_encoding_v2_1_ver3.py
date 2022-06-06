import time
import math
import numpy as np
from tqdm import tqdm
import json

from data_v2.taffic_signs import TrafficSignsData
from sign_boards import TrafficSignBoard
from lidar_points import LiDARSampling
from encoding_v2_1.encode_v2_1 import encode
from encoding_v2_1.decode_v2_1_ver3 import decode
import utils
from simulation.exceptions import *

ALL_ENV_SETTINGS = {
    "tri11": {
        "sample": {"category": 1, "sign": 85},
        "canvas": {"height": 1150, "width": 1350},
        "board": {"shape": "triangle", "kwargs": {"tri_length": 1300}},
        "encoding": {"scaled": True, "height": 221, "width": 67, "orientation": "bottom"},
    },  # Triangle (*1300): Scaled Height + 3.3 Ratio (221*67)
    "tri10": {
        "sample": {"category": 1, "sign": 85},
        "canvas": {"height": 1150, "width": 1350},
        "board": {"shape": "triangle", "kwargs": {"tri_length": 1300}},
        "encoding": {"scaled": True, "height": 257, "width": 51, "orientation": "bottom"},
    },  # Triangle (*1300): Scaled Height, NO Ratio=5 (257*51)
    "tri01": {
        "sample": {"category": 1, "sign": 85},
        "canvas": {"height": 1150, "width": 1350},
        "board": {"shape": "triangle", "kwargs": {"tri_length": 1300}},
        "encoding": {"scaled": False, "height": 275, "width": 83, "orientation": "bottom"},
    },  # Triangle (*1300): NO Scaled Height, 3.3 Ratio (275*83)
    "tri00": {
        "sample": {"category": 1, "sign": 85},
        "canvas": {"height": 1150, "width": 1350},
        "board": {"shape": "triangle", "kwargs": {"tri_length": 1300}},
        "encoding": {"scaled": False, "height": 333, "width": 67, "orientation": "bottom"},
    },  # Triangle (*1300): NO Scaled Height, NO Ratio=5 (333*67)

    "cir11": {
        "sample": {"category": 1, "sign": 85},
        "canvas": {"height": 1250, "width": 1250},
        "board": {"shape": "circle", "kwargs": {"cir_radius": 600}},
        "encoding": {"scaled": True, "height": 311, "width": 94, "orientation": "center"},
    },  # Circle (*600): Scaled Height + 3.3 Ratio (311*94)
    "cir10": {
        "sample": {"category": 1, "sign": 85},
        "canvas": {"height": 1250, "width": 1250},
        "board": {"shape": "circle", "kwargs": {"cir_radius": 600}},
        "encoding": {"scaled": True, "height": 353, "width": 71, "orientation": "center"},
    },  # Circle (*600): Scaled Height, NO Ratio=5 (353*71)
    "cir01": {
        "sample": {"category": 1, "sign": 85},
        "canvas": {"height": 1250, "width": 1250},
        "board": {"shape": "circle", "kwargs": {"cir_radius": 600}},
        "encoding": {"scaled": False, "height": 382, "width": 116, "orientation": "center"},
    },  # Circle (*600): NO Scaled Height + 3.3 Ratio (382*116)
    "cir00": {
        "sample": {"category": 1, "sign": 85},
        "canvas": {"height": 1250, "width": 1250},
        "board": {"shape": "circle", "kwargs": {"cir_radius": 600}},
        "encoding": {"scaled": False, "height": 469, "width": 94, "orientation": "center"},
    },  # Circle (*600): NO Scaled Height, NO Ratio=5 (469*94)

    "rect11": {
        "sample": {"category": 1, "sign": 85},
        "canvas": {"height": 1300, "width": 1300},
        "board": {"shape": "rectangle", "kwargs": {"rect_height": 1200, "rect_width": 1200}},
        "encoding": {"scaled": True, "height": 400, "width": 121, "orientation": "center"},
    },  # Rectangle (1300*1300): Scaled Height + 3.3 Ratio (400*121)
    "rect10": {
        "sample": {"category": 1, "sign": 85},
        "canvas": {"height": 1300, "width": 1300},
        "board": {"shape": "rectangle", "kwargs": {"rect_height": 1200, "rect_width": 1200}},
        "encoding": {"scaled": True, "height": 400, "width": 80, "orientation": "center"},
    },  # Rectangle (1300*1300): Scaled Height, NO Ratio=5 (400*80)
    "rect01": {
        "sample": {"category": 1, "sign": 85},
        "canvas": {"height": 1300, "width": 1300},
        "board": {"shape": "rectangle", "kwargs": {"rect_height": 1200, "rect_width": 1200}},
        "encoding": {"scaled": False, "height": 495, "width": 150, "orientation": "center"},
    },  # Rectangle (1300*1300): NO Scaled Height, 3.3 Ratio (495*150)
    "rect00": {
        "sample": {"category": 1, "sign": 85},
        "canvas": {"height": 1300, "width": 1300},
        "board": {"shape": "rectangle", "kwargs": {"rect_height": 1200, "rect_width": 1200}},
        "encoding": {"scaled": False, "height": 600, "width": 120, "orientation": "center"},
    },  # Rectangle (1300*1300): NO Scaled Height, NO Ratio=5 (600*120)
}
ALL_DECODING_SETTINGS = {
    "1": {"use_cnt_delta": True, },
    # "0": {"use_cnt_delta": False, },
}


def do(setting_env_key, setting_dec_key):
    # setting_env_key = "rect"
    # setting_dec_key = "1"
    setting_env = ALL_ENV_SETTINGS[setting_env_key]
    setting_dec = ALL_DECODING_SETTINGS[setting_dec_key]
    print("===== Using Env Setting \"%s\" =====" % setting_env_key)
    print(json.dumps(setting_env, indent=2))
    print("===== Using Decoding Setting \"%s\" =====" % setting_dec_key)
    print(json.dumps(setting_dec, indent=2))

    # sample a traffic sign
    data_obj = TrafficSignsData()
    data_sample = data_obj.get_sample(category_idx=1, sign_idx=75)
    print(data_sample)

    # encode the sampled traffic sign
    data_sample_encoding = encode(sample=data_sample, use_scaled_height=setting_env["encoding"]["scaled"])
    print(data_sample_encoding)
    height, width = setting_env["encoding"]["height"], setting_env["encoding"]["width"]  # milli-meters
    data_sample_raw_bar = utils.encoding_2_raw_bar(encoding=data_sample_encoding,
                                                   elem_height=height, elem_width=width)

    # test draw rectangle
    sign_board_obj = TrafficSignBoard(height=setting_env["canvas"]["height"], width=setting_env["canvas"]["width"])
    sign_board_obj.draw_sign_board(shape=setting_env["board"]["shape"], **setting_env["board"]["kwargs"])

    sign_board_obj.place_encoding(encoding=data_sample_raw_bar, orientation=setting_env["encoding"]["orientation"])
    # sign_board_obj.render().show()
    sign_board_obj.render().savefig("./canvas_v2_1__%s.png" % setting_env_key)

    def sample_n_decode(distance, vert_step, hori_step):
        # vert_step, hori_step = 20, 1
        # sample points on the canvas
        # distance = 10  # meters
        hori_angle_resol, vert_angle_resol = 0.1, 0.33
        pt_sample_obj = LiDARSampling(canvas=sign_board_obj,
                                      hori_angle_resol=hori_angle_resol, vert_angle_resol=vert_angle_resol)
        sample_res, sample_res_loc = pt_sample_obj.sample_at_distance(
            dist=distance, vert_step=vert_step, hori_step=hori_step)
        # print(sample_res)

        ENABLE_STATS_ANA = True
        NO_ERR_MSG = True
        # statistical analysis settings
        STATS_ANA_MAX_ATTEMPTS = 1000
        sample_step_size = math.ceil(len(sample_res) * 1. / STATS_ANA_MAX_ATTEMPTS)
        cnt_success, cnt_suc_full, cnt_suc_not_full_not_tol, cnt_suc_tol, cnt_fail, cnt_wrong = 0, 0, 0, 0, 0, 0
        cnt_val_b, cnt_val_a, cnt_tol_b, cnt_tol_a = 0, 0, 0, 0
        cnt_suc_levels = {1: 0, 2: 0}
        _iter_obj = range(0, len(sample_res)) if not ENABLE_STATS_ANA else tqdm(
            range(0, len(sample_res), sample_step_size))
        # actual iteration starts here
        for _sample_idx in _iter_obj:
            _sample = sample_res[_sample_idx]
            _sample_loc = sample_res_loc[_sample_idx]
            # np.save("sample.npy", _sample)
            # exit()
            try:
                _sample_decoded, _sample_decoded_info, _sample_step_cnt = decode(
                    sign_data_obj=data_obj,
                    points=_sample,
                    hori_margin=utils.dist_2_margin(dist=distance, angle_resol=hori_angle_resol),
                    vert_margin=utils.dist_2_margin(dist=distance, angle_resol=vert_angle_resol),
                    height=height, width=width,
                    is_scaled_height=setting_env["encoding"]["scaled"],
                    use_cnt_delta=setting_dec["use_cnt_delta"],
                    tolerable=True)
                if not ENABLE_STATS_ANA:  # debug printing
                    print(_sample_decoded, _sample_decoded_info)
                else:  # statistical analysis
                    cnt_val_b += _sample_step_cnt["validation"]["before"]
                    cnt_val_a += _sample_step_cnt["validation"]["after"]
                    cnt_tol_b += _sample_step_cnt["toleration"]["before"]
                    cnt_tol_a += _sample_step_cnt["toleration"]["after"]
                    _is_suc = True
                    if _is_suc is True and _sample_decoded["category_1"] is not None:
                        _is_suc = (_sample_decoded["category_1"] == data_sample["encoding"]["category"])
                    if _is_suc is True and _sample_decoded["category_2"] is not None:
                        _is_suc = (_sample_decoded["category_2"] == data_sample["encoding"]["idx"])
                    if _is_suc is True:
                        _cnt_levels = int(_sample_decoded["category_1"] is not None) + \
                                      int(_sample_decoded["category_2"] is not None)
                        cnt_suc_levels[_cnt_levels] += 1
                    # update counts
                    if _is_suc is False:
                        cnt_wrong += 1
                        continue
                    cnt_success += 1
                    if _sample_decoded_info["is_complete"] is True:
                        cnt_suc_full += 1
                    if (_sample_decoded_info["is_complete"] is False) and _sample_decoded_info.get(
                            "is_tolerated") is None:
                        cnt_suc_not_full_not_tol += 1
                    if _sample_decoded_info.get("is_tolerated") is True:
                        cnt_suc_tol += 1
            except DecodeFailure as err:
                if NO_ERR_MSG is False:
                    print("Decode Failed for Sample Loc (%d,%d): %s" % (
                        _sample_loc["hori"], _sample_loc["vert"], str(err)))
                cnt_fail += 1
                continue
        if ENABLE_STATS_ANA:  # statistical analysis
            print(
                "==============================\n"
                "[SETTINGS] distance=%dm, v/h step=%d/%d\n"
                "[ALL] %d\n"
                "\t[SUCCESS] %d (full=%d, !full!tol=%d, tolerated=%d)\n\t\tLevels: 1=%d, 2=%d\n"
                "\t[WRONG] %d\n\t[FAILURE] %d\n"
                "[VAL] %d -> %d; [TOL] %d -> %d\n"
                "=============================="
                % (distance, vert_step, hori_step,
                   len(_iter_obj), cnt_success, cnt_suc_full, cnt_suc_not_full_not_tol, cnt_suc_tol,
                   cnt_suc_levels[1], cnt_suc_levels[2], cnt_wrong, cnt_fail,
                   cnt_val_b, cnt_val_a, cnt_tol_b, cnt_tol_a))
            return "%d\t%d\t%d\t%d\t" \
                   "%d\t%d\t" \
                   "%d\t%d\t" \
                   "%d\t%d" \
                   % (cnt_success, cnt_suc_tol, cnt_wrong, cnt_fail,
                      cnt_suc_levels[1], cnt_suc_levels[2],
                      cnt_val_b, cnt_val_a,
                      cnt_tol_b, cnt_tol_a)

    print()
    toc1 = time.perf_counter()
    excel_str = []
    for dist in range(10, 140 + 10, 10):  # [10, 40]:  # range(10, 140 + 10, 10):
        if 10 == dist:
            v_step = 1
        elif 20 == dist:
            v_step = 4
        elif 30 == dist:
            v_step = 8
        elif 40 == dist:
            v_step = 10
        else:
            v_step = 20
        h_step = 1
        _excel_str = sample_n_decode(distance=dist, vert_step=v_step, hori_step=h_step)
        excel_str.append(_excel_str)

    print(setting_env_key, setting_dec_key)
    for i in excel_str:
        print(i)

    toc2 = time.perf_counter()
    print("[Time Elapsed - Altogether]:", toc2 - toc1)


# res = []
# for env_key in ALL_ENV_SETTINGS.keys():
#     for dec_key in ALL_DECODING_SETTINGS.keys():
#         res.append((env_key, dec_key))
# print(res)
# all_comb = [("tri11", "1"), ("tri10", "1"), ("tri01", "1"), ("tri00", "1"),
#             ("cir11", "1"), ("cir10", "1"), ("cir01", "1"), ("cir00", "1"),
#             ("rect11", "1"), ("rect10", "1"), ("rect01", "1"), ("rect00", "1")]
all_comb = [
    ("tri01", "1"),
    ("tri11", "1"), ("cir11", "1"), ("rect11", "1"),  # fast test settings
    # ("tri11", "1"),  # in fast test settings
    ("tri10", "1"), ("tri01", "1"), ("tri00", "1"),
    # ("cir11", "1"),  # in fast test settings
    ("cir10", "1"), ("cir01", "1"), ("cir00", "1"),
    # ("rect11", "1"),  # in fast test settings
    ("rect10", "1"), ("rect01", "1"), ("rect00", "1"),
]
ENABLE_TIMER = False
for env_key, dec_key in all_comb:
    do(setting_env_key=env_key, setting_dec_key=dec_key)
    if ENABLE_TIMER is True:
        exit()
