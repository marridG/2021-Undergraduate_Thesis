from typing import Dict
import numpy as np


class MaxDistCal:
    SIZE_RECT = 1200  # mm
    SIZE_CIR = 1200  # mm
    SIZE_TRI = 1300  # mm

    RESOL_HORI = 0.10  # degrees
    RESOL_VERT = 0.33  # degrees

    def __init__(self, enc_bar_cnt_row: int, enc_bar_cnt_col: int):
        self.ENC_BAR_CNT_ROW = enc_bar_cnt_row
        self.ENC_BAR_CNT_COL = enc_bar_cnt_col

    def _cal_rect_bar_hw(self, bar_hw_ratio: float) -> (float, float):
        x_by_width = self.SIZE_RECT * 1. / self.ENC_BAR_CNT_COL
        x_by_height = self.SIZE_RECT * 1. / (self.ENC_BAR_CNT_ROW * bar_hw_ratio)
        res = min(x_by_width, x_by_height)
        res_width = res
        res_height = res * bar_hw_ratio
        return res_height, res_width

    def _cal_cir_bar_hw(self, bar_hw_ratio: float) -> (float, float):
        res = self.SIZE_CIR / np.sqrt(self.ENC_BAR_CNT_COL * self.ENC_BAR_CNT_COL
                                      + self.ENC_BAR_CNT_ROW * self.ENC_BAR_CNT_ROW * bar_hw_ratio * bar_hw_ratio)
        res_width = res
        res_height = res * bar_hw_ratio
        return res_height, res_width

    def _cal_tri_bar_hw(self, bar_hw_ratio: float) -> (float, float):
        res = self.SIZE_TRI / (self.ENC_BAR_CNT_COL + 2. * self.ENC_BAR_CNT_ROW * bar_hw_ratio / np.sqrt(3))
        res_width = res
        res_height = res * bar_hw_ratio
        return res_height, res_width

    def _cal_bar_hw(self, bar_hw_ratio: float, shape: str) -> (float, float):
        assert shape in ["r", "rect", "rectangle",
                         "c", "cir", "circle",
                         "t", "tri", "triangle"], "Unknown Shape \"%s\"" % shape

        if shape.startswith("r"):  # rectangle
            res = self._cal_rect_bar_hw(bar_hw_ratio=bar_hw_ratio)
        elif shape.startswith("c"):  # circle
            res = self._cal_cir_bar_hw(bar_hw_ratio=bar_hw_ratio)
        elif shape.startswith("t"):  # triangle
            res = self._cal_tri_bar_hw(bar_hw_ratio=bar_hw_ratio)
        else:
            raise NotImplementedError

        return res

    def _cal_hori_dist_by_width(self, width: float) -> float:
        """unit-free => unit-free"""
        res = width / np.tan(self.RESOL_HORI / 180. * np.pi)
        return res

    def _cal_vert_dist_by_height(self, height: float) -> float:
        """unit-free => unit-free"""
        res = height / np.tan(self.RESOL_VERT / 180. * np.pi)
        return res

    def cal_dist(self, bar_hw_ratio: float,
                 lv1_pt_cnt_vert: int, lv1_pt_cnt_hori: int, lv2_pt_cnt_vert: int, lv2_pt_cnt_hori: int) \
            -> Dict[str, Dict[str, Dict[str, float]]]:
        """
        calculate the maximum distance where lv-1 or lv-2 info can be 100% extracted
        :param bar_hw_ratio:            ratio of the bar height to bar width
        :param lv1_pt_cnt_vert:             number of VERTICAL sample points required for lv-1 info
        :param lv1_pt_cnt_hori:             number of HORIZONTAL sample points required for lv-1 info
        :param lv2_pt_cnt_vert:             number of VERTICAL sample points required for lv-2 info
        :param lv2_pt_cnt_hori:             number of HORIZONTAL sample points required for lv-2 info
        :return:                        maximum distance (in METERs) calculation results, as a <dict>:
                                        {
                                            shape_name: {
                                                "lv1"/"lv2": {"dist"/"hori"/"vert": <float>}
                                            }
                                        }
        """

        assert lv1_pt_cnt_hori < self.ENC_BAR_CNT_COL and 0 == self.ENC_BAR_CNT_COL % lv1_pt_cnt_hori
        assert lv1_pt_cnt_vert < self.ENC_BAR_CNT_ROW and 0 == self.ENC_BAR_CNT_ROW % lv1_pt_cnt_vert
        assert lv2_pt_cnt_hori < self.ENC_BAR_CNT_COL and 0 == self.ENC_BAR_CNT_COL % lv2_pt_cnt_hori
        assert lv2_pt_cnt_vert < self.ENC_BAR_CNT_ROW and 0 == self.ENC_BAR_CNT_ROW % lv2_pt_cnt_vert

        lv1_max_width_by_bar_cnt = self.ENC_BAR_CNT_COL // lv1_pt_cnt_hori
        lv1_max_height_by_bar_cnt = self.ENC_BAR_CNT_ROW // lv1_pt_cnt_vert
        lv2_max_width_by_bar_cnt = self.ENC_BAR_CNT_COL // lv2_pt_cnt_hori
        lv2_max_height_by_bar_cnt = self.ENC_BAR_CNT_ROW // lv2_pt_cnt_vert

        res = {}
        for shape in ["rectangle", "circle", "triangle"]:
            bar_height, bar_width = self._cal_bar_hw(bar_hw_ratio=bar_hw_ratio, shape=shape)
            # level 1 info
            dist_lv1_hori = self._cal_hori_dist_by_width(width=bar_width * lv1_max_width_by_bar_cnt) / 1000.  # m
            dist_lv1_vert = self._cal_vert_dist_by_height(height=bar_height * lv1_max_height_by_bar_cnt) / 1000.  # m
            dist_lv1 = min(dist_lv1_hori, dist_lv1_vert)
            res[shape] = {"lv1": {"dist": dist_lv1, "hori": dist_lv1_hori, "vert": dist_lv1_vert}}
            # lv2 info
            dist_lv2_hori = self._cal_hori_dist_by_width(width=bar_width * lv2_max_width_by_bar_cnt) / 2000.  # m
            dist_lv2_vert = self._cal_vert_dist_by_height(height=bar_height * lv2_max_height_by_bar_cnt) / 2000.  # m
            dist_lv2 = min(dist_lv2_hori, dist_lv2_vert)
            res[shape] = {"lv2": {"dist": dist_lv2, "hori": dist_lv2_hori, "vert": dist_lv2_vert}}

        return res


if "__main__" == __name__:
    # 2*4, 2 per bar
    # 2*2, 2 per bar

    # 2*5, 1 per bar
    obj = MaxDistCal(enc_bar_cnt_col=10, enc_bar_cnt_row=2)
    res = obj.cal_dist(bar_hw_ratio=3.3, lv1_pt_cnt_vert=2, lv1_pt_cnt_hori=5, lv2_pt_cnt_vert=2, lv2_pt_cnt_hori=10)
    for shape, shape_res in res.items():
        print("RECT [LV 2] = %f (hori=%f, vert=%f)" % (dist_lv2, dist_lv2_hori, dist_lv2_vert))  # todo
