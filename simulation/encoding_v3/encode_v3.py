from typing import *
import numpy as np

from encoding_v3 import pattern_v3


def encode(sample: Dict[str, Union[str, None, int, Dict[str, int]]],
           use_scaled_height: bool = False) -> np.ndarray:
    """
    Encode the given traffic sign sample to binary representations
    :param sample:          given sample of traffic signs.
                                e.g. {'str': 'pb', 'encoding': {'category': 1, 'idx': 34}}
    :param use_scaled_height:whether to use scaled height according to the horizontal encoding designs
                                (here, minimum digits required for cat_1/cat_2 is 4/8, so ideally,
                                the vertical height of cat_1/cat_2 should be 2:1)
    :return:                binary representation of the given sample
    """
    print("Start Generating Binary Encodings %s..." % ("" if not use_scaled_height else "(Using Scaled Height)"))
    res_length = pattern_v3.ENCODING_LENGTH
    res_rows = pattern_v3.ENCODING_LEVELS if use_scaled_height is False else pattern_v3.ENCODING_LEVELS + 1
    res = np.full((res_rows, res_length), -1, dtype=int)

    # fill the 1ST row in the encoding (IDX[-2]): 1-ST category
    _category_1 = sample["encoding"]["category"]  # int
    _res_cat_1_pat = pattern_v3.get_bin_pattern_by_idx(idx=_category_1)  # 2 digit <np.ndarray>
    _res_1_cat_1 = pattern_v3.get_sequence_by_pattern(pattern=_res_cat_1_pat)  # 8 digit
    res[-2, :] = _res_1_cat_1
    print("\tCat_1: %3d           ," % _category_1, _res_1_cat_1)

    # fill the scaled (for redundancy) 1ST row in the encoding (IDX[-3])
    if use_scaled_height is True:
        res[-3, :] = _res_1_cat_1

    # fill the 2ND row in the encoding (IDX[-1]): 2-ND category
    _category_2 = sample["encoding"]["idx"]  # int
    _cat_2_bin, _cat_2_real_dec = pattern_v3.dec_2_non_dup_bin(num=_category_2, digit=res_length,
                                                                 category_1_idx=_category_1)
    _res_2_cat_2 = np.abs(_cat_2_bin - res[0, :])  # res_repr = abs(target-row)
    res[-1, :] = _res_2_cat_2
    print("\tCat_2: %3d (from %3d)," % (_cat_2_real_dec, _category_2), _cat_2_bin)
    print("\t       ==============>", _res_2_cat_2)

    print("=== DONE ===")
    return res


if "__main__" == __name__:
    pass
    print()
