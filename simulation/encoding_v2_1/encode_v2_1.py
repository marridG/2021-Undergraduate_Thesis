from typing import *
import numpy as np

from encoding_v2_1 import pattern_v2_1


def encode(sample: Dict[str, Union[str, None, int, Dict[str, int]]]) -> np.ndarray:
    """
    Encode the given traffic sign sample to binary representations
    :param sample:          given sample of traffic signs.
                                e.g. {'str': 'pb', 'encoding': {'category': 1, 'idx': 34}}
    :return:                binary representation of the given sample
    """
    res_length = pattern_v2_1.ENCODING_LENGTH
    res = np.full((pattern_v2_1.ENCODING_LEVELS, res_length), -1, dtype=int)

    # fill the 1ST row: 1-ST category
    _category_1 = sample["encoding"]["category"]  # int
    _res_2_cat_1_pat = pattern_v2_1.get_bin_pattern_by_idx(idx=_category_1)  # 4 digit <np.ndarray>
    _res_2_cat_1 = pattern_v2_1.get_sequence_by_pattern(pattern=_res_2_cat_1_pat)  # 8 digit
    res[0, :] = _res_2_cat_1

    # fill the 2ND row: 2-ND category
    _category_2 = sample["encoding"]["idx"]  # int
    _cat_2_bin = pattern_v2_1.dec_2_non_dup_bin(num=_category_2, digit=res_length,
                                                category_1_idx=_category_1, is_category_2=True)
    _res_2_cat_2 = np.abs(_cat_2_bin - res[0, :])  # res_repr = abs(target-row)
    res[1, :] = _res_2_cat_2

    return res


if "__main__" == __name__:
    pass
    print()
