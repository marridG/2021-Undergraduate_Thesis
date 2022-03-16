from typing import *
import numpy as np

from encoding_v2 import pattern_v2


def encode(sample: Dict[str, Union[str, None, int, Dict[str, int]]]) -> np.ndarray:
    """
    Encode the given traffic sign sample to binary representations
    :param sample:          given sample of traffic signs.
                                e.g. {'str': 'pb', 'num': None, 'encoding': {'category': 1, 'idx': 34}}
    :return:                binary representation of the given sample
    """
    res_length = 8
    res = np.full((3, res_length), -1, dtype=int)

    # fill the second row: 1-ST category
    _category_1 = sample["encoding"]["category"]  # int
    _res_2_cat_1 = pattern_v2.get_pattern(idx=_category_1)  # np.ndarray
    res[1, :] = _res_2_cat_1

    # fill the last row: possible number on the traffic sign
    if sample["num"] is None:
        _num_bin = np.full((res_length,), fill_value=1, dtype=int)
    else:
        _num_bin = pattern_v2.dec_2_non_dup_bin(num=sample["num"], digit=res_length,
                                                category_1_idx=_category_1, is_num=True)
    _res_3_num = np.abs(_num_bin - res[1, :])
    res[-1, :] = _res_3_num

    # fill the first row: 2-ST category
    _category_2 = sample["encoding"]["idx"]  # int
    _cat_2_bin = pattern_v2.dec_2_non_dup_bin(num=_category_2, digit=res_length,
                                              category_1_idx=_category_1, is_category_2=True)
    _res_2_cat_2 = np.abs(_cat_2_bin - res[1, :])  # res_repr = abs(target-row)
    res[0, :] = _res_2_cat_2

    return res


if "__main__" == __name__:
    pass
    print()
