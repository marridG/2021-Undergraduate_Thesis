from typing import List, Dict, Tuple, Optional
import numpy as np

from data_v1.taffic_signs import TrafficSignsData
from simulation import utils
from simulation.exceptions import *
from encoding_v1_2 import pattern_v1_2, substring_match_BM
from data_v1 import constants


def _search_bin_array_patterns(seq: np.ndarray, pat: np.ndarray) -> (bool, int):
    """
    search for the given category_1 patterns in the given sequence, both represented as <np.ndarray>
    :param seq:                 sequence
    :param pat:                 category_1 pattern
    :return:                    (1) False if NOT found, True otherwise;
                                (2) -1 if not found, the starting index (in the sequence) of the first pattern found
    """
    assert 1 == len(seq.shape)
    assert 1 == len(pat.shape)

    if len(seq) < len(pat):
        return False, -1

    seq_str = "".join([str(i) for i in seq])
    pat_str = "".join([str(i) for i in pat])
    match_idx = substring_match_BM.match(text=seq_str, pattern=pat_str)
    if -1 == match_idx:
        return False, -1

    return True, match_idx


def _merge_lines(lines_decoded: List[np.ndarray]) -> np.ndarray:
    """
    Merge decoded lines into <= the required (by levels count pattern) number of lines.
        i.e. merge adjacent lines that are the same
    :param lines_decoded:           decoded lines data
    :return:                        merged lines, given as type <int>
    """
    # make sure that all the decoded lines are of the same length
    _length_set = set([len(i) for i in lines_decoded])
    assert 1 == len(_length_set)

    _res = []
    for _line in lines_decoded:
        if 0 == len(_res):
            _res.append(_line)
            continue
        # merge adjacent lines that are the same
        if np.array_equal(_res[-1], _line) is True:
            continue
        _res.append(_line)

    # check the sufficiency of encoding levels
    if pattern_v1_2.ENCODING_LEVELS < len(_res):
        raise DecodeFailureVert("Too Many Levels: Expecting <= %d. Got %d"
                                % (pattern_v1_2.ENCODING_LEVELS, len(_res)))

    res = np.array(_res, dtype=int)
    return res


def _decode_handful_lines(lines_decoded: np.ndarray, cat_1_idx: int) -> Dict[str, int]:
    """
    Decode handful decoded lines TODO: lines_decoded should have at most pattern_v1_2.ENCODING_LEVELS+2 lines
    :param lines_decoded:           of shape ((0,pattern_v1_2.ENCODING_LEVELS], pattern_v1_2.ENCODING_LENGTH)
    :param cat_1_idx:               category_1 idx
    :return:                        {"category_1": cat_1_idx, "category_2": cat_2_idx, "num": num_idx}
                                    value is `None` if the corresponding key field cannot be decoded
                                    ("category_1" will never be `None`)
    """
    assert pattern_v1_2.ENCODING_LEVELS >= lines_decoded.shape[0] > 0
    assert pattern_v1_2.ENCODING_LENGTH == lines_decoded.shape[1]

    lines_decoded = lines_decoded.astype(int)
    res = {"category_1": cat_1_idx, "category_2": None, "num": None}

    # find the line representing the category_1
    cat_1_pat = pattern_v1_2.get_bin_pattern_by_idx(idx=cat_1_idx)
    cat_1_line_idx = -1
    for _line_idx, _line in enumerate(lines_decoded):
        if np.array_equal(_line, cat_1_pat) is True:
            cat_1_line_idx = _line_idx
            break
    assert -1 != cat_1_line_idx

    # [case 1] one line for category_1(LINE#1) only => end decoding
    if 1 == lines_decoded.shape[0] and 0 == cat_1_line_idx:
        return res

    # [case 2] two lines for category_1(LINE#1) and category_2(LINE#0)/num(LINE#2) => continue decoding
    if 2 == lines_decoded.shape[0]:
        # [case 2-1] two lines for category_1(LINE#1) and category_2(LINE#0)
        if 1 == cat_1_line_idx:
            cat_2_bin = lines_decoded[0] ^ lines_decoded[1]
            cat_2_idx = pattern_v1_2.non_dup_bin_2_dec(num=cat_2_bin, category_1_idx=cat_1_idx,
                                                       is_category_2=True, is_num=False)
            res["category_2"] = cat_2_idx
            return res
        # [case 2-1] two lines for category_1(LINE#1, but as #0) and num(LINE#2, but as #1)
        else:  # i.e., 0 == cat_1_line_idx
            num_bin = lines_decoded[1] ^ lines_decoded[0]
            num_idx = pattern_v1_2.non_dup_bin_2_dec(num=num_bin, category_1_idx=cat_1_idx,
                                                     is_category_2=False, is_num=True)
            res["num"] = num_idx
            return res
    # [case 3] three lines for all category_1(LINE#1), category_2(LINE#0) and num(LINE#2)
    else:  # i.e., 3 == lines_decoded.shape[0]
        cat_2_bin = lines_decoded[0] ^ lines_decoded[1]
        cat_2_idx = pattern_v1_2.non_dup_bin_2_dec(num=cat_2_bin, category_1_idx=cat_1_idx,
                                                   is_category_2=True, is_num=False)
        res["category_2"] = cat_2_idx
        num_bin = lines_decoded[2] ^ lines_decoded[1]
        num_idx = pattern_v1_2.non_dup_bin_2_dec(num=num_bin, category_1_idx=cat_1_idx,
                                                 is_category_2=False, is_num=True)
        res["num"] = num_idx
        return res


