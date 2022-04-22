import numpy as np
import pandas as pd
from matplotlib import cm
from matplotlib import pyplot as plt

ALL_SHAPES = ["矩形", "三角形", "圆形"]
ALL_SETTING_BOOL = [True, False]
ALL_SETTING_BOOL_2_VAL_STR = {True: "是", False: "否"}
ALL_SETTING_BOOL_2_TITLE_STR = {True: "使用", False: "不使用"}
# "理想级间高度比" "理想位高宽比" "相邻位采样点数差信息" "行首起始零信息"

SIZE_TITLE_FONT, SIZE_SUB_TITLE_SUB_FONT = 13, 8
SIZE_AXIS_LABEL_FONT, SIZE_AXIS_TICK_FONT, SIZE_LEGEND_FONT = 9, 10, 8
SIZE_SCATTER, SIZE_LINE = 8, 1.5

PLOT_DO_DRAW_REDRAW_ALL = False
PLOT_DO_DRAW = {1: False, 2: False, 3: False, 4: True, 5: True,
                6: True, 7: True, 8: True, 9: True, 10: True,
                11: True, 12: True, 13: True, 14: True, 15: True,
                16: True, 17: True, 18: True, 19: True, 20: True}

ALL_X_TICK_LABELS = np.arange(10, 140 + 10, 10)
ALL_X_TICKS = np.arange(len(ALL_X_TICK_LABELS))
ALL_Y_TICKS = np.arange(0, 1.0 + 0.2, 0.2)
ALL_Y_TICK_LABELS = ["%d%%" % int(i * 100) for i in ALL_Y_TICKS]

PATH = "./plots/"
PLOT_GROUP_IDX = 0
RESULTS = pd.read_table("./raw_results.txt", sep="\t", encoding="utf8")
df = RESULTS[["形状", "双行", "比例", "距离", "数量差", "行首零",
              "正确率", "成功率", "正确完整率", "1正确率", "2正确率", "语义筛选", "合并筛选"]]

plt.rcParams["font.sans-serif"] = ["SimHei"]


def set_plt_info(tar_ax, _set_y_ticks=True):
    tar_ax.set_xlabel("距离 / m", fontdict={"size": SIZE_AXIS_LABEL_FONT})
    tar_ax.set_xticks(ALL_X_TICKS), tar_ax.set_xticklabels(ALL_X_TICK_LABELS, fontsize=SIZE_AXIS_TICK_FONT)
    tar_ax.set_ylabel("比率", fontdict={"size": SIZE_AXIS_LABEL_FONT})
    if _set_y_ticks:
        tar_ax.set_yticks(ALL_Y_TICKS), tar_ax.set_yticklabels(ALL_Y_TICK_LABELS, fontsize=SIZE_AXIS_TICK_FONT)
    tar_ax.set_xlim(ALL_X_TICKS[0], ALL_X_TICKS[-1])
    # tar_ax.set_ylim(ALL_Y_TICKS[0], ALL_Y_TICKS[-1])
    tar_ax.legend(prop={"size": SIZE_LEGEND_FONT})


def get_setting_str(scale=None, ratio=None, delta=None, zero=None, lines=None):
    acc_str = "正确率 =  正确数 / 总测试数"

    board = []
    if scale is not None:
        board.append(ALL_SETTING_BOOL_2_TITLE_STR[scale] + "理想级间高度比")
    if ratio is not None:
        board.append(ALL_SETTING_BOOL_2_TITLE_STR[ratio] + "理想位高宽比")
    board_setting_str = "+".join(board)

    decode = []
    if delta is not None:
        decode.append(ALL_SETTING_BOOL_2_TITLE_STR[delta] + "相邻位采样点数差信息")
    if zero is not None:
        decode.append(ALL_SETTING_BOOL_2_TITLE_STR[zero] + "行首起始零信息")
    decode_setting_str = "+".join(decode)

    res = acc_str + "\n" + board_setting_str + "; " + decode_setting_str
    if lines is not None:
        for _line in lines:
            res += ("\n" + _line)
    return res


