from typing import List, Dict, Tuple, Optional
import numpy as np

from data_v2.taffic_signs import TrafficSignsData
from simulation import utils
from simulation.exceptions import *
from encoding_v2_1 import pattern_v2_1, substring_match_BM
from data_v1 import constants


def _search_bin_array_patterns(seq: np.ndarray, pat: np.ndarray) -> (bool, int):
    """
    search for the given category_1 patterns in the given sequence, both represented as <np.ndarray>
    :param seq:                 sequence (including on-board-only points, & thus of arbitrary length)
    :param pat:                 category_1 pattern (of length 4 or length 8)
    :return:                    (1) False if NOT found, True otherwise;
                                (2) -1 if not found, the starting index (in the sequence) of the first pattern found
    """
    assert 1 == len(seq.shape)
    assert 1 == len(pat.shape)

    if len(pat) > len(seq):
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
    if pattern_v2_1.ENCODING_LEVELS < len(_res):
        raise DecodeFailureVert("Too Many Levels: Expecting <= %d. Got %d"
                                % (pattern_v2_1.ENCODING_LEVELS, len(_res)))

    res = np.array(_res, dtype=int)
    return res


def _decode_handful_lines(lines_decoded: np.ndarray, cat_1_idx: int) -> Dict[str, int]:
    """
    Decode handful decoded lines
    :param lines_decoded:           of shape ((0,pattern_v2_1.ENCODING_LEVELS+2],
                                        pattern_v2_1.ENCODING_PATTERN_LENGTH or pattern_v2_1.ENCODING_LENGTH)
    :param cat_1_idx:               category_1 idx
    :return:                        {"category_1": cat_1_idx, "category_2": cat_2_idx}
                                    value is `None` if the corresponding key field cannot be decoded
                                    ("category_1" will never be `None`)
    """
    assert pattern_v2_1.ENCODING_LEVELS + 2 >= lines_decoded.shape[0] > 0
    assert (pattern_v2_1.ENCODING_PATTERN_LENGTH == lines_decoded.shape[1]) or \
           (pattern_v2_1.ENCODING_LENGTH == lines_decoded.shape[1])

    lines_decoded = lines_decoded.astype(int)
    lines_are_full_length = (pattern_v2_1.ENCODING_LENGTH == lines_decoded.shape[1])  # length lead to pattern
    res = {"category_1": cat_1_idx, "category_2": None}

    # find the line representing the category_1
    cat_1_pat = pattern_v2_1.get_bin_pattern_by_idx(idx=cat_1_idx)
    if lines_are_full_length:
        cat_1_pat = pattern_v2_1.get_sequence_by_pattern(pattern=cat_1_pat)
    cat_1_line_idx = -1
    for _line_idx, _line in enumerate(lines_decoded):
        if np.array_equal(_line, cat_1_pat) is True:
            cat_1_line_idx = _line_idx
            break
    assert -1 != cat_1_line_idx

    # remove all lines above the line representing the category_1
    lines_decoded = lines_decoded[cat_1_line_idx:, :]
    cat_1_line_idx = 0

    # [case 1] one valid line for category_1(LINE#1) only => end decoding
    if lines_are_full_length is False:
        return res

    # [case 2] two valid lines for category_1(LINE#1) and category_2(LINE#0) => continue decoding
    cat_2_bin = lines_decoded[0] ^ lines_decoded[1]
    cat_2_idx, _ = pattern_v2_1.non_dup_bin_2_dec(num=cat_2_bin, category_1_idx=cat_1_idx, is_category_2=True)
    res["category_2"] = cat_2_idx
    return res


