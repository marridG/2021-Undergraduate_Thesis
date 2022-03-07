from typing import *
import numpy as np


def _dec_2_bin(num: int, digit: int) -> np.ndarray:
    res = np.zeros(digit, dtype=int)
    num_bin_str = bin(num)  # "0b******"
    num_bin_str = num_bin_str[2:]  # "******"
    # number of digit to move right-hand-side while assigning numbers from the str to the result
    _delta_digit = digit - len(num_bin_str)
    assert _delta_digit >= 0, \
        "Given Decimal Number %d Exceeds the Range of Binary Numbers of the %d Digits" % (num, digit)

    for i in range(len(num_bin_str)):
        res[i + _delta_digit] = int(eval(num_bin_str[i]))

    return res


def encode(sample: Dict[str, Union[str, None, int, Dict[str, int]]]) -> np.ndarray:
    """
    Encode the given traffic sign sample to binary representations
    :param sample:          given sample of traffic signs.
                                e.g. {'str': 'pb', 'num': None, 'encoding': {'category': 1, 'idx': 34}}
    :return:                binary representation of the given sample
    """
    res_length = 8
    res = np.full((3, res_length), -1, dtype=int)

    # fill the last row: possible number on the traffic sign
    if sample["num"] is None:
        res[-1, :] = 1
    else:
        _num_bin = _dec_2_bin(num=sample["num"], digit=res_length)
        _res_3_num = _num_bin
        res[-1, :] = _res_3_num

    # fill the first row: 1-ST category
    _category = sample["encoding"]["category"]  # int
    _cat_1_bin = _dec_2_bin(num=_category, digit=2)
    _res_1_cat_1 = np.array([_cat_1_bin[0]] * (res_length // 2) + [_cat_1_bin[1]] * (res_length // 2))
    _res_1_cat_1 = np.abs(_res_1_cat_1 - res[-1, :])  # res_repr = abs(target-row)
    res[0, :] = _res_1_cat_1

    # fill the second row: 2-ST category
    _category = sample["encoding"]["idx"]  # int
    _cat_2_bin = _dec_2_bin(num=_category, digit=res_length)
    _res_2_cat_2 = np.abs(_cat_2_bin - res[-1, :])  # res_repr = abs(target-row)
    res[1, :] = _res_2_cat_2

    return res


if "__main__" == __name__:
    print(_dec_2_bin(num=4, digit=5))