def get_lim(lim: float, step: float = 0.1):
    num_steps = int(lim // step)
    res = num_steps * step if lim < 0 else (num_steps + 1) * step
    res = np.around(res, decimals=1)
    return res


def get_percentage_y_ticks(lim: (float, float), step: float = 0.1):
    res = ["%d%%" % round(i * 100)
           for i in np.arange(lim[0], lim[1] + step, step)]
    return res


# === #1 === 三种指示牌 不同距离下 正确率（一级/一级&二级） (all #### comb)
PLOT_GROUP_IDX += 1
do_draw_this_idx = PLOT_DO_DRAW_REDRAW_ALL is True or PLOT_DO_DRAW[PLOT_GROUP_IDX] is True
print("===== IDX=%d: %s =====" % (PLOT_GROUP_IDX, "DO DRAW" if do_draw_this_idx is True else "SKIPPED"))
if do_draw_this_idx:
    for bool_scale in ALL_SETTING_BOOL:
        for bool_ratio in ALL_SETTING_BOOL:
            for bool_delta in ALL_SETTING_BOOL:
                for bool_zero in ALL_SETTING_BOOL:
                    # plt.clf()
                    fig, ax = plt.subplots()
                    colors = cm.get_cmap("rainbow")(np.linspace(0, 1, len(ALL_SHAPES)))
                    for shape, c in zip(ALL_SHAPES, colors):
                        data = df.loc[(df["形状"] == shape)
                                      & (df["双行"] == ALL_SETTING_BOOL_2_VAL_STR[bool_scale])
                                      & (df["比例"] == ALL_SETTING_BOOL_2_VAL_STR[bool_ratio])
                                      & (df["数量差"] == ALL_SETTING_BOOL_2_VAL_STR[bool_delta])
                                      & (df["行首零"] == ALL_SETTING_BOOL_2_VAL_STR[bool_zero])]
                        data = data[["1正确率", "2正确率"]]
                        data = data.values  # <np.ndarray> of shape (cnt_group, 2)

                        labels = ["%s-大类信息正确率" % shape, "%s-全部信息正确率" % shape]
                        line_styles = ["-", "--"]
                        for _d, _l, _ls in zip(data.T, labels, line_styles):
                            ax.plot(_d, label=_l, linestyle=_ls, color=c, linewidth=SIZE_LINE)
                            ax.scatter(ALL_X_TICKS, _d, color=c, s=SIZE_SCATTER)
                            # print(_d)
                    set_plt_info(tar_ax=ax)
                    plt.title(get_setting_str(scale=bool_scale, ratio=bool_ratio, delta=bool_delta, zero=bool_zero),
                              fontsize=SIZE_SUB_TITLE_SUB_FONT)  # sub-title
                    fig.suptitle("指示牌不同距离下遍历法解码正确率", fontsize=SIZE_TITLE_FONT)  # title
                    # plt.show()
                    fn = PATH + "[%d] %d%d-%d%d_三种指示牌_正确率.png" % \
                         (PLOT_GROUP_IDX, int(bool_scale), int(bool_ratio), int(bool_delta), int(bool_zero))
                    plt.savefig(fn, dpi=200)
                    plt.close()
                    print("SAVED:", fn)

# === #2 === 三种指示牌 不同距离下 是否使用【行首零信息】正确率差值 (一级/一级&二级) (是-否) (all ###1 - ###0 comb)
PLOT_GROUP_IDX += 1
do_draw_this_idx = PLOT_DO_DRAW_REDRAW_ALL is True or PLOT_DO_DRAW[PLOT_GROUP_IDX] is True
print("===== IDX=%d: %s =====" % (PLOT_GROUP_IDX, "DO DRAW" if do_draw_this_idx is True else "SKIPPED"))
if do_draw_this_idx:
    y_tick_step = 0.1
    for bool_scale in ALL_SETTING_BOOL:
        for bool_ratio in ALL_SETTING_BOOL:
            for bool_delta in ALL_SETTING_BOOL:
                # plt.clf()
                fig, ax = plt.subplots()
                colors = cm.get_cmap("rainbow")(np.linspace(0, 1, len(ALL_SHAPES)))
                y_max, y_min = -99, 99
                for shape, c in zip(ALL_SHAPES, colors):
                    data_yes = df.loc[(df["形状"] == shape)
                                      & (df["双行"] == ALL_SETTING_BOOL_2_VAL_STR[bool_scale])
                                      & (df["比例"] == ALL_SETTING_BOOL_2_VAL_STR[bool_ratio])
                                      & (df["数量差"] == ALL_SETTING_BOOL_2_VAL_STR[bool_delta])
                                      & (df["行首零"] == ALL_SETTING_BOOL_2_VAL_STR[True])]
                    data_yes = data_yes[["1正确率", "2正确率"]]
                    data_yes = data_yes.values  # <np.ndarray> of shape (cnt_group, 2)

                    data_no = df.loc[(df["形状"] == shape)
                                     & (df["双行"] == ALL_SETTING_BOOL_2_VAL_STR[bool_scale])
                                     & (df["比例"] == ALL_SETTING_BOOL_2_VAL_STR[bool_ratio])
                                     & (df["数量差"] == ALL_SETTING_BOOL_2_VAL_STR[bool_delta])
                                     & (df["行首零"] == ALL_SETTING_BOOL_2_VAL_STR[False])]
                    data_no = data_no[["1正确率", "2正确率"]]
                    data_no = data_no.values  # <np.ndarray> of shape (cnt_group, 2)

                    data = data_yes - data_no
                    y_max = max(y_max, get_lim(np.max(data), y_tick_step))
                    y_min = min(y_min, get_lim(np.min(data), y_tick_step))

                    labels = ["%s-大类信息正确率提升值" % shape, "%s-全部信息正确率提升值" % shape]
                    line_styles = ["-", "--"]
                    for _d, _l, _ls in zip(data.T, labels, line_styles):
                        ax.plot(_d, label=_l, linestyle=_ls, color=c)
                        ax.scatter(ALL_X_TICKS, _d, color=c, s=8)
                        # print(_d)

                set_plt_info(tar_ax=ax)
                ax.set_ylabel("比率提升值", fontsize=SIZE_AXIS_LABEL_FONT)
                ax_ylim = (min(-0.2, y_min), max(0.5, y_max))
                ax.set_yticks(np.arange(ax_ylim[0], ax_ylim[1] + y_tick_step, y_tick_step))
                ax.set_yticklabels(get_percentage_y_ticks(ax_ylim, y_tick_step), fontsize=SIZE_AXIS_TICK_FONT)
                ax.set_ylim(ax_ylim[0], ax_ylim[1])

                plt.title(get_setting_str(scale=bool_scale, ratio=bool_ratio, delta=bool_delta, zero=None,
                                          lines=["提升值 = 使用该信息的正确率 - 不使用该信息的正确率"]),
                          fontsize=SIZE_SUB_TITLE_SUB_FONT)  # sub-title
                fig.suptitle("行首起始零信息对指示牌遍历法解码正确率的影响", fontsize=SIZE_TITLE_FONT)  # title
                fig.subplots_adjust(top=0.85)
                # plt.show()
                fn = PATH + "[%d] %d%d-%d#_三种指示牌_行首零_正确率差值.png" % \
                     (PLOT_GROUP_IDX, int(bool_scale), int(bool_ratio), int(bool_delta))
                plt.savefig(fn, dpi=200)
                plt.close()
                print("SAVED:", fn)

# === #3 === 三种指示牌 不同距离下 是否使用【采样点数量差值】 正确率差值 (一级/一级&二级) (是-否) (all ##1# - ##0# comb)
PLOT_GROUP_IDX += 1
do_draw_this_idx = PLOT_DO_DRAW_REDRAW_ALL is True or PLOT_DO_DRAW[PLOT_GROUP_IDX] is True
print("===== IDX=%d: %s =====" % (PLOT_GROUP_IDX, "DO DRAW" if do_draw_this_idx is True else "SKIPPED"))
if do_draw_this_idx:
    y_tick_step = 0.01
    for bool_scale in ALL_SETTING_BOOL:
        for bool_ratio in ALL_SETTING_BOOL:
            for bool_zero in ALL_SETTING_BOOL:
                # plt.clf()
                fig, ax = plt.subplots()
                colors = cm.get_cmap("rainbow")(np.linspace(0, 1, len(ALL_SHAPES)))
                y_max, y_min = -99, 99
                for shape, c in zip(ALL_SHAPES, colors):
                    data_yes = df.loc[(df["形状"] == shape)
                                      & (df["双行"] == ALL_SETTING_BOOL_2_VAL_STR[bool_scale])
                                      & (df["比例"] == ALL_SETTING_BOOL_2_VAL_STR[bool_ratio])
                                      & (df["数量差"] == ALL_SETTING_BOOL_2_VAL_STR[True])
                                      & (df["行首零"] == ALL_SETTING_BOOL_2_VAL_STR[bool_zero])]
                    data_yes = data_yes[["1正确率", "2正确率"]]
                    data_yes = data_yes.values  # <np.ndarray> of shape (cnt_group, 2)

                    data_no = df.loc[(df["形状"] == shape)
                                     & (df["双行"] == ALL_SETTING_BOOL_2_VAL_STR[bool_scale])
                                     & (df["比例"] == ALL_SETTING_BOOL_2_VAL_STR[bool_ratio])
                                     & (df["数量差"] == ALL_SETTING_BOOL_2_VAL_STR[False])
                                     & (df["行首零"] == ALL_SETTING_BOOL_2_VAL_STR[bool_zero])]
                    data_no = data_no[["1正确率", "2正确率"]]
                    data_no = data_no.values  # <np.ndarray> of shape (cnt_group, 2)

                    data = data_yes - data_no
                    y_max = max(y_max, get_lim(np.max(data), y_tick_step))
                    y_min = min(y_min, get_lim(np.min(data), y_tick_step))

                    labels = ["%s-大类信息正确率提升值" % shape, "%s-全部信息正确率提升值" % shape]
                    line_styles = ["-", "--"]
                    for _d, _l, _ls in zip(data.T, labels, line_styles):
                        ax.plot(_d, label=_l, linestyle=_ls, color=c)
                        ax.scatter(ALL_X_TICKS, _d, color=c, s=8)
                        # print(_d)

                set_plt_info(tar_ax=ax)
                ax.set_ylabel("比率提升值", fontsize=SIZE_AXIS_LABEL_FONT)
                ax_ylim = (min(-0.05, y_min), max(0.05, y_max))
                ax.set_yticks(np.arange(ax_ylim[0], ax_ylim[1] + 0.01, 0.01))
                ax.set_yticklabels(["%d%%" % round(i * 100) for i in np.arange(ax_ylim[0], ax_ylim[1] + 0.01, 0.01)],
                                   fontsize=SIZE_AXIS_TICK_FONT)
                ax.set_ylim(ax_ylim[0], ax_ylim[1])

                plt.title(get_setting_str(scale=bool_scale, ratio=bool_ratio, delta=None, zero=bool_zero,
                                          lines=["提升值 = 使用该信息的正确率 - 不使用该信息的正确率"]),
                          fontsize=SIZE_SUB_TITLE_SUB_FONT)  # sub-title
                fig.suptitle("相邻位采样点数差信息对指示牌遍历法解码正确率的影响", fontsize=SIZE_TITLE_FONT)  # title
                fig.subplots_adjust(top=0.85)
                # plt.show()
                fn = PATH + "[%d] %d%d-#%d_三种指示牌_数量差_正确率差值.png" % \
                     (PLOT_GROUP_IDX, int(bool_scale), int(bool_ratio), int(bool_zero))
                plt.savefig(fn, dpi=200)
                plt.close()
                print("SAVED:", fn)

# === #4 === 三种指示牌 不同距离下 是否使用【双倍高度】 正确率差值 (一级/一级&二级) (是-否) (all 1### - 0### comb)
PLOT_GROUP_IDX += 1
do_draw_this_idx = PLOT_DO_DRAW_REDRAW_ALL is True or PLOT_DO_DRAW[PLOT_GROUP_IDX] is True
print("===== IDX=%d: %s =====" % (PLOT_GROUP_IDX, "DO DRAW" if do_draw_this_idx is True else "SKIPPED"))
if do_draw_this_idx:
    y_tick_step = 0.1
    for bool_ratio in ALL_SETTING_BOOL:
        for bool_delta in ALL_SETTING_BOOL:
            for bool_zero in ALL_SETTING_BOOL:
                # plt.clf()
                fig, ax = plt.subplots()
                colors = cm.get_cmap("rainbow")(np.linspace(0, 1, len(ALL_SHAPES)))
                y_max, y_min = -99, 99
                for shape, c in zip(ALL_SHAPES, colors):
                    data_yes = df.loc[(df["形状"] == shape)
                                      & (df["双行"] == ALL_SETTING_BOOL_2_VAL_STR[True])
                                      & (df["比例"] == ALL_SETTING_BOOL_2_VAL_STR[bool_ratio])
                                      & (df["数量差"] == ALL_SETTING_BOOL_2_VAL_STR[bool_delta])
                                      & (df["行首零"] == ALL_SETTING_BOOL_2_VAL_STR[bool_zero])]
                    data_yes = data_yes[["1正确率", "2正确率"]]
                    data_yes = data_yes.values  # <np.ndarray> of shape (cnt_group, 2)

                    data_no = df.loc[(df["形状"] == shape)
                                     & (df["双行"] == ALL_SETTING_BOOL_2_VAL_STR[False])
                                     & (df["比例"] == ALL_SETTING_BOOL_2_VAL_STR[bool_ratio])
                                     & (df["数量差"] == ALL_SETTING_BOOL_2_VAL_STR[bool_delta])
                                     & (df["行首零"] == ALL_SETTING_BOOL_2_VAL_STR[bool_zero])]
                    data_no = data_no[["1正确率", "2正确率"]]
                    data_no = data_no.values  # <np.ndarray> of shape (cnt_group, 2)

                    data = data_yes - data_no
                    y_max = max(y_max, get_lim(np.max(data), y_tick_step))
                    y_min = min(y_min, get_lim(np.min(data), y_tick_step))

                    labels = ["%s-大类信息正确率提升值" % shape, "%s-全部信息正确率提升值" % shape]
                    line_styles = ["-", "--"]
                    for _d, _l, _ls in zip(data.T, labels, line_styles):
                        ax.plot(_d, label=_l, linestyle=_ls, color=c)
                        ax.scatter(ALL_X_TICKS, _d, color=c, s=8)
                        # print(_d)

                set_plt_info(tar_ax=ax)
                ax.set_ylabel("比率提升值", fontsize=SIZE_AXIS_LABEL_FONT)
                ax_ylim = (min(-0.3, y_min), max(0.6, y_max))
                ax.set_yticks(np.arange(ax_ylim[0], ax_ylim[1] + y_tick_step, y_tick_step))
                ax.set_yticklabels(
                    ["%d%%" % round(i * 100) for i in np.arange(ax_ylim[0], ax_ylim[1] + y_tick_step, y_tick_step)],
                    fontsize=SIZE_AXIS_TICK_FONT)
                ax.set_ylim(ax_ylim[0], ax_ylim[1])

                plt.title(get_setting_str(scale=None, ratio=bool_ratio, delta=bool_delta, zero=bool_zero,
                                          lines=["提升值 = 使用该高度比的正确率 - 不使用该高度比的正确率"]),
                          fontsize=SIZE_SUB_TITLE_SUB_FONT)  # sub-title
                fig.suptitle("理想级间高度比对指示牌遍历法解码正确率的影响", fontsize=SIZE_TITLE_FONT)  # title
                fig.subplots_adjust(top=0.85)
                # plt.show()
                fn = PATH + "[%d] #%d-%d%d_三种指示牌_高度比_正确率差值.png" % \
                     (PLOT_GROUP_IDX, int(bool_ratio), int(bool_delta), int(bool_zero))
                plt.savefig(fn, dpi=200)
                plt.close()
                print("SAVED:", fn)

print()
