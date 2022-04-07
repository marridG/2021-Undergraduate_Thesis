from typing import List
import numpy as np

from simulation import utils
from data_v2 import constants

ENCODING_LENGTH = 8
ENCODING_LEVELS = 2
ENCODING_PATTERN_LENGTH = 4

# sub patterns for 1st category
_ALL_BIN_PATTERNS = [
    np.array([0, 0, 1, 1], dtype=int),
    np.array([0, 1, 1, 0], dtype=int),
    np.array([0, 0, 0, 0], dtype=int),
]
# indices to be avoided so as not to emerge the same sub-sequence (for 1st category) used on the boards
_all_avoid_bin_dec_set = set()  # seq = board_dup + category_1_seq
_all_cat_2_bin = [[0, i1, 0, i3, 0, i5, 0, i7]
                  for i1 in range(2) for i3 in range(2) for i5 in range(2) for i7 in range(2)] + \
                 [[i0, 0, i2, 0, i4, 0, i6, 0]
                  for i0 in range(2) for i2 in range(2) for i4 in range(2) for i6 in range(2)]  # original bin
for __cat_2_bin in _all_cat_2_bin:
    __cat_2_bin = np.array(__cat_2_bin)
    __cat_2_dec = utils.num_bin_2_dec(num=__cat_2_bin)
    _all_avoid_bin_dec_set.add(__cat_2_dec)
_ALL_BIN_PATTERNS_AVOID_DEC_IDX_SET = _all_avoid_bin_dec_set
_ALL_BIN_PATTERNS_AVOID_DEC_IDX_LIST = sorted(list(_all_avoid_bin_dec_set))
_ALL_BIN_PATTERNS_DEC_IDX_SUBSTITUTION_ORI_2_SUB = {
    # substitutions of the avoided indices: category_1_idx->avoided_original->substitution
    0: {}, 1: {}, 2: {},
}
_ALL_BIN_PATTERNS_DEC_IDX_SUBSTITUTION_SUB_2_ORI = {
    # substitutions of the avoided indices: category_1_idx->substitution->avoided_original
    0: {}, 1: {}, 2: {},
}
for _cat_idx in range(constants.CNT_CATEGORY_1):  # todo: remove impossible to-be-avoided cat_2 idx
    _crt_sub = constants.CNT_CATEGORY_2
    for __avoid_idx in _ALL_BIN_PATTERNS_AVOID_DEC_IDX_LIST:
        while (_crt_sub in _ALL_BIN_PATTERNS_AVOID_DEC_IDX_SET) is True:
            _crt_sub += 1
        _ALL_BIN_PATTERNS_DEC_IDX_SUBSTITUTION_ORI_2_SUB[_cat_idx][__avoid_idx] = _crt_sub
        _ALL_BIN_PATTERNS_DEC_IDX_SUBSTITUTION_SUB_2_ORI[_cat_idx][_crt_sub] = __avoid_idx
        _crt_sub += 1


def get_sequence_by_pattern(pattern: np.ndarray) -> np.ndarray:
    """[1,0,1,1] => [1,1, 0,0, 1,1, 1,1]"""
    res = np.zeros((ENCODING_LENGTH,), dtype=int)
    res[0::2] = pattern
    res[1::2] = pattern
    return res


def get_pattern_by_sequence(sequence: np.ndarray) -> None or np.ndarray:
    """[1,1, 0,0, 1,1, 1,1] => [1,0,1,1]"""
    res_1 = sequence[0::2]
    res_2 = sequence[1::2]
    assert np.array_equal(res_1, res_2)

    return res_2


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


def dec_2_non_dup_bin(num: int, digit: int, category_1_idx: int, is_category_2: bool = False) -> (np.ndarray, int):
    """
    Translate the given DECIMAL number, representing the indices of either the 2nd category or
        number part of the traffic sign (but never both), into its BINARY form
        without interfering the pattern of the given category_1 index
    :param num:                 given DECIMAL number
    :param digit:               maximum digits of the binary form (unused digits from the MSB will be 0;
                                    must be sufficient for the binary form)
    :param category_1_idx:      given category_1 index (determines which pattern to avoid)
    :param is_category_2:       whether the DECIMAL number is representing the 2nd category.
                                    `True` is so, `False` otherwise
    :return:                    (1) bin of non-dup idx (translation result);
                                (2) dec of non-dup idx (for debug)
    """
    # given number will be presented on the board in the same pattern sequence with that of the given category_1 index
    try:
        num_sub = _ALL_BIN_PATTERNS_DEC_IDX_SUBSTITUTION_ORI_2_SUB[category_1_idx][num]
        num = num_sub
    except KeyError:
        pass

    res = utils.num_dec_2_bin(num=num, digit=digit)
    return res, num


def non_dup_bin_2_dec(num: np.ndarray, category_1_idx: int, is_category_2: bool = False) -> (int, int):
    """
    Translate the given non-duplicate BINARY number, representing the indices of either the 2nd category or
        number part of the traffic sign (but never both), into its DECIMAL form\
    :param num:                 given BINARY number
    :param category_1_idx:      given category_1 index (determines which pattern is possibly avoided)
    :param is_category_2:       whether the DECIMAL BINARY is representing the 2nd category.
                                    `True` is so, `False` otherwise
    :return:                    (1) original dec of non-dup bin (translation result);
                                (2) direct dec of non-dup bin (for debug)
    """

    res = utils.num_bin_2_dec(num=num)  # <int>
    try:
        num_ori = _ALL_BIN_PATTERNS_DEC_IDX_SUBSTITUTION_SUB_2_ORI[category_1_idx][res]
        return num_ori, res
    except KeyError:
        pass

    return res, res


if "__main__" == __name__:
    print()
