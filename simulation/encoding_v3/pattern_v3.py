from typing import List
import numpy as np

from simulation import utils
from data_v2 import constants

ENCODING_LENGTH = 8
ENCODING_LEVELS = 2
ENCODING_PATTERN_LENGTH = 2

# sub patterns for 1st category
_ALL_BIN_PATTERNS = [
    np.array([0, 1], dtype=int),
    np.array([1, 0], dtype=int),
    np.array([1, 1], dtype=int),
]
# indices to be avoided so that there will be no all-zero columns
avoid = [
    ("warning",  # [0, 1]
     [[0, 0, 0, 0, i1, i2, i3, i4]
      for i1 in range(2) for i2 in range(2) for i3 in range(2) for i4 in range(2)] + \
     [[0, 0, 1, 0, i1, i2, i3, i4]
      for i1 in range(2) for i2 in range(2) for i3 in range(2) for i4 in range(2)] + \
     [[0, 0, 0, 1, i1, i2, i3, i4]
      for i1 in range(2) for i2 in range(2) for i3 in range(2) for i4 in range(2)] + \
     [[0, 1, 0, 0, i1, i2, i3, i4]
      for i1 in range(2) for i2 in range(2) for i3 in range(2) for i4 in range(2)] + \
     [[0, 1, 1, 0, i1, i2, i3, i4]
      for i1 in range(2) for i2 in range(2) for i3 in range(2) for i4 in range(2)] + \
     [[0, 1, 0, 1, i1, i2, i3, i4]
      for i1 in range(2) for i2 in range(2) for i3 in range(2) for i4 in range(2)] + \
     [[1, 0, 0, 0, i1, i2, i3, i4]
      for i1 in range(2) for i2 in range(2) for i3 in range(2) for i4 in range(2)] + \
     [[1, 0, 1, 0, i1, i2, i3, i4]
      for i1 in range(2) for i2 in range(2) for i3 in range(2) for i4 in range(2)] + \
     [[1, 0, 0, 1, i1, i2, i3, i4]
      for i1 in range(2) for i2 in range(2) for i3 in range(2) for i4 in range(2)]
     ),

    ("prohibitory",  # [1, 0]
     [[i1, i2, i3, i4, 0, 0, 0, 0]
      for i1 in range(2) for i2 in range(2) for i3 in range(2) for i4 in range(2)] + \
     [[i1, i2, i3, i4, 0, 0, 1, 0]
      for i1 in range(2) for i2 in range(2) for i3 in range(2) for i4 in range(2)] + \
     [[i1, i2, i3, i4, 0, 0, 0, 1]
      for i1 in range(2) for i2 in range(2) for i3 in range(2) for i4 in range(2)] + \
     [[i1, i2, i3, i4, 0, 1, 0, 0]
      for i1 in range(2) for i2 in range(2) for i3 in range(2) for i4 in range(2)] + \
     [[i1, i2, i3, i4, 0, 1, 1, 0]
      for i1 in range(2) for i2 in range(2) for i3 in range(2) for i4 in range(2)] + \
     [[i1, i2, i3, i4, 0, 1, 0, 1]
      for i1 in range(2) for i2 in range(2) for i3 in range(2) for i4 in range(2)] + \
     [[i1, i2, i3, i4, 1, 0, 0, 0]
      for i1 in range(2) for i2 in range(2) for i3 in range(2) for i4 in range(2)] + \
     [[i1, i2, i3, i4, 1, 0, 1, 0]
      for i1 in range(2) for i2 in range(2) for i3 in range(2) for i4 in range(2)] + \
     [[i1, i2, i3, i4, 1, 0, 0, 1]
      for i1 in range(2) for i2 in range(2) for i3 in range(2) for i4 in range(2)]
     ),

    ("mandatory",  # [1, 1]
     [])
]
_ALL_BIN_AVOID_DEC_BY_CAT = {"warning": set(), "prohibitory": set(), "mandatory": set()}  # decimal of binary
for _c1_str, _c2s in avoid:
    for __c2 in _c2s:
        __c2 = np.array(__c2)
        __cat_2_dec = utils.num_bin_2_dec(num=__c2)
        _ALL_BIN_AVOID_DEC_BY_CAT[_c1_str].add(__cat_2_dec)