def decode(sign_data_obj: TrafficSignsData,
           points: np.ndarray,
           hori_margin: float, vert_margin: float,
           height: int, width: int,
           tolerable: Optional[bool] = False) -> Tuple[Dict[str, int], Dict[str, str]]:
    assert 0 == np.nanmin(points)

    # === generate all possible location combinations, by the horizontal starting location
    hori_plans = []
    all_bin_patterns = pattern_v1_2.get_all_bin_patterns()
    for _hori in range(int(hori_margin)):  # horizontal starting location
        _lines_decoded = []  # <list>of<np.ndarray>
        _pattern_found_src_idx = set()  # to filter out those found multiple patterns
        _lines_decoded_pattern_found_idx = []  # [ (line_idx, pattern_idx, starting_idx_in_line), ...]
        for __line in points:
            __line_data = __line[np.where(False == np.isnan(__line))]  # Note: np.nan != np.nan
            if 0 == len(__line_data):
                _lines_decoded.append(np.array([], dtype=int))
                continue
            __line_loc = np.arange(_hori, _hori + len(__line_data) * hori_margin, hori_margin)
            __line_decoded = utils.decode_one_line(points=__line_data, points_loc=__line_loc, width=width)

            # search for possibly existing category_1 patterns
            for ___pattern_idx, ___pattern in enumerate(all_bin_patterns):  # each as <np.ndarray)>
                ___match_res, ___match_idx = _search_bin_array_patterns(seq=__line_decoded, pat=___pattern)
                if ___match_res is True:
                    _lines_decoded_pattern_found_idx.append({
                        "line": len(_lines_decoded), "pat_idx": ___pattern_idx, "loc": ___match_idx})
                    _pattern_found_src_idx.add(___pattern_idx)
            _lines_decoded.append(__line_decoded)

        #  omit horizontal_starting_loc if NO category_1 patterns are found
        if 0 == len(_lines_decoded_pattern_found_idx):
            continue
        # omit horizontal_starting_loc if MULTIPLE (>=2) category_1 patterns are found
        if 1 < len(_pattern_found_src_idx):
            continue
        # otherwise, add to the possible plans
        hori_plans.append({
            "horizontal_starting_location": _hori,
            "patterns_found_cnt": len(_lines_decoded_pattern_found_idx),
            "patterns_found_category": _pattern_found_src_idx.pop(),
            "lines_decoded": _lines_decoded,
            "lines_decoded_patterns_found_idx": _lines_decoded_pattern_found_idx,
        })

    if 0 == len(hori_plans):
        raise DecodeFailureHori("No Possibilities")
    pass

    # === remove decoded on-board-only points
    hori_plans_sliced = []
    for _plan_idx, _plan in enumerate(hori_plans):
        _plan_dec = _plan["lines_decoded"]  # [<np.ndarray>s]
        _plan_dec_pat = _plan["lines_decoded_patterns_found_idx"][0]  # {"line": 2, "pat_idx":1, "loc":2}
        _plan_dec_slice = [__line[_plan_dec_pat["loc"]:_plan_dec_pat["loc"] + pattern_v1_2.ENCODING_LENGTH]
                           for __line in _plan_dec]
        _plan["lines_decoded_sliced"] = _plan_dec_slice
        hori_plans_sliced.append(_plan)
    pass

    # === merge all horizontal starting locations that lead to the same decoded results
    def _hori_plan_are_equal(plan_1: dict, plan_2: dict) -> bool:
        if (plan_1["patterns_found_cnt"] == plan_2["patterns_found_cnt"]) is False:
            return False
        if (plan_1["patterns_found_category"] == plan_2["patterns_found_category"]) is False:
            return False
        if (plan_1["lines_decoded_patterns_found_idx"] == plan_2["lines_decoded_patterns_found_idx"]) is False:
            return False
        return all([np.array_equal(i, j) for i, j in
                    zip(plan_1["lines_decoded_sliced"], plan_2["lines_decoded_sliced"])])

    hori_plans_sliced_merged = []
    for _plan in hori_plans_sliced:
        _set_found = False
        for __plan_set_idx, __plan_set in enumerate(hori_plans_sliced_merged):
            if _hori_plan_are_equal(_plan, __plan_set) is True:
                _set_found = True
                hori_plans_sliced_merged[__plan_set_idx]["horizontal_starting_location"].append(
                    _plan["horizontal_starting_location"])
                break
        if _set_found is False:
            _plan["horizontal_starting_location"] = [_plan["horizontal_starting_location"]]
            hori_plans_sliced_merged.append(_plan)

    """
    if 1 != len(hori_plans_sliced_merged):
        raise DecodeFailureHori("Multiple Possibilities: Expecting 1. Got %d" % len(hori_plans_sliced_merged))
    res_category_1_idx = hori_plans_sliced_merged[0]["patterns_found_category"]
    pass

    # === extract the final results of the horizontal decoding
    hori_res = hori_plans_sliced_merged[0]["lines_decoded_sliced"]
    hori_res = [_line for _line in hori_res if 0 != len(_line)]
    pass

    # === merge lines
    vert_res = _merge_lines(lines_decoded=hori_res)
    pass

    # === actual decoder: handful decoded lines data to sign board info
    decode_res = _decode_handful_lines(lines_decoded=vert_res, cat_1_idx=res_category_1_idx)
    pass

    return decode_res
    """  # [deprecated] codes that do not contain info validation check

    # try to decode all merged plans
    _res_decoded = []
    _res_decoded_info = []  # [{"category_1"/"category_2"/"num": <str>}, ...]
    for _final_plan in hori_plans_sliced_merged:
        _res_category_1_idx = _final_plan["patterns_found_category"]
        pass
        # === extract the final results of the horizontal decoding
        _hori_res = _final_plan["lines_decoded_sliced"]
        _hori_res = [__line for __line in _hori_res if 0 != len(__line)]
        pass
        # === merge lines
        _vert_res = _merge_lines(lines_decoded=_hori_res)
        pass
        # === actual decoder: handful decoded lines data to sign board info
        _decode_res = _decode_handful_lines(lines_decoded=_vert_res, cat_1_idx=_res_category_1_idx)
        pass
        # === validate the decoded result
        _decode_res_info = sign_data_obj.get_sign_info_by_idx(cat_1_idx=_decode_res["category_1"],
                                                              cat_2_idx=_decode_res["category_2"],
                                                              num_idx=_decode_res["num"])
        if _decode_res_info is not None:
            _res_decoded.append(_decode_res)
            _res_decoded_info.append(_decode_res_info)

    if 0 == len(_res_decoded):
        raise DecodeFailure("No Valid Possibilities")

    # tolerable parsing: merge as-many-as-possible fields
    if 1 < len(_res_decoded) and tolerable is True:
        _res_decoded_tol_success = False
        _res_decoded_tol = {key: None for key in _res_decoded[0].keys()}
        _res_decoded_info_tol = {key: None for key in _res_decoded_info[0].keys()}
        # merge category_1
        _res_dec_all_cat_1 = set([_dec_res["category_1"] for _dec_res in _res_decoded])
        if 1 == len(_res_dec_all_cat_1):
            _res_decoded_tol["category_1"] = _res_decoded[0]["category_1"]
            _res_decoded_info_tol["category_1"] = _res_decoded_info[0]["category_1"]
            _res_decoded_tol_success = True
            # merge category_2
            _res_dec_all_cat_2 = set([_dec_res["category_2"] for _dec_res in _res_decoded])
            if 1 == len(_res_dec_all_cat_2):
                _res_decoded_tol["category_2"] = _res_decoded[0]["category_2"]
                _res_decoded_info_tol["category_2"] = _res_decoded_info[0]["category_2"]
            del _res_dec_all_cat_2
        del _res_dec_all_cat_1
        # merge num
        _res_dec_all_num = set([_dec_res["num"] for _dec_res in _res_decoded])
        if 1 == len(_res_dec_all_num):
            _res_decoded_tol["num"] = _res_decoded[0]["num"]
            _res_decoded_info_tol["num"] = _res_decoded_info[0]["num"]
            _res_decoded_tol_success = True
        del _res_dec_all_num
        if _res_decoded_tol_success is True:
            _res_decoded = [_res_decoded_tol]
            _res_decoded_info_tol["is_complete"] = False
            _res_decoded_info_tol["is_tolerated"] = True
            _res_decoded_info = [_res_decoded_info_tol]

    if 1 < len(_res_decoded):
        raise DecodeFailureHori("Multiple Valid Possibilities: Expecting 1. Got %d" % len(_res_decoded))
    res_decoded = _res_decoded[0]
    res_decoded_info = _res_decoded_info[0]

    return res_decoded, res_decoded_info


if "__main__" == __name__:
    pass
    print()
