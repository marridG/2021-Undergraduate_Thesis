import numpy as np


# === for math calculations ===

def degree_2_radian(deg: float) -> float:
    return (deg / 180.) * np.pi


def radian_2_degree(rad: float) -> float:
    return (rad / np.pi) * 180.


def dist_2_margin(dist: int, angle_resol: float) -> int:
    """
    calculate the HORIZONTAL margin of two adjacent LiDAR points at the given distance
    :param dist:                given distance from the point to the LiDAR (not projection) (in METER's)
    :param angle_resol:         given angle resolution of the LiDAR (in DEGREE's)
    :return:                    horizontal margin as a CEIL-ed int (in MILLI-METERS)
    """
    resol = degree_2_radian(deg=angle_resol)  # in radians
    res = dist * np.tan(resol)  # in meters
    res *= 100. * 10.  # in milli-meters
    res = np.ceil(res).astype(int)
    return res


# === for encoding-related operations ===

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
            _loc_h_start, _loc_h_end = _h_idx * elem_height, (_h_idx + 1) * elem_height
            _loc_w_start, _loc_w_end = _w_idx * elem_width, (_w_idx + 1) * elem_width
            res[_loc_h_start:_loc_h_end, _loc_w_start:_loc_w_end] = encoding[_h_idx, _w_idx]

    return res


# === for decoding-related operations ===

def decode_one_line(points: np.ndarray, points_loc: np.ndarray, width: int, use_cnt_delta: bool) \
        -> None or np.ndarray:
    """
    General decoder to "combine" DETECTED horizontal digits into the fixed length of encodings
    :param points:          samples of binary values (0/1)
    :param points_loc:      location of the samples of binary values (in milli-meters)
    :param width:           width of each digit in the horizontal sequence (in milli-meters)
    :param use_cnt_delta:   whether to use the delta info of the numbers of points in adjacent bars
    :return:                "combined" sequence of bars, given as type <int>
    """
    assert 1 == len(points.shape)
    assert len(points) > 0
    assert points.shape == points_loc.shape
    assert False == np.isnan(np.max(points))  # make sure no nan values

    # map points to bars, by their locations
    pt_bar_idx = points_loc / (1.0 * width)
    pt_bar_idx = np.floor(pt_bar_idx).astype(int)
    pt_bar_idx -= np.min(pt_bar_idx)
    pt_bar_cnt = np.max(pt_bar_idx) - np.min(pt_bar_idx) + 1
    assert 0 != pt_bar_cnt

    # merge values of the same bar
    _pt_bar_val_accum = np.zeros(pt_bar_cnt, dtype=int)  # accumulate values
    _pt_bar_pt_cnt = np.zeros(pt_bar_cnt, dtype=int)  # as counter
    for _val, _idx in zip(points, pt_bar_idx):
        _pt_bar_val_accum[_idx] += _val
        _pt_bar_pt_cnt[_idx] += 1

    # judge cnt delta if used
    if use_cnt_delta:
        _delta = _pt_bar_pt_cnt[1:] - _pt_bar_pt_cnt[:-1]  # delta = right - left]
        if 0 != _delta.size:
            if np.abs(np.max(_delta)) > 1 or np.abs(np.min(_delta)) > 1:
                return None

    res = _pt_bar_val_accum * 1.0 / _pt_bar_pt_cnt
    res = np.round(res).astype(int)

    return res


def map_one_column(points_loc: np.ndarray, height: int):
    """
    General mapper to "combine" DETECTED vertical digits into bars
    :param points_loc:      location of the samples of binary values (in milli-meters)
    :param height:          height of each digit in the vertical sequence (in milli-meters)
    :return:                "combined" indices of bars that each vertical line falls into
    """

    # map points to bars, by their locations
    pt_bar_idx = points_loc / (1.0 * height)
    pt_bar_idx = np.floor(pt_bar_idx).astype(int)

    return pt_bar_idx


if "__main__" == __name__:
    print(num_bin_2_dec(np.array([0, 0, 0, 1, 0, 1, 0, 1])))
