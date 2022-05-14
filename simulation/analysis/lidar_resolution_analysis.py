import numpy as np
from matplotlib import pyplot as plt

import utils

margin = lambda i, resol: \
    np.abs(
        1 +
        np.tan(utils.degree_2_radian(deg=(i + 1) * resol)) *
        np.tan(utils.degree_2_radian(deg=i * resol))
    )


# # all possible lines
# resolutions = [0.1, 0.2, 0.4, 2]
# for _resol in resolutions:
#     x_values = range(np.ceil(-90 // _resol).astype(int) + 1,
#                      np.ceil(90 // _resol).astype(int) - 1)  # alert: what if cannot be fully divided
#     x_values = np.array(x_values)
#     y_values = margin(x_values, _resol)
#     plt.plot(x_values, y_values, label="resol=%.1f" % _resol)
#
# plt.xlabel("Indices of \"Lines\""), plt.ylabel("Resolution / °")
# plt.title("ABS() Part Values Versus Resolution and All Line Indices"), plt.legend()
# plt.show()
#
# # reasonable line groups: at most 400 points
# plt.clf()
# resolutions = [0.1, 0.2, 0.4, 2]
# for _resol in resolutions:
#     x_values = range(max(np.ceil(-90 // _resol).astype(int) + 1, -200),
#                      min(200, np.ceil(90 // _resol).astype(int) - 1))  # alert: what if cannot be fully divided
#     x_values = np.array(x_values)
#     y_values = 2 * np.tan(utils.degree_2_radian(deg=_resol)) * margin(x_values, _resol)
#     plt.plot(x_values, y_values, label="resol=%.1f" % _resol)
#
# plt.xlabel("Indices of \"Lines\""), plt.ylabel("Almost Full d Values")
# plt.title("Almost Full d Values Versus Resolution and <=400 Line Indices"), plt.legend()
# plt.show()
#
# # HORIZONTAL ONLY + reasonable line groups: at most 400 points
# plt.clf()
# resolutions = [0.1, 0.2, 0.4]
# for _resol in resolutions:
#     x_values = range(max(np.ceil(-90 // _resol).astype(int) + 1, -200),
#                      min(200, np.ceil(90 // _resol).astype(int) - 1))  # alert: what if cannot be fully divided
#     x_values = np.array(x_values)
#     y_values = 2 * np.tan(utils.degree_2_radian(deg=_resol)) * margin(x_values, _resol)
#     plt.plot(x_values, y_values, label="resol=%.1f" % _resol)
#
# plt.xlabel("Indices of \"Lines\""), plt.ylabel("Almost Full d Values")
# plt.title("Almost Full d Values Versus Resolution and <=400 Line Indices"), plt.legend()
# plt.show()
#
# # HORIZONTAL ONLY + reasonable line groups: at most 100 points
# plt.clf()
# resolutions = [0.1, 0.2, 0.4]
# for _resol in resolutions:
#     x_values = range(max(np.ceil(-90 // _resol).astype(int) + 1, -50),
#                      min(50, np.ceil(90 // _resol).astype(int) - 1))  # alert: what if cannot be fully divided
#     x_values = np.array(x_values)
#     y_values = 2 * np.tan(utils.degree_2_radian(deg=_resol)) * margin(x_values, _resol)
#     plt.plot(x_values, y_values, label="resol=%.1f" % _resol)
#
# plt.xlabel("Indices of \"Lines\""), plt.ylabel("Almost Full d Values")
# plt.title("Almost Full d Values Versus Resolution and <=100 Line Indices"), plt.legend()
# plt.show()
#
#
# # # for max/min values only (to be generalized)
# # resolutions = [0.1, 0.2, 0.4, 2]
# # for _resol in resolutions:
# #     x_values = range(max(np.ceil(-90 // _resol).astype(int) + 1, -50),
# #                      min(50, np.ceil(90 // _resol).astype(int) - 1))  # alert: what if cannot be fully divided
# #     x_values = np.array(x_values)
# #     y_values = 2 * np.tan(utils.degree_2_radian(deg=_resol)) * margin(x_values, _resol)
# #     # max
# #     max_y = np.max(y_values)
# #     max_y_pt = x_values[np.argmax(y_values)]
# #     # min
# #     min_y = np.min(y_values)
# #     min_y_pt = x_values[np.argmin(y_values)]
# #     print("Resolution = %.1f\n\ty_max = %.10f, y_max_pt = %d\n\ty_min = %.10f, y_min_pt = %d\n\tdelta_max = %.10f"
# #           % (_resol, max_y, max_y_pt, min_y, min_y_pt, max_y - min_y))


