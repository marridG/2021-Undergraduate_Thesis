from typing import List
import numpy as np

from simulation import utils
from data_v1 import constants

ENCODING_LENGTH = 8
ENCODING_LEVELS = 3

# PATTERN: 10110110110110110...
# sub patterns for 1st category
_ALL_BIN_PATTERNS = [
    # np.array([1, 0, 1, 1, 0, 1, 1, 0], dtype=int),
    # np.array([0, 1, 1, 0, 1, 1, 0, 1], dtype=int),
    # np.array([1, 1, 0, 1, 1, 0, 1, 1], dtype=int),
    np.array([0, 1, 1, 1, 1, 1, 1, 0], dtype=int),
    np.array([0, 1, 0, 0, 1, 1, 0, 0], dtype=int),
    np.array([0, 0, 0, 0, 1, 1, 1, 0], dtype=int),
]
# indices to be avoided so as not to emerge the same sub-sequence (for 1st category) used on the  boards
_ALL_BIN_PATTERNS_AVOID_DEC_IDX = [utils.num_bin_2_dec(num=np.zeros_like(i, dtype=int))
                                   for i in _ALL_BIN_PATTERNS]  # seq = board_dup + category_1_seq
_ALL_BIN_PATTERNS_DEC_IDX_SUBSTITUTION_USAGE_2_IDX = {
    # substitutions of the avoided indices: category_1_idx->usage->substitution
    0: {"category_2": constants.CNT_CATEGORY_2 + 1, "numbers": constants.CNT_NUM + 1},
    1: {"category_2": constants.CNT_CATEGORY_2 + 2, "numbers": constants.CNT_NUM + 2},
    2: {"category_2": constants.CNT_CATEGORY_2 + 3, "numbers": constants.CNT_NUM + 3},
}
# _ALL_BIN_PATTERNS_DEC_IDX_SUBSTITUTION_IDX_2_USAGE = {
#     # reversed reference tables [ALERT] duplicate key `_idx` may occur if the counts are similar!
#     _idx: {"usage": _usage, "category_1": _cat_1}
#     for _cat_1, _usage_n_idx in _ALL_BIN_PATTERNS_DEC_IDX_SUBSTITUTION_USAGE_2_IDX.items()
#     for _usage, _idx in _usage_n_idx.items()
# }

# _PATTERN_CNT_TO_PATTERN = {
#     # (3, 2): 0, (2, 3): 1, (3, 3): 2,
#     (3, 3): 0, (1, 2): 1, (0, 3): 2
# }
_IDX_2_BIN_PATTERN = {
    0: _ALL_BIN_PATTERNS[0],
    1: _ALL_BIN_PATTERNS[1],
    2: _ALL_BIN_PATTERNS[2],
}


def get_idx_by_bin_pattern(pattern: np.ndarray) -> int:
    # res = _PATTERN_CNT_TO_PATTERN[(pattern_cnt_1, pattern_cnt_2)]
    for _pat_idx, _pat in enumerate(_ALL_BIN_PATTERNS):
        if np.array_equal(_pat, pattern) is True:
            return _pat_idx
    raise RuntimeError("Pattern Not Found:", pattern)


def get_bin_pattern_by_idx(idx: int) -> np.ndarray:
    res = _IDX_2_BIN_PATTERN[idx]
    return res


def get_all_bin_patterns() -> List[np.ndarray]:
    return _ALL_BIN_PATTERNS


def dec_2_non_dup_bin(num: int, digit: int, category_1_idx: int,
                      is_category_2: bool = False, is_num: bool = False) -> np.ndarray:
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
    :param is_num:              whether the DECIMAL number is representing the number part.
                                    `True` is so, `False` otherwise
    :return:
    """
    assert (is_category_2 ^ is_num) is True  # either is True, but not both

    avoid_dec = _ALL_BIN_PATTERNS_AVOID_DEC_IDX[category_1_idx]
    # given number will be presented on the board in the same pattern sequence with that of the given category_1 index
    if num == avoid_dec:
        _usage_str = "category_2" if is_category_2 is True else "numbers"
        num = _ALL_BIN_PATTERNS_DEC_IDX_SUBSTITUTION_USAGE_2_IDX[category_1_idx][_usage_str]

    res = utils.num_dec_2_bin(num=num, digit=digit)
    return res


def non_dup_bin_2_dec(num: np.ndarray, category_1_idx: int,
                      is_category_2: bool = False, is_num: bool = False) -> int:
    """
    Translate the given non-duplicate BINARY number, representing the indices of either the 2nd category or
        number part of the traffic sign (but never both), into its DECIMAL form\
    :param num:                 given BINARY number
    :param category_1_idx:      given category_1 index (determines which pattern is possibly avoided)
    :param is_category_2:       whether the DECIMAL BINARY is representing the 2nd category.
                                    `True` is so, `False` otherwise
    :param is_num:              whether the BINARY number is representing the number part.
                                    `True` is so, `False` otherwise
    :return:
    """
    assert (is_category_2 ^ is_num) is True  # either is True, but not both

    res = utils.num_bin_2_dec(num=num)  # <int>
    _usage_str = "category_2" if is_category_2 is True else "numbers"
    if _ALL_BIN_PATTERNS_DEC_IDX_SUBSTITUTION_USAGE_2_IDX[category_1_idx][_usage_str] == res:
        res = _ALL_BIN_PATTERNS_AVOID_DEC_IDX[category_1_idx]
    return res


if "__main__" == __name__:
    print()
