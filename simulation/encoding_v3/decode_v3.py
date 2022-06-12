from typing import List, Dict, Tuple, Optional
import numpy as np

from data_v2.taffic_signs import TrafficSignsData
from simulation import utils
from simulation.exceptions import *
from encoding_v3 import pattern_v3, substring_match_BM


def _decode_one_line(points: np.ndarray, bar_cnt: int, max_cnt_per_bar: int, allow_end_1: bool = True) \
        -> List[Dict[str, List[int]]]:
    """
    doc todo: General decoder to "combine" DETECTED horizontal digits into the fixed length of encodings
    :param points:          samples of binary values (0/1)
    :param bar_cnt:         count of target bars
    :param max_cnt_per_bar: maximum number of sample points per bar
    :param allow_end_1:     allow the last digit of the encodings to be 1
    :return:                "combined" sequence of bars and corresponding merge plans
    """
    assert 1 == len(points.shape)
    assert len(points) > 0
    assert False == np.isnan(np.max(points))  # make sure no nan values

    points = points.astype(int)
    pts_l_neq_r = np.concatenate(([True], points[:-1] != points[1:], [True]))
    pts_l_neq_r_start_idx = np.where(True == pts_l_neq_r)[0]
    pts_l_neq_r_start_idx_is_one_idx = np.where(1 == points[pts_l_neq_r_start_idx[:-1]])
    pts_conti_cnt = np.diff(pts_l_neq_r_start_idx)
    pts_conti_cnt[pts_l_neq_r_start_idx_is_one_idx] *= -1
    # now, in variable `pts_conti_cnt`, each element is the number of continuous 1/0's (cnt_1<0, cnt_0>0)
    if pts_conti_cnt[0] < 0:
        pts_conti_cnt = pts_conti_cnt[1:]
    assert len(pts_conti_cnt) > 0
    pts_conti_cnt_backup = pts_conti_cnt.copy()

    _empty_val = -99
    all_possibilities = []  # [{"seq"/"pt_cnt": []}, ...]
    seq = [_empty_val] * bar_cnt
    seq_pt_cnt = [_empty_val] * bar_cnt

    def back_trace(_seq_ptr, _conti_ptr):
        if bar_cnt == _seq_ptr:
            # === assuming the last digit of the pattern can NOT be 1 ===
            if allow_end_1 is False:
                # last digit is 1
                if 1 == seq[-1]:
                    return False
                # unused zeros at _conti_ptr+2
                if _conti_ptr <= (len(pts_conti_cnt) - 1) - 2:
                    return False
                # unused zeros at _conti_ptr
                if _conti_ptr <= len(pts_conti_cnt) - 1 and 0 < pts_conti_cnt[_conti_ptr]:
                    return False
            # === assuming the last digit of the pattern CAN be 1 ===
            else:  # i.e., ALLOW_END_1 is True:
                if 0 == seq[-1]:
                    # unused zeros at _conti_ptr+2
                    if _conti_ptr <= (len(pts_conti_cnt) - 1) - 2:
                        return False
                    # unused zeros at _conti_ptr
                    if _conti_ptr <= len(pts_conti_cnt) - 1 and 0 < pts_conti_cnt[_conti_ptr]:
                        return False
                else:
                    # unused ones/zeros at _conti_ptr+1
                    if _conti_ptr <= (len(pts_conti_cnt) - 1) - 1:
                        return False
                    # unused zeros at _conti_ptr
                    if _conti_ptr <= len(pts_conti_cnt) - 1 and 0 < pts_conti_cnt[_conti_ptr]:
                        return False
            # return True
            all_possibilities.append({"seq": seq.copy(), "pt_cnt": seq_pt_cnt.copy()})
            return False

        for __pt_cnt in range(max(1, max_cnt_per_bar - 1), max_cnt_per_bar + 1):
            if _conti_ptr == len(pts_conti_cnt):
                return False
            if __pt_cnt > abs(pts_conti_cnt[_conti_ptr]):
                continue
            if _seq_ptr > 0 and abs(__pt_cnt - seq_pt_cnt[_seq_ptr - 1]) > 1:
                continue
            __pt_is_one = (pts_conti_cnt[_conti_ptr] < 0)
            __pt_val = 1 if __pt_is_one else 0

            seq[_seq_ptr] = __pt_val
            seq_pt_cnt[_seq_ptr] = __pt_cnt
            _seq_ptr += 1
            pts_conti_cnt[_conti_ptr] += __pt_cnt * (1 if __pt_is_one else -1)
            _conti_ptr_moved = (0 == pts_conti_cnt[_conti_ptr])
            _conti_ptr += 1 if _conti_ptr_moved else 0

            _next_res = back_trace(_seq_ptr=_seq_ptr, _conti_ptr=_conti_ptr)  # CHECKPOINT
            if _next_res is True:
                return True
            # restore status
            _conti_ptr -= 1 if _conti_ptr_moved else 0
            pts_conti_cnt[_conti_ptr] -= __pt_cnt * (1 if __pt_is_one else -1)
            _seq_ptr -= 1
            seq_pt_cnt[_seq_ptr] = _empty_val
            seq[_seq_ptr] = _empty_val
            continue  # CHECKPOINT
        return False

    bt_res = back_trace(_seq_ptr=0, _conti_ptr=0)  # is always False
    # print(bt_res)
    # print(all_possibilities)

    return all_possibilities


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

    seq_str = "".join([str(i) for i in seq[np.where((0 == seq) | (1 == seq))]])
    pat_str = "".join([str(i) for i in pat])
    match_idx = substring_match_BM.match(text=seq_str, pattern=pat_str)
    if -1 == match_idx:
        return False, -1

    return True, match_idx


