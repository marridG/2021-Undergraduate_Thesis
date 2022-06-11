import numpy as np

ALL_POS = [
    # [0, 0],
    [0, 1],
    [1, 0],
    [1, 1],
]

COL_WIDTH = 100
MAX_IDX = len(ALL_POS[0]) * COL_WIDTH - 1

to_sample = []
for _pos in ALL_POS:
    _to_sam = []
    for __pos_bit in _pos:
        for i in range(COL_WIDTH):
            _to_sam.append(__pos_bit)
    to_sample.append(np.array(_to_sam))
print("To-Sample Generated")


def gen_all_loc(start, margin) -> np.ndarray:
    res = []
    _crt_loc = start
    while _crt_loc <= MAX_IDX:
        res.append(_crt_loc)
        _crt_loc += margin

    res = np.array(res)
    return res


def plan_is_valid(all_loc: np.ndarray) -> bool:
    all_loc_bin_idx = np.floor(all_loc * 1. / COL_WIDTH)
    _arr_ptr = 0
    for _bin_idx in range(len(ALL_POS[0])):
        if 0 == np.where(all_loc_bin_idx == _bin_idx)[0].size:
            return False
    return True


# <dict>, { margin: { start: [<int>], ... } }
sample_plans = {}
for _margin in range(1, COL_WIDTH):
    sample_plans[_margin] = {}
    for __start_loc in range(COL_WIDTH):
        __all_loc = gen_all_loc(start=__start_loc, margin=_margin)
        __plan_is_valid = plan_is_valid(all_loc=__all_loc)
        if __plan_is_valid is True:
            sample_plans[_margin][__start_loc] = __all_loc

print("All Sample Plans Generated")


def sample_arr_2_str(sample_arr: np.ndarray) -> str:
    res = "".join([str(i) for i in sample_arr])
    return res


_all_plans_passed = True
for _margin, _margin_plans in sample_plans.items():
    _sample_res_set = [set(), set(), set()]
    _sample_res_str_2_loc = [{}, {}, {}]
    for __plan_start, __plan in _margin_plans.items():
        for __pattern_idx in range(len(ALL_POS)):
            __pattern = to_sample[__pattern_idx]
            __pattern_sample_arr = __pattern[__plan]
            __pattern_sample_str = sample_arr_2_str(sample_arr=__pattern_sample_arr)
            _sample_res_set[__pattern_idx].add(__pattern_sample_str)
            try:
                _sample_res_str_2_loc[__pattern_idx][__pattern_sample_str].append(
                    {"start": __plan_start, "loc": __plan})
            except KeyError:
                _sample_res_str_2_loc[__pattern_idx][__pattern_sample_str] = [{"start": __plan_start, "loc": __plan}]

    intersect_12 = _sample_res_set[0].intersection(_sample_res_set[1])
    intersect_13 = _sample_res_set[0].intersection(_sample_res_set[2])
    intersect_23 = _sample_res_set[1].intersection(_sample_res_set[2])

    if 0 != len(intersect_12):
        _all_plans_passed = False
        print("#1-#2 Duplicate:", intersect_12)
        for _dup in intersect_12:
            print("\t", _sample_res_str_2_loc[0][_dup], " || ", _sample_res_str_2_loc[1][_dup])
    elif 0 != len(intersect_13):
        _all_plans_passed = False
        print("#1-#3 Duplicate:", intersect_13)
        for _dup in intersect_13:
            print("\t", _sample_res_str_2_loc[0][_dup], " || ", _sample_res_str_2_loc[2][_dup])
    elif 0 != len(intersect_23):
        _all_plans_passed = False
        print("#2-#3 Duplicate:", intersect_23)
        for _dup in intersect_23:
            print("\t", _sample_res_str_2_loc[1][_dup], " || ", _sample_res_str_2_loc[2][_dup])
    else:
        print("#1 INT-SEC #2:", intersect_12)
        print("#1 INT-SEC #3:", intersect_13)
        print("#2 INT-SEC #3:", intersect_23)
        print("====================")
        print()

print()
print("========== ALL PLANS PASSED = %r ==========" % _all_plans_passed)
