import numpy as np

from data_v2 import constants
import utils

cat_1 = [
    np.array([0, 0, 0, 0, 0, 0, 0, 0], dtype=int),
    np.array([0, 0, 0, 0, 1, 1, 1, 1], dtype=int),
    np.array([1, 1, 1, 1, 0, 0, 0, 0], dtype=int),
]

cat1lr_2_idx = {}  # {(cat_1, left, right): [idx]}
idx_2_cat1lr = {}
for num_dec in range(256):
    num_bin = 1 - utils.num_dec_2_bin(num=num_dec, digit=8)
    for _cat_1_idx, _cat_1 in enumerate(cat_1):
        _num_cat_1 = np.abs(_cat_1 - num_bin)  # res_repr = abs(target-row)
        _num_cat_1_sum_left = int(np.sum(_num_cat_1[:4]).astype(int))
        _num_cat_1_sum_right = int(np.sum(_num_cat_1[4:]).astype(int))
        # print("IDX=%d\t#%d\t(%d,%d)" % (num_dec, _cat_1_idx, _num_cat_1_sum_left, _num_cat_1_sum_right))
        _key = tuple((_cat_1_idx, _num_cat_1_sum_left, _num_cat_1_sum_right))
        try:
            cat1lr_2_idx[_key].append(num_dec)
        except KeyError:
            cat1lr_2_idx[_key] = [num_dec]
        try:
            idx_2_cat1lr[num_dec].append(_key)
        except KeyError:
            idx_2_cat1lr[num_dec] = [_key]

print()