_ALL_BIN_DEC_SUBSTITUTION_ORI_2_SUB = {
    # substitutions of the avoided indices: category_1_idx->avoided_original->substitution
    0: {}, 1: {}, 2: {},
}
_ALL_BIN_DEC_SUBSTITUTION_SUB_2_ORI = {
    # substitutions of the avoided indices: category_1_idx->substitution->avoided_original
    0: {}, 1: {}, 2: {},
}

for _cat_idx in range(constants.CNT_CATEGORY_1):
    _cat_str = {0: "warning", 1: "prohibitory", 2: "mandatory"}[_cat_idx]
    _crt_avoid = _ALL_BIN_AVOID_DEC_BY_CAT[_cat_str]
    _crt_sub = constants.CNT_CATEGORY_2_BY_CAT[_cat_str]
    for __avoid_idx in _crt_avoid:
        if __avoid_idx >= constants.CNT_CATEGORY_2_BY_CAT[_cat_str]:
            break
        while (_crt_sub in _crt_avoid) is True:
            _crt_sub += 1
        _ALL_BIN_DEC_SUBSTITUTION_ORI_2_SUB[_cat_idx][__avoid_idx] = _crt_sub
        _ALL_BIN_DEC_SUBSTITUTION_SUB_2_ORI[_cat_idx][_crt_sub] = __avoid_idx
        _crt_sub += 1
print(end="")


def get_sequence_by_pattern(pattern: np.ndarray) -> np.ndarray:
    """[0,1] => [0,0,0,0, 1,1,1,1]"""
    res = np.zeros((ENCODING_LENGTH,), dtype=int)
    res[0:4] = pattern[0]
    res[4:] = pattern[1]
    return res


def get_pattern_by_sequence(sequence: np.ndarray) -> None or np.ndarray:
    """[0,0,0,0, 1,1,1,1] => [0,1]"""
    res_1 = sequence[0::4]
    res_2 = sequence[1::4]
    res_3 = sequence[2::4]
    res_4 = sequence[3::4]
    assert np.array_equal(res_1, res_2) and np.array_equal(res_2, res_3) and np.array_equal(res_3, res_4)

    return res_1


def get_idx_by_bin_pattern(pattern: np.ndarray) -> int:
    for _pat_idx, _pat in enumerate(_ALL_BIN_PATTERNS):
        if np.array_equal(_pat, pattern) is True:
            return _pat_idx
    raise RuntimeError("Pattern Not Found:", pattern)


def get_bin_pattern_by_idx(idx: int) -> np.ndarray:
    res = _ALL_BIN_PATTERNS[idx]
    return res


def get_all_bin_patterns() -> List[np.ndarray]:
    return _ALL_BIN_PATTERNS


def dec_2_non_dup_bin(num: int, digit: int, category_1_idx: int) -> (np.ndarray, int):
    """
    Translate the given DECIMAL number, representing the indices of either the 2nd category or
        number part of the traffic sign (but never both), into its BINARY form,
        where no all-zero columns occur
    :param num:                 given DECIMAL number
    :param digit:               maximum digits of the binary form (unused digits from the MSB will be 0;
                                    must be sufficient for the binary form)
    :param category_1_idx:      given category_1 index (determines which pattern to avoid)
    :return:                    (1) bin of non-dup idx (translation result);
                                (2) dec of non-dup idx (for debug)
    """
    # given number will be presented on the board in the same pattern sequence with that of the given category_1 index
    try:
        num_sub = _ALL_BIN_DEC_SUBSTITUTION_ORI_2_SUB[category_1_idx][num]
        num = num_sub
    except KeyError:
        pass

    res = utils.num_dec_2_bin(num=num, digit=digit)
    return res, num


def non_dup_bin_2_dec(num: np.ndarray, category_1_idx: int) -> (int, int):
    """
    Translate the given non-duplicate BINARY number, representing the indices of the 2nd category into its DECIMAL form
    :param num:                 given BINARY number
    :param category_1_idx:      given category_1 index (determines which pattern is possibly avoided)
    :return:                    (1) original dec of non-dup bin (translation result);
                                (2) direct dec of non-dup bin (for debug)
    """

    res = utils.num_bin_2_dec(num=num)  # <int>
    try:
        num_ori = _ALL_BIN_DEC_SUBSTITUTION_SUB_2_ORI[category_1_idx][res]
        return num_ori, res
    except KeyError:
        pass

    return res, res


if "__main__" == __name__:
    print()
