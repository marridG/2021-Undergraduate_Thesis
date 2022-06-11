import numpy as np

SIZE_RECT = 1200  # mm
SIZE_CIR = 1200  # mm
SIZE_TRI = 1300  # mm


def rect_wh_by_cnt_ratio(cnt_col, cnt_row=2, ratio=3.3):
    x_by_width = SIZE_RECT * 1. / cnt_col
    x_by_height = SIZE_RECT * 1. / (cnt_row * ratio)
    res = min(x_by_width, x_by_height)
    res_width = res
    res_height = res * ratio
    return res_width, res_height


def cir_wh_by_cnt_ratio(cnt_col, cnt_row=2, ratio=3.3):
    res = SIZE_CIR / np.sqrt(cnt_col * cnt_col + cnt_row * cnt_row * ratio * ratio)
    res_width = res
    res_height = res * ratio
    return res_width, res_height


def tri_wh_by_cnt_ratio(cnt_col, cnt_row=2, ratio=3.3):
    res = SIZE_TRI / (cnt_col + 2. * cnt_row * ratio / np.sqrt(3))
    res_width = res
    res_height = res * ratio
    return res_width, res_height


def hori_dist_by_width(width):
    res = width / np.tan(0.1 / 180. * np.pi)
    return res


def vert_dist_by_height(height):
    res = height / np.tan(0.33 / 180. * np.pi)
    return res


def distance(cnt_col, cnt_row, lv1_cnt_col, lv2_cnt_col):
    # rectangle
    width, height = rect_wh_by_cnt_ratio(cnt_col=cnt_col, cnt_row=cnt_row)  # mm
    # lv1
    dist_lv1_hori = hori_dist_by_width(width=width * lv1_cnt_col) / 1000.  # m
    dist_lv1_vert = vert_dist_by_height(height=height) / 1000.  # m
    dist_lv1 = min(dist_lv1_hori, dist_lv1_vert)
    print("RECT [LV 1] = %f (hori=%f, vert=%f)" % (dist_lv1, dist_lv1_hori, dist_lv1_vert))
    # lv2
    dist_lv2_hori = hori_dist_by_width(width=width * lv2_cnt_col) / 1000.  # m
    dist_lv2_vert = vert_dist_by_height(height=height) / 1000.  # m
    dist_lv2 = min(dist_lv2_hori, dist_lv2_vert)
    print("RECT [LV 2] = %f (hori=%f, vert=%f)" % (dist_lv2, dist_lv2_hori, dist_lv2_vert))

    # circle
    width, height = cir_wh_by_cnt_ratio(cnt_col=cnt_col, cnt_row=cnt_row)  # mm
    # lv1
    dist_lv1_hori = hori_dist_by_width(width=width * lv1_cnt_col) / 1000.  # m
    dist_lv1_vert = vert_dist_by_height(height=height) / 1000.  # m
    dist_lv1 = min(dist_lv1_hori, dist_lv1_vert)
    print("CIR [LV 1] = %f (hori=%f, vert=%f)" % (dist_lv1, dist_lv1_hori, dist_lv1_vert))
    # lv2
    dist_lv2_hori = hori_dist_by_width(width=width * lv2_cnt_col) / 1000.  # m
    dist_lv2_vert = vert_dist_by_height(height=height) / 1000.  # m
    dist_lv2 = min(dist_lv2_hori, dist_lv2_vert)
    print("CIR [LV 2] = %f (hori=%f, vert=%f)" % (dist_lv2, dist_lv2_hori, dist_lv2_vert))

    # triangle
    width, height = tri_wh_by_cnt_ratio(cnt_col=cnt_col, cnt_row=cnt_row)  # mm
    # lv1
    dist_lv1_hori = hori_dist_by_width(width=width * lv1_cnt_col) / 1000.  # m
    dist_lv1_vert = vert_dist_by_height(height=height) / 1000.  # m
    dist_lv1 = min(dist_lv1_hori, dist_lv1_vert)
    print("TRI [LV 1] = %f (hori=%f, vert=%f)" % (dist_lv1, dist_lv1_hori, dist_lv1_vert))
    # lv2
    dist_lv2_hori = hori_dist_by_width(width=width * lv2_cnt_col) / 1000.  # m
    dist_lv2_vert = vert_dist_by_height(height=height) / 1000.  # m
    dist_lv2 = min(dist_lv2_hori, dist_lv2_vert)
    print("TRI [LV 2] = %f (hori=%f, vert=%f)" % (dist_lv2, dist_lv2_hori, dist_lv2_vert))


settings = [(2, 8, 1, 0.5), (2, 10, 2, 1), (2, 8, 2, 0.5)]
for _cnt_row, _cnt_col, _lv1_cnt_col, _lv2_cnt_col in settings:
    distance(cnt_col=_cnt_col, cnt_row=_cnt_row, lv1_cnt_col=_lv1_cnt_col, lv2_cnt_col=_lv2_cnt_col)
    print()
