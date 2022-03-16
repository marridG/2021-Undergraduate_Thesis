import numpy as np


def degree_2_radian(deg: float) -> float:
    return (deg / 180.) * np.pi


def radian_2_degree(rad: float) -> float:
    return (rad / np.pi) * 180.


def num_dec_2_bin(num: int, digit: int) -> np.ndarray:
    """
    translate the given DECIMAL number into its BINARY form
    :param num:                 given DECIMAL number
    :param digit:               maximum digits of the binary form (unused digits from the MSB will be 0;
                                    must be sufficient for the binary form)
    :return:                    e.g. (5,5)=>[0,0,1,0,1]; (5,1)=>AssertionFailure
    """
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


def num_bin_2_dec(num: np.ndarray) -> int:
    num = num.astype(int)
    bin_str = "".join([str(i) for i in num])
    res = int(bin_str, 2)
    return res


def encoding_2_raw_bar(encoding: np.ndarray, elem_height: int, elem_width: int) -> np.ndarray:
    res = np.full((encoding.shape[0] * elem_height, encoding.shape[1] * elem_width), -99)

    for _h_idx in range(encoding.shape[0]):
        for _w_idx in range(encoding.shape[1]):
            res[_h_idx * elem_height:(_h_idx + 1) * elem_height, _w_idx * elem_width:(_w_idx + 1) * elem_width
            ] = encoding[_h_idx, _w_idx]

    return res


if "__main__" == __name__:
    print(num_bin_2_dec(np.array([0, 0, 0, 1, 0, 1, 0, 1])))