def _merge_bars(line: np.ndarray, pt_cnt: List[int]) -> None or np.ndarray:
    assert line.size == np.sum(pt_cnt)
    assert False == np.isnan(np.max(line))

    line = line.astype(int)
    res = np.full_like(pt_cnt, -1, dtype=int)
    _line_ptr = 0
    for _pt_cnt_idx, _pt_cnt in enumerate(pt_cnt):
        _line_pts = line[_line_ptr: _line_ptr + _pt_cnt]
        _line_pts_unique = np.unique(_line_pts)  # support nans, even if should NEVER occur
        if 1 != len(_line_pts_unique):
            return None
        res[_pt_cnt_idx] = _line_pts_unique[0]
        _line_ptr += _pt_cnt
    return res


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
    if pattern_v3.ENCODING_LEVELS < len(_res):
        raise DecodeFailureVert("Too Many Levels: Expecting <= %d. Got %d"
                                % (pattern_v3.ENCODING_LEVELS, len(_res)))

    res = np.array(_res, dtype=int)
    return res


def _decode_handful_lines(lines_decoded: np.ndarray, cat_1_idx: int) -> Dict[str, int]:
    """
    Decode handful decoded lines
    :param lines_decoded:           of shape ((0,pattern_v3.ENCODING_LEVELS+2],
                                        pattern_v3.ENCODING_PATTERN_LENGTH or pattern_v3.ENCODING_LENGTH)
    :param cat_1_idx:               category_1 idx
    :return:                        {"category_1": cat_1_idx, "category_2": cat_2_idx}
                                    value is `None` if the corresponding key field cannot be decoded
                                    ("category_1" will never be `None`)
    """
    assert pattern_v3.ENCODING_LEVELS >= lines_decoded.shape[0] > 0, \
        "Lines Cnt Mismatch: Got %d" % lines_decoded.shape[0]
    assert (pattern_v3.ENCODING_PATTERN_LENGTH == lines_decoded.shape[1]) or \
           (pattern_v3.ENCODING_LENGTH == lines_decoded.shape[1]), "Length Mismatch: Got %d" % lines_decoded.shape[1]

    lines_decoded = lines_decoded.astype(int)
    lines_are_full_length = (pattern_v3.ENCODING_LENGTH == lines_decoded.shape[1])  # length lead to pattern
    res = {"category_1": cat_1_idx, "category_2": None}

    # find the line representing the category_1
    cat_1_pat = pattern_v3.get_bin_pattern_by_idx(idx=cat_1_idx)
    if lines_are_full_length:
        cat_1_pat = pattern_v3.get_sequence_by_pattern(pattern=cat_1_pat)
    cat_1_line_idx = -1
    for _line_idx, _line in enumerate(lines_decoded):
        if np.array_equal(_line, cat_1_pat) is True:
            cat_1_line_idx = _line_idx
            break
    assert -1 != cat_1_line_idx

    # remove all lines above the line representing the category_1
    lines_decoded = lines_decoded[cat_1_line_idx:, :]

    # [case 1] one valid line for category_1(LINE#1) only => end decoding
    if lines_are_full_length is False or lines_decoded.shape[0] < pattern_v3.ENCODING_LEVELS:
        return res

    # [case 2] two valid lines for category_1(LINE#1) and category_2(LINE#0) => continue decoding
    cat_2_bin = lines_decoded[0] ^ lines_decoded[1]
    cat_2_idx, _ = pattern_v3.non_dup_bin_2_dec(num=cat_2_bin, category_1_idx=cat_1_idx)
    res["category_2"] = cat_2_idx
    return res