def decode(sign_data_obj: TrafficSignsData,
           points: np.ndarray,
           hori_margin: int, vert_margin: int,
           height: int, width: int,
           tolerable: Optional[bool] = False) -> Tuple[Dict[str, int], Dict[str, str]]:
    assert 0 == np.nanmin(points)

    # === calculate the number of points on the encoding part
    max_cnt_encoding_hori_pt = np.floor(width * 1. * pattern_v2_1.ENCODING_LENGTH / hori_margin).astype(int) + 1
    if max_cnt_encoding_hori_pt < pattern_v2_1.ENCODING_PATTERN_LENGTH:
        raise DecodeFailureHori("Insufficient Data: Required >= %d on Encodings, Got <=%d"
                                % (pattern_v2_1.ENCODING_PATTERN_LENGTH, max_cnt_encoding_hori_pt))
    max_cnt_encoding_vert_pt = np.floor(height * 1. * pattern_v2_1.ENCODING_LEVELS / vert_margin).astype(int) + 1
    if max_cnt_encoding_vert_pt < 1:
        raise DecodeFailureVert("Insufficient Data: Required >= 1 on Encodings, Got <1")

    # === generate all the possible plans of decode_width<->pattern, by the number of points on the encoding part
    # decode_schemas = []
    all_bin_patterns = pattern_v2_1.get_all_bin_patterns()
    all_bin_patterns_full = [pattern_v2_1.get_sequence_by_pattern(pattern=i) for i in all_bin_patterns]
    if max_cnt_encoding_hori_pt < pattern_v2_1.ENCODING_LENGTH:  # [4,8) guaranteed
        decode_schemas = [{"length": pattern_v2_1.ENCODING_PATTERN_LENGTH,
                           "width": width * 2, "patterns": all_bin_patterns}]
    elif max_cnt_encoding_hori_pt == pattern_v2_1.ENCODING_LENGTH:  # 7 guaranteed, 8 possible
        decode_schemas = [{"length": pattern_v2_1.ENCODING_PATTERN_LENGTH,
                           "width": width * 2, "patterns": all_bin_patterns},
                          {"length": pattern_v2_1.ENCODING_LENGTH,
                           "width": width, "patterns": all_bin_patterns_full}]
    else:  # i.e., max_cnt_encoding_hori_pt > pattern_v2_1.ENCODING_LENGTH:  # [8,+inf) guaranteed
        decode_schemas = [{"length": pattern_v2_1.ENCODING_LENGTH,
                           "width": width, "patterns": all_bin_patterns_full}]

    # === generate all possible location combinations, by the horizontal starting location
    hori_plans = []  # CHECKPOINT: focus on variable `decode_schemas`
    for schema in decode_schemas:
        schema_length = schema["length"]
        schema_width = schema["width"]
        schema_all_patterns = schema["patterns"]
        for _hori in range(min(width * 2, hori_margin)):  # horizontal starting location
            _lines_decoded = []  # <list>of<np.ndarray>
            _pattern_found_src_idx = set()  # to filter out those found multiple patterns
            _lines_decoded_pattern_found_idx = []  # [ (line_idx, pattern_idx, starting_idx_in_line), ...]
            for __line in points:
                __line_data = __line[np.where(False == np.isnan(__line))]  # remove nan-s (Note: np.nan != np.nan)
                if 0 == len(__line_data):
                    _lines_decoded.append(np.array([], dtype=int))
                    continue
                __line_loc = np.arange(_hori, _hori + len(__line_data) * hori_margin, hori_margin)
                __line_decoded = utils.decode_one_line(points=__line_data, points_loc=__line_loc, width=schema_width)

                # search for possibly existing category_1 patterns if necessary
                if True:  # 0 == len(_pattern_found_src_idx):
                    for ___pattern_idx, ___pattern in enumerate(schema_all_patterns):  # each as <np.ndarray)>
                        ___match_res, ___match_idx = _search_bin_array_patterns(seq=__line_decoded, pat=___pattern)
                        if ___match_res is True:
                            # newly added criterion (2022/04/03):
                            #   bits before the staring of the found pattern must all be 1s AND
                            #   bits after the ending of the found pattern must all be 1s
                            if all(1 == __line_decoded[:___match_idx]) is False:
                                continue
                            if all(1 == __line_decoded[___match_idx + len(___pattern):]) is False:
                                continue
                            # newly added criterion (2022/04/04):
                            #   bits above the line of the found pattern must all be 1s
                            __lines_above_bits_cnt = np.sum([len(__line_above) for __line_above in _lines_decoded])
                            __lines_above_ones_cnt = np.sum([np.sum(__line_above) for __line_above in _lines_decoded])
                            if __lines_above_bits_cnt != __lines_above_ones_cnt:
                                continue
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
                "schema": schema_length,
                "horizontal_starting_location": _hori,
                "patterns_found_cnt": len(_lines_decoded_pattern_found_idx),
                "patterns_found_category": _pattern_found_src_idx.pop(),
                "lines_decoded": _lines_decoded,
                "lines_decoded_patterns_found_idx": _lines_decoded_pattern_found_idx,
            })

    if 0 == len(hori_plans):  # CHECKPOINT: focus on variable `hori_plans`
        raise DecodeFailureHori("No Possibilities")
    pass

    # === remove decoded on-board-only points
    hori_plans_sliced = []
    for _plan_idx, _plan in enumerate(hori_plans):
        _plan_schema_length = _plan["schema"]
        _plan_dec = _plan["lines_decoded"]  # [<np.ndarray>s]
        _plan_dec_pat = _plan["lines_decoded_patterns_found_idx"][0]  # {"line": 2, "pat_idx":1, "loc":2}
        _plan_dec_slice = [__line[_plan_dec_pat["loc"]:_plan_dec_pat["loc"] + _plan_schema_length]
                           for __line in _plan_dec]
        _plan["lines_decoded_sliced"] = _plan_dec_slice
        hori_plans_sliced.append(_plan)
    pass

    # === merge all horizontal starting locations that lead to the same decoded results
    def _hori_plan_are_equal(plan_1: dict, plan_2: dict) -> bool:
        if (plan_1["schema"] == plan_2["schema"]) is False:
            return False
        if (plan_1["patterns_found_cnt"] == plan_2["patterns_found_cnt"]) is False:
            return False
        if (plan_1["patterns_found_category"] == plan_2["patterns_found_category"]) is False:
            return False
        if (plan_1["lines_decoded_patterns_found_idx"] == plan_2["lines_decoded_patterns_found_idx"]) is False:
            return False
        return all([np.array_equal(i, j) for i, j in
                    zip(plan_1["lines_decoded_sliced"], plan_2["lines_decoded_sliced"])])

    hori_plans_sliced_merged = []  # CHECKPOINT: focus on variable `hori_plans_sliced`
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

    # try to decode all merged plans
    _res_decoded = []  # CHECKPOINT: focus on variable `hori_plans_sliced_merged`
    _res_decoded_info = []  # [{"category_1"/"category_2": <str>}, ...]
    for _final_plan in hori_plans_sliced_merged:
        _res_category_1_idx = _final_plan["patterns_found_category"]
        # === extract the final results of the horizontal decoding: remove all empty lines
        _hori_res = _final_plan["lines_decoded_sliced"]
        _hori_res = [__line for __line in _hori_res if 0 != len(__line)]
        print(end="")  # CHECKPOINT: focus on variable `_hori_res`
        # === merge lines
        _vert_res = _merge_lines(lines_decoded=_hori_res)
        print(end="")  # CHECKPOINT: focus on variable `_vert_res`
        # === actual decoder: handful decoded lines data to sign board info
        _decode_res = _decode_handful_lines(lines_decoded=_vert_res, cat_1_idx=_res_category_1_idx)
        print(end="")  # CHECKPOINT: focus on variable `_decode_res`
        # === validate the decoded result (by data encoding properties)
        _decode_res_info = sign_data_obj.get_sign_info_by_idx(cat_1_idx=_decode_res["category_1"],
                                                              cat_2_idx=_decode_res["category_2"])
        if _decode_res_info is not None:
            # validate the decoded result (by max possible encoding levels)
            _fields_cnt = int(_decode_res["category_1"] is not None) + \
                          int(_decode_res["category_2"] is not None)
            # omit impossibility: max lines cnt on encoding NOT sufficient for the levels extracted
            if _fields_cnt > max_cnt_encoding_vert_pt:
                continue
            # omit impossibility: levels extracted not complete for the min lines&length cnt on encoding
            if _fields_cnt < min(2, max_cnt_encoding_vert_pt - 1) and \
                    _fields_cnt < (max_cnt_encoding_hori_pt - 1) // pattern_v2_1.ENCODING_PATTERN_LENGTH:
                continue
            _res_decoded.append(_decode_res)
            _res_decoded_info.append(_decode_res_info)

    if 0 == len(_res_decoded):  # CHECKPOINT: focus on variable `_res_decoded`, `_res_decoded_info`
        raise DecodeFailure("No Valid Possibilities")

    # tolerable parsing: merge as-many-as-possible fields
    #   Note: (observed phenomenon) two identical cat_1&cat_2 might be merged tolerably,
    #       since they can be decode results with different pattern-found-location (e.g. due to different leading 1s)
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
        # merge tolerated if is successful
        if _res_decoded_tol_success is True:
            _res_decoded = [_res_decoded_tol]
            _res_decoded_info_tol["is_complete"] = (_res_decoded_info_tol["category_1"] is not None) and \
                                                   (_res_decoded_info_tol["category_2"] is not None)
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
