import numpy as np

from simulation import utils
from data import constants

# PATTERN: 10110110110110110...
# sub patterns for 1st category
_ALL_BIN_PATTERNS = [
    np.array([1, 0, 1, 1, 0, 1, 1, 0], dtype=int),
    np.array([0, 1, 1, 0, 1, 1, 0, 1], dtype=int),
    np.array([1, 1, 0, 1, 1, 0, 1, 1], dtype=int),
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
_ALL_BIN_PATTERNS_DEC_IDX_SUBSTITUTION_IDX_2_USAGE = {
    # reversed reference tables [ALERT] duplicate key `_idx` may occur if the counts are similar!
    _idx: {"usage": _usage, "category_1": _cat_1}
    for _cat_1, _usage_n_idx in _ALL_BIN_PATTERNS_DEC_IDX_SUBSTITUTION_USAGE_2_IDX.items()
    for _usage, _idx in _usage_n_idx.items()
}

_PATTERN_CNT_TO_PATTERN = {(3, 2): 0, (2, 3): 1, (3, 3): 2}
_IDX_2_BIN_PATTERN = {
    0: _ALL_BIN_PATTERNS[0],
    1: _ALL_BIN_PATTERNS[1],
    2: _ALL_BIN_PATTERNS[2],
}


def get_idx(pattern_cnt_1: int, pattern_cnt_2: int) -> int:
    res = _PATTERN_CNT_TO_PATTERN[(pattern_cnt_1, pattern_cnt_2)]
    return res


def get_pattern(idx: int) -> np.ndarray:
    res = _IDX_2_BIN_PATTERN[idx]
    return res


def dec_2_non_dup_bin(num: int, digit: int, category_1_idx: int,
                      is_category_2: bool = False, is_num: bool = False) -> np.ndarray:
    """
    translate the given DECIMAL number, representing the indices of either the 2nd category or
        number part of the traffic sign (but never both), into its BINARY form
        without interfering the pattern of the given category_1 index
    :param num:                 given DECIMAL number
    :param digit:               maximum digits of the binary form (unused digits from the MSB will be 0;
                                    must be sufficient for the binary form)
    :param category_1_idx:      given category_1 index (determines which pattern to avoid)
    :param is_category_2:       whether the DECIMAL number is representing the 2nd category.
                                    `True` is so, `False` otehrwise
    :param is_num:              whether the DECIMAL number is representing the number part.
                                    `True` is so, `False` otehrwise
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


if "__main__" == __name__:
    print()