def decode(sign_data_obj: TrafficSignsData,
           points: np.ndarray,
           hori_margin: int, vert_margin: int,
           height: int, width: int,
           is_scaled_height: bool,
           use_cnt_delta: bool,
           tolerable: Optional[bool] = False, ) \
        -> Tuple[Dict[str, int], Dict[str, str], Dict[str, Dict[str, int]]]:
    if 0 != np.nanmin(points).astype(int):
        raise DecodeFailure("No Sampled Points are Translated to 0")

    # === calculate the number of points on the encoding part
    max_cnt_encoding_hori_pt = np.floor(width * 1. * pattern_v3.ENCODING_LENGTH / hori_margin).astype(int) + 1
    if max_cnt_encoding_hori_pt < pattern_v3.ENCODING_PATTERN_LENGTH:
        raise DecodeFailureHori("Insufficient Data: Required >= %d on Encodings, Got <=%d"
                                % (pattern_v3.ENCODING_PATTERN_LENGTH, max_cnt_encoding_hori_pt))
    encoding_real_levels = pattern_v3.ENCODING_LEVELS if is_scaled_height is False else pattern_v3.ENCODING_LEVELS + 1
    max_cnt_encoding_vert_pt = np.floor(height * 1. * encoding_real_levels / vert_margin).astype(int) + 1
    if max_cnt_encoding_vert_pt < 1:
        raise DecodeFailureVert("Insufficient Data: Required >= 1 on Encodings, Got <1")

    # === generate all the possible plans of decode_width<->pattern, by the number of points on the encoding part
    # decode_schemas = []
    all_bin_patterns = pattern_v3.get_all_bin_patterns()
    all_bin_patterns_full = [pattern_v3.get_sequence_by_pattern(pattern=i) for i in all_bin_patterns]
    if max_cnt_encoding_hori_pt < pattern_v3.ENCODING_LENGTH:  # [4,8) guaranteed
        decode_schemas = [{"length": pattern_v3.ENCODING_PATTERN_LENGTH,
                           "width": width * 2, "patterns": all_bin_patterns}]
    elif max_cnt_encoding_hori_pt == pattern_v3.ENCODING_LENGTH:  # 7 guaranteed, 8 possible
        decode_schemas = [{"length": pattern_v3.ENCODING_PATTERN_LENGTH,
                           "width": width * 2, "patterns": all_bin_patterns},
                          {"length": pattern_v3.ENCODING_LENGTH,
                           "width": width, "patterns": all_bin_patterns_full}]
    else:  # i.e., max_cnt_encoding_hori_pt > pattern_v3.ENCODING_LENGTH:  # [8,+inf) guaranteed
        decode_schemas = [{"length": pattern_v3.ENCODING_LENGTH,
                           "width": width, "patterns": all_bin_patterns_full}]

    hori_bt_plans = []  # CHECKPOINT: focus on variable `points_sliced`
    for schema in decode_schemas:
        schema_length = schema["length"]
        schema_width = schema["width"]
        schema_all_patterns = schema["patterns"]
        schema_max_cnt_per_bar = np.floor(schema_width * 1. / hori_margin).astype(int) + 1
        _lines_pat_found, _line_idx_pat_found, _lines_found_pat_idx = False, -1, -1
        _lines_bt_plan = []
        for _line_idx, _line in enumerate(points):
            if _lines_pat_found is True:
                break
            _line_not_nan_idx = np.where(False == np.isnan(_line))
            _line_data = _line[_line_not_nan_idx]
            # skip this line if insufficient not-NANs samples are left for the schema
            if _line_data.size < schema_length:
                continue
            # skip this line if is all ones
            if 1 == int(np.min(_line_data)):
                continue
            _bt_comb = _decode_one_line(
                points=_line_data, bar_cnt=schema_length, max_cnt_per_bar=schema_max_cnt_per_bar)
            if 0 == len(_bt_comb):  # skip this line if no possible back-tracing results exist
                continue

            for __bt_comb_item in _bt_comb:
                __bt_comb_seq = __bt_comb_item["seq"]
                __bt_comb_plan = __bt_comb_item["pt_cnt"]

                # match pattern
                for ___pattern_idx, ___pattern in enumerate(schema_all_patterns):
                    if np.array_equal(___pattern, __bt_comb_seq) is True:
                        if _lines_found_pat_idx >= 0 and ___pattern_idx != _lines_found_pat_idx:
                            raise DecodeFailureHori("Multiple Patterns Found in one Line: %d, %d"
                                                    % (_lines_found_pat_idx, ___pattern_idx))
                        _lines_pat_found = True
                        if _lines_found_pat_idx < 0:
                            _lines_found_pat_idx = ___pattern_idx
                        _lines_bt_plan.append(__bt_comb_item)
                        _line_idx_pat_found = _line_idx
                        break

        if _lines_pat_found is False:
            continue

        # slice points for each back-tracing plan, decode and add to results
        for _bt_plan in _lines_bt_plan:
            _bt_plan_plan = _bt_plan["pt_cnt"]
            _slice_line_start = _line_idx_pat_found
            _plan_pat_line = points[_slice_line_start, :]  # must have 0s
            _slice_col_start = np.nanargmin(_plan_pat_line)
            _slice_col_end = _slice_col_start + np.sum(_bt_plan_plan)
            _points_sliced = points[_slice_line_start:, _slice_col_start: _slice_col_end]
            # decode
            _lines_decoded = [schema_all_patterns[_lines_found_pat_idx]]
            for __line in _points_sliced[1:, :]:
                if True == np.isnan(np.max(__line)):
                    break
                __line_decoded = _merge_bars(line=__line, pt_cnt=_bt_plan_plan)
                if __line_decoded is None:
                    break
                if 1 == int(np.min(__line_decoded)):
                    break
                _lines_decoded.append(__line_decoded)
            # add to result
            hori_bt_plans.append({
                "schema_length": schema_length,
                "schema_width": schema_width,
                "pattern_category": _lines_found_pat_idx,
                "pattern": schema_all_patterns[_lines_found_pat_idx],
                "bt_plan": _bt_plan_plan,
                "sliced": _points_sliced,
                "decoded": _lines_decoded,
            })

    if 0 == len(hori_bt_plans):  # CHECKPOINT: focus on variable `hori_bt_plans`
        raise DecodeFailureHori("No Possibilities for Bach-Tracing in Search for Patterns")

    # try to decode all merged plans
    _res_decoded = []  # CHECKPOINT: focus on variable `hori_plans_merged_shortened`
    _res_decoded_info = []  # [{"category_1"/"category_2": <str>}, ...]
    res_cnt_before_validation = 0
    res_cnt_after_validation = 0
    for _final_plan in hori_bt_plans:
        _res_category_1_idx = _final_plan["pattern_category"]
        _hori_res = _final_plan["decoded"]
        # if 0 == len(_hori_res):
        #     continue
        print(end="")  # CHECKPOINT: focus on variable `_hori_res`
        # === merge lines
        try:
            _vert_res = _merge_lines(lines_decoded=_hori_res)
        except DecodeFailureVert as err:
            continue
        print(end="")  # CHECKPOINT: focus on variable `_vert_res`
        # === actual decoder: handful decoded lines data to sign board info
        try:
            _decode_res = _decode_handful_lines(lines_decoded=_vert_res, cat_1_idx=_res_category_1_idx)
        except AssertionError as err:
            continue
        print(end="")  # CHECKPOINT: focus on variable `_decode_res`
        # === validate the decoded result (by data encoding properties)
        _decode_res_info = sign_data_obj.get_sign_info_by_idx(cat_1_idx=_decode_res["category_1"],
                                                              cat_2_idx=_decode_res["category_2"])
        res_cnt_before_validation += 1
        if _decode_res_info is not None:
            # validate the decoded result (by max possible encoding levels)
            _fields_cnt = int(_decode_res["category_1"] is not None) + \
                          int(_decode_res["category_2"] is not None)
            # omit impossibility: max lines cnt on encoding NOT sufficient for the levels extracted
            if _fields_cnt > max_cnt_encoding_vert_pt:
                continue
            # omit impossibility: levels extracted not complete for the min lines&length cnt on encoding
            if _fields_cnt < min(2, max_cnt_encoding_vert_pt - 1) and \
                    _fields_cnt < (max_cnt_encoding_hori_pt - 1) // pattern_v3.ENCODING_PATTERN_LENGTH:
                continue
            _res_decoded.append(_decode_res)
            _res_decoded_info.append(_decode_res_info)
            res_cnt_after_validation += 1

    if 0 == len(_res_decoded):  # CHECKPOINT: focus on variable `_res_decoded`, `_res_decoded_info`
        raise DecodeFailure("No Valid Possibilities while Translating Binary to Decimal")

    # tolerable parsing: merge as-many-as-possible fields
    #   Note: (observed phenomenon) two identical cat_1&cat_2 might be merged tolerably,
    #       since they can be decode results with different pattern-found-location (e.g. due to different leading 1s)
    res_cnt_before_toleration = len(_res_decoded) if len(_res_decoded) > 1 else 0
    res_cnt_after_toleration = 1 if len(_res_decoded) > 1 else 0
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
            if 1 != len(_res_dec_all_cat_2):
                print(end="")
            if 1 == len(_res_dec_all_cat_2):
                _res_decoded_tol["category_2"] = _res_decoded[0]["category_2"]
                _res_decoded_info_tol["category_2"] = _res_decoded_info[0]["category_2"]
            del _res_dec_all_cat_2
        del _res_dec_all_cat_1
        # merge tolerated if is successful
        if _res_decoded_tol_success is True:
            _res_decoded_info_tol["is_complete"] = (_res_decoded_tol["category_1"] is not None) and \
                                                   (_res_decoded_tol["category_2"] is not None)
            # if _res_decoded_info_tol["is_complete"] is True:
            #     print()
            _res_decoded_info_tol["is_tolerated"] = True
            _res_decoded = [_res_decoded_tol]
            _res_decoded_info = [_res_decoded_info_tol]

    if 1 < len(_res_decoded):
        raise DecodeFailureHori("Multiple Valid Possibilities: Expecting 1. Got %d" % len(_res_decoded))
    res_decoded = _res_decoded[0]
    res_decoded_info = _res_decoded_info[0]

    return res_decoded, res_decoded_info, \
           {
               "validation": {"before": res_cnt_before_validation, "after": res_cnt_after_validation},
               "toleration": {"before": res_cnt_before_toleration, "after": res_cnt_after_toleration},
           }


if "__main__" == __name__:
    a = np.array([0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0.])
    b = _decode_one_line(points=a, bar_cnt=8, max_cnt_per_bar=2)
    print()
