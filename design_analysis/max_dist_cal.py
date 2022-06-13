from typing import Dict
import numpy as np
from matplotlib import pyplot as plt


class MaxDistCal:
    SIZE_RECT = 1200  # mm
    SIZE_CIR = 1200  # mm
    SIZE_TRI = 1300  # mm

    RESOL_HORI = 0.10  # degrees
    RESOL_VERT = 0.33  # degrees

    ALL_SHAPE_STR = ["rectangle", "circle", "triangle"]

    def __init__(self, enc_bar_cnt_row: int = 2, enc_bar_cnt_col: int = 8, **kwargs):
        self.ENC_BAR_CNT_ROW = enc_bar_cnt_row
        self.ENC_BAR_CNT_COL = enc_bar_cnt_col

        if isinstance(kwargs.get("size_rect"), int) is True:
            self.SIZE_RECT = kwargs["size_rect"]
        if isinstance(kwargs.get("size_cir"), int) is True:
            self.SIZE_CIR = kwargs["size_cir"]
        if isinstance(kwargs.get("size_tri"), int) is True:
            self.SIZE_TRI = kwargs["size_tri"]

    def _cal_rect_bar_hw(self, bar_hw_ratio: float) -> (float, float):
        x_by_width = self.SIZE_RECT * 1. / self.ENC_BAR_CNT_COL
        x_by_height = self.SIZE_RECT * 1. / (self.ENC_BAR_CNT_ROW * bar_hw_ratio)
        res = min(x_by_width, x_by_height)
        res_width = res
        res_height = res * bar_hw_ratio
        return res_height, res_width  # unit-free-alike, unit depends on that of `self.SIZE_RECT`

    def _cal_cir_bar_hw(self, bar_hw_ratio: float) -> (float, float):
        res = self.SIZE_CIR / np.sqrt(self.ENC_BAR_CNT_COL * self.ENC_BAR_CNT_COL
                                      + self.ENC_BAR_CNT_ROW * self.ENC_BAR_CNT_ROW * bar_hw_ratio * bar_hw_ratio)
        res_width = res
        res_height = res * bar_hw_ratio
        return res_height, res_width  # unit-free-alike, unit depends on that of `self.SIZE_CIR`

    def _cal_tri_bar_hw(self, bar_hw_ratio: float) -> (float, float):
        res = self.SIZE_TRI / (self.ENC_BAR_CNT_COL + 2. * self.ENC_BAR_CNT_ROW * bar_hw_ratio / np.sqrt(3))
        res_width = res
        res_height = res * bar_hw_ratio
        return res_height, res_width  # unit-free-alike, unit depends on that of `self.SIZE_TRI`

    def cal_bar_hw(self, bar_hw_ratio: float, shape: str) -> (float, float):
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
        """unit-free-alike => unit-free-alike, unit depends on that of `width`"""
        res = width / np.tan(self.RESOL_HORI / 180. * np.pi)
        return res

    def _cal_vert_dist_by_height(self, height: float) -> float:
        """unit-free-alike => unit-free-alike, unit depends on that of `width`"""
        res = height / np.tan(self.RESOL_VERT / 180. * np.pi)
        return res

    def cal_dist(self, bar_hw_ratio: float,
                 lv1_pt_cnt_vert: int, lv1_pt_cnt_hori: int, lv2_pt_cnt_vert: int, lv2_pt_cnt_hori: int,
                 print_res: bool = False) \
            -> Dict[str, Dict[str, Dict[str, float]]]:
        """
        calculate the maximum distance where lv-1 or lv-2 info can be 100% extracted
        :param bar_hw_ratio:            ratio of the bar height to bar width
        :param lv1_pt_cnt_vert:             number of VERTICAL sample points required for lv-1 info
        :param lv1_pt_cnt_hori:             number of HORIZONTAL sample points required for lv-1 info
        :param lv2_pt_cnt_vert:             number of VERTICAL sample points required for lv-2 info
        :param lv2_pt_cnt_hori:             number of HORIZONTAL sample points required for lv-2 info
        :param print_res:                   whether to print the calculated result max distances
        :return:                        maximum distance (in METERs) calculation results, as a <dict>:
                                        {
                                            shape_name: {
                                                "lv1"/"lv2": {"dist"/"hori"/"vert": <float>}
                                            }
                                        }
        """

        # assert lv1_pt_cnt_hori <= self.ENC_BAR_CNT_COL and 0 == self.ENC_BAR_CNT_COL % lv1_pt_cnt_hori
        # assert lv1_pt_cnt_vert <= self.ENC_BAR_CNT_ROW and 0 == self.ENC_BAR_CNT_ROW % lv1_pt_cnt_vert
        # assert lv2_pt_cnt_hori <= self.ENC_BAR_CNT_COL and 0 == self.ENC_BAR_CNT_COL % lv2_pt_cnt_hori
        # assert lv2_pt_cnt_vert <= self.ENC_BAR_CNT_ROW and 0 == self.ENC_BAR_CNT_ROW % lv2_pt_cnt_vert

        lv1_max_width_by_bar_cnt = self.ENC_BAR_CNT_COL / lv1_pt_cnt_hori
        lv1_max_height_by_bar_cnt = self.ENC_BAR_CNT_ROW / lv1_pt_cnt_vert
        lv2_max_width_by_bar_cnt = self.ENC_BAR_CNT_COL / lv2_pt_cnt_hori
        lv2_max_height_by_bar_cnt = self.ENC_BAR_CNT_ROW / lv2_pt_cnt_vert

        res = {}
        for shape in ["rectangle", "circle", "triangle"]:
            res[shape] = {}
            bar_height, bar_width = self.cal_bar_hw(bar_hw_ratio=bar_hw_ratio, shape=shape)
            # level 1 info
            dist_lv1_hori = self._cal_hori_dist_by_width(width=bar_width * lv1_max_width_by_bar_cnt) / 1000.  # m
            dist_lv1_vert = self._cal_vert_dist_by_height(height=bar_height * lv1_max_height_by_bar_cnt) / 1000.  # m
            dist_lv1 = min(dist_lv1_hori, dist_lv1_vert)
            res[shape]["lv1"] = {"dist": dist_lv1, "hori": dist_lv1_hori, "vert": dist_lv1_vert}
            # lv2 info
            dist_lv2_hori = self._cal_hori_dist_by_width(width=bar_width * lv2_max_width_by_bar_cnt) / 1000.  # m
            dist_lv2_vert = self._cal_vert_dist_by_height(height=bar_height * lv2_max_height_by_bar_cnt) / 1000.  # m
            dist_lv2 = min(dist_lv2_hori, dist_lv2_vert)
            res[shape]["lv2"] = {"dist": dist_lv2, "hori": dist_lv2_hori, "vert": dist_lv2_vert}

        if print_res is True:
            for shape, shape_dist in res.items():
                for _lv, _lv_dist in shape_dist.items():
                    print("%s [%s] = %.3fm (hori=%.3fm, vert=%.3fm)"
                          % (shape[:3].upper(), _lv, _lv_dist["dist"], _lv_dist["hori"], _lv_dist["vert"]))
        return res

    def find_opt_hw_ratio(self,
                          lv1_pt_cnt_vert: int, lv1_pt_cnt_hori: int, lv2_pt_cnt_vert: int, lv2_pt_cnt_hori: int,
                          empirical_ratio: float = -1) -> None:
        """
        "find" (by showing plots) the optimal ratio of a bar's height:width, which maximizes the maximum distance
            where lv-1 or lv-2 info can be 100% extracted
        :param lv1_pt_cnt_vert:             number of VERTICAL sample points required for lv-1 info
        :param lv1_pt_cnt_hori:             number of HORIZONTAL sample points required for lv-1 info
        :param lv2_pt_cnt_vert:             number of VERTICAL sample points required for lv-2 info
        :param lv2_pt_cnt_hori:             number of HORIZONTAL sample points required for lv-2 info
        :param empirical_ratio:             empirical value of the optimal height:width ratio
        """
        _RATIO_STEP_SIZE = 0.05

        # calculate all max distance values for all ratios and all shapes
        all_ratio = np.arange(0 + _RATIO_STEP_SIZE, 10, _RATIO_STEP_SIZE)
        max_dist_res = {"rectangle": {"lv1": [], "lv2": []},
                        "circle": {"lv1": [], "lv2": []},
                        "triangle": {"lv1": [], "lv2": []}}
        for _ratio in all_ratio:
            _max_dist = self.cal_dist(bar_hw_ratio=_ratio,
                                      lv1_pt_cnt_vert=lv1_pt_cnt_vert, lv1_pt_cnt_hori=lv1_pt_cnt_hori,
                                      lv2_pt_cnt_vert=lv2_pt_cnt_vert, lv2_pt_cnt_hori=lv2_pt_cnt_hori)
            for __shape, __shape_dist in _max_dist.items():
                for ___lv, ___lv_dist in __shape_dist.items():
                    max_dist_res[__shape][___lv].append(___lv_dist["dist"])

        # plot max distance values
        fig, ax = plt.subplots(nrows=2, ncols=3, figsize=(10, 6))
        ax = ax.flatten()
        _subplot_idx = 0
        for _shape, _shape_dist in max_dist_res.items():
            for __lv, __lv_dist in _shape_dist.items():
                ax[_subplot_idx].plot(all_ratio, __lv_dist)
                # optimal ratio value
                __opt_ratio = all_ratio[np.argmax(__lv_dist)]
                __opt_ratio_max_dist = np.max(__lv_dist)
                ax[_subplot_idx].axvline(x=all_ratio[np.argmax(__lv_dist)], color="red", linestyle=":")
                ax[_subplot_idx].annotate(text="%.2f\n%.4fm" % (__opt_ratio, __opt_ratio_max_dist),
                                          xy=(__opt_ratio, 20), color="red")
                # empirical optimal ratio value
                ax[_subplot_idx].axvline(x=empirical_ratio, color="black", linestyle=":")
                __emp_ratio_max_dist = __lv_dist[int(empirical_ratio // _RATIO_STEP_SIZE)]
                ax[_subplot_idx].annotate(text="%.2f\n%.4fm" % (empirical_ratio, __emp_ratio_max_dist),
                                          xy=(empirical_ratio, 0), color="black")
                # set subplot title
                ax[_subplot_idx].set_title("%s - %s (%s)" % (
                    _shape, __lv, "opt==emp" if __opt_ratio_max_dist == __emp_ratio_max_dist else "opt!=emp"))
                _subplot_idx += 3
            _subplot_idx -= 5
        fig.suptitle("Lv1=%d*%d; Lv2=%d*%d" % (lv1_pt_cnt_vert, lv1_pt_cnt_hori, lv2_pt_cnt_vert, lv2_pt_cnt_hori))
        fig.supxlabel("Height:Width Ratio"), fig.supylabel("Maximum Distance / m")
        fig.subplots_adjust(left=0.1, bottom=0.1, right=0.98, top=0.89, wspace=0.15, hspace=0.25)
        plt.show()

        return


if "__main__" == __name__:
    """
    # for migration test
    # 2*4, 2 per bar
    obj = MaxDistCal(enc_bar_cnt_col=8, enc_bar_cnt_row=2)
    _ = obj.cal_dist(bar_hw_ratio=3.3,
                     lv1_pt_cnt_vert=2, lv1_pt_cnt_hori=8, lv2_pt_cnt_vert=2, lv2_pt_cnt_hori=16, print_res=True)
    print()
    # 2*5, 1 per bar
    obj = MaxDistCal(enc_bar_cnt_col=10, enc_bar_cnt_row=2)
    _ = obj.cal_dist(bar_hw_ratio=3.3,
                     lv1_pt_cnt_vert=2, lv1_pt_cnt_hori=5, lv2_pt_cnt_vert=2, lv2_pt_cnt_hori=10, print_res=True)
    print()
    # 2*2, 2 per bar
    obj = MaxDistCal(enc_bar_cnt_col=8, enc_bar_cnt_row=2)
    _ = obj.cal_dist(bar_hw_ratio=3.3,
                     lv1_pt_cnt_vert=2, lv1_pt_cnt_hori=4, lv2_pt_cnt_vert=2, lv2_pt_cnt_hori=16, print_res=True)
    print()
    """  # for migration test

    # # === find optimal ratio == =
    # # 2*2, 2 per bar => 6.6
    # obj = MaxDistCal(enc_bar_cnt_col=8, enc_bar_cnt_row=2)
    # obj.find_opt_hw_ratio(lv1_pt_cnt_vert=2, lv1_pt_cnt_hori=4, lv2_pt_cnt_vert=2, lv2_pt_cnt_hori=16,
    #                       empirical_ratio=6.6)
    # # 2*4, 2 per bar => ~3.3
    # obj = MaxDistCal(enc_bar_cnt_col=8, enc_bar_cnt_row=2)
    # obj.find_opt_hw_ratio(lv1_pt_cnt_vert=2, lv1_pt_cnt_hori=8, lv2_pt_cnt_vert=2, lv2_pt_cnt_hori=16,
    #                       empirical_ratio=3.3)
    # # 2*5, 1 per bar => 6.6
    # obj = MaxDistCal(enc_bar_cnt_col=10, enc_bar_cnt_row=2)
    # obj.find_opt_hw_ratio(lv1_pt_cnt_vert=2, lv1_pt_cnt_hori=5, lv2_pt_cnt_vert=2, lv2_pt_cnt_hori=10,
    #                       empirical_ratio=6.6)

    # # === calculate maximum distance for the optimal ratio ===
    # # 2*2, 2 per bar
    # obj = MaxDistCal(enc_bar_cnt_col=8, enc_bar_cnt_row=2)
    # _ = obj.cal_dist(bar_hw_ratio=6.6,
    #                  lv1_pt_cnt_vert=2, lv1_pt_cnt_hori=4, lv2_pt_cnt_vert=2, lv2_pt_cnt_hori=16, print_res=True)
    # print()
    # # 2*4, 2 per bar
    # obj = MaxDistCal(enc_bar_cnt_col=8, enc_bar_cnt_row=2)
    # _ = obj.cal_dist(bar_hw_ratio=3.3,
    #                  lv1_pt_cnt_vert=2, lv1_pt_cnt_hori=8, lv2_pt_cnt_vert=2, lv2_pt_cnt_hori=16, print_res=True)
    # print()
    # # 2*5, 1 per bar
    # obj = MaxDistCal(enc_bar_cnt_col=10, enc_bar_cnt_row=2)
    # _ = obj.cal_dist(bar_hw_ratio=6.6,
    #                  lv1_pt_cnt_vert=2, lv1_pt_cnt_hori=5, lv2_pt_cnt_vert=2, lv2_pt_cnt_hori=10, print_res=True)
    # print()

    # === calculate bar size ===
    # # 2*2, 2 per bar
    # obj = MaxDistCal(enc_bar_cnt_col=8, enc_bar_cnt_row=2, size_cir=550)  # size_cir=1150)
    # h, w = obj.cal_bar_hw(bar_hw_ratio=6.6, shape="cir")
    # print("%.4f\t%.4f\t%.4f\t%.4f" % (h / 10., w / 10., 2. * h / 10., 8. * w / 10.))
    # d = obj.cal_dist(bar_hw_ratio=6.6, lv1_pt_cnt_vert=2, lv1_pt_cnt_hori=4, lv2_pt_cnt_vert=2, lv2_pt_cnt_hori=16)
    # print("%.4f\t%.4f" % (d["circle"]["lv1"]["dist"], d["circle"]["lv2"]["dist"]))
    # # 2*2, 2 per bar
    # obj = MaxDistCal(enc_bar_cnt_col=8, enc_bar_cnt_row=2, size_tri=550)  # size_tri=1150)  # size_tri=1240)
    # h, w = obj.cal_bar_hw(bar_hw_ratio=6.6, shape="tri")
    # print("%.4f\t%.4f\t%.4f\t%.4f" % (h, w, 2. * h, 8. * w))
    # d = obj.cal_dist(bar_hw_ratio=6.6, lv1_pt_cnt_vert=2, lv1_pt_cnt_hori=4, lv2_pt_cnt_vert=2, lv2_pt_cnt_hori=16)
    # print("%.4f\t%.4f" % (d["triangle"]["lv1"]["dist"], d["triangle"]["lv2"]["dist"]))

    pass