def cal_max_line_resol_diff(_size, _resol, _dist, scale: str = "mm"):
    """
    :param _size:               in centi-meters
    :param _resol:              in degrees
    :param _dist:               in meters
    :param scale:
    :return:
    """
    assert scale in ["m", "cm", "mm"]

    __num_pt_per_side = np.floor(
        utils.radian_2_degree(rad=np.arctan(_size / 2. / _dist / 100))
        / _resol
    )
    # print(_size, _resol, _dist, __num_pt_per_side)

    __x_values = np.arange(-__num_pt_per_side, __num_pt_per_side)
    if 0 == len(__x_values):  # not any possible points at all
        return None, 0, None, None
    __y_values = 2 * np.tan(utils.degree_2_radian(deg=_resol)) * margin(__x_values, _resol)

    __max_y = np.max(__y_values)
    __min_y = np.min(__y_values)
    __delta_max_y = __max_y - __min_y

    __res = _dist * __delta_max_y  # in meters
    __min_y_resol = _dist * np.tan(utils.degree_2_radian(deg=_resol))  # in meters
    if "m" == scale:  # in meters
        return __res, __num_pt_per_side, (__max_y, __min_y, __delta_max_y), __min_y_resol
    if "cm" == scale:  # in centi-meters
        return 100. * __res, __num_pt_per_side, (__max_y, __min_y, __delta_max_y), 100. * __min_y_resol
    if "mm" == scale:  # in milli-meters
        return 100. * 10. * __res, __num_pt_per_side, (__max_y, __min_y, __delta_max_y), 100. * 10. * __min_y_resol
    raise NotImplementedError


# sign_size_n_resol_vals = [(130., 0.1), (130., 0.2), (130., 0.4),
#                           (65. * np.sqrt(3), 0.33), (65. * np.sqrt(3), 2.)]  # in (centi-meters, degrees)
sign_size_n_resol_vals = [(120., 0.1), (120, 0.33)]  # in (centi-meters, degrees)
distance_vals = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150]  # in meters
print("d_j\t\\omega_0\td_0\t=>\tj(2j+1)\tdelta\tLine Resol Diff\tResol")
for _size, _resol in sign_size_n_resol_vals:
    for _dist in distance_vals:
        __val, __j, __y_vals, __line_resol = cal_max_line_resol_diff(
            _size=_size, _resol=_resol, _dist=_dist, scale="mm")
        if __val is None and __y_vals is None:
            print("%.2f\t%.2f\t%d\t=>\t%d (%d)\tN/A\tN/A\tN/A"
                  % (_size, _resol, _dist, __j, 2 * __j + 1))
        else:
            print("%.2f\t%.2f\t%d\t=>\t%d (%d)\t%.10f\t%.10f\t%.5f"
                  % (_size, _resol, _dist, __j, 2 * __j + 1, __y_vals[-1], __val, __line_resol))

# plt.clf()
# distance_vals = np.arange(0, 150 + 5, 5)  # in meters
# for _size, _resol in sign_size_n_resol_vals:
#     values = cal_max_line_resol_diff(_size=_size, _resol=_resol, _dist=distance_vals, scale="mm")
#     plt.plot(distance_vals, values, label="(size,resol)=(%.3f,%.1f)" % (_size, _resol))
# plt.xlabel("Distance $d_0$ / m"), plt.ylabel("Maximum Difference of Line Resolution")
# plt.title("Maximum Difference of Line Resolution at Different Distance and Angle Resolution"), plt.legend()
# plt.show()
