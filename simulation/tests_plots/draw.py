import numpy as np
import pandas as pd
from matplotlib import cm
from matplotlib import pyplot as plt

ALL_SHAPES = ["矩形", "三角形", "圆形"]
ALL_SETTING_BOOL = [True, False]
ALL_SETTING_BOOL_2_VAL_STR = {True: "是", False: "否"}
ALL_SETTING_BOOL_2_TITLE_STR = {True: "使用", False: "不使用"}
# "理想级间高度比" "理想位高宽比" "相邻位采样点数差信息" "行首起始零信息"

PLOT_DO_DRAW_REDRAW_ALL = False
PLOT_DO_DRAW = {1: False, 2: False, 3: False, 4: False, 5: False,
                6: False, 7: False, 8: False, 9: False, 10: False,
                11: False, 12: False, 13: False, 14: True, 15: False,
                16: False, 17: True, 18: True, 19: True, 20: True}

ALL_X_TICK_LABELS = np.arange(10, 140 + 10, 10)
ALL_X_TICKS = np.arange(len(ALL_X_TICK_LABELS))
ALL_Y_TICKS = np.arange(0, 1.0 + 0.2, 0.2)
ALL_Y_TICK_LABELS = ["%d%%" % int(i * 100) for i in ALL_Y_TICKS]

PATH = "./plots/"
PLOT_GROUP_IDX = 0
RESULTS_VER2 = pd.read_table("./raw_results.txt", sep="\t", encoding="utf8")
RESULTS_VER3 = pd.read_table("./raw_results_v3.txt", sep="\t", encoding="utf8")
df_v2 = RESULTS_VER2[["形状", "双行", "比例", "距离", "数量差", "行首零",
                      "正确率", "成功率", "正确完整率", "1正确率", "2正确率", "语义筛选", "合并筛选"]]
df_v3 = RESULTS_VER3[["形状", "双行", "比例", "距离",
                      "正确率", "成功率", "正确完整率", "1正确率", "2正确率", "语义筛选", "合并筛选"]]
df_v2 = df_v2.fillna(0)
df_v3 = df_v3.fillna(0)

SIZE_TITLE_FONT, SIZE_SUB_TITLE_SUB_FONT = 13, 8
SIZE_AXIS_LABEL_FONT, SIZE_AXIS_TICK_FONT, SIZE_LEGEND_FONT = 9, 10, 8
SIZE_SCATTER, SIZE_LINE = 8, 1.5
plt.rcParams["font.sans-serif"] = ["SimHei"]
# plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=SIZE_SUB_TITLE_SUB_FONT)  # fontsize of the axes title
plt.rc('axes', labelsize=SIZE_AXIS_LABEL_FONT)  # fontsize of the x and y labels
plt.rc('xtick', labelsize=SIZE_AXIS_TICK_FONT)  # fontsize of the tick labels
plt.rc('ytick', labelsize=SIZE_AXIS_TICK_FONT)  # fontsize of the tick labels
plt.rc('legend', fontsize=SIZE_LEGEND_FONT)  # legend fontsize
plt.rc('figure', titlesize=SIZE_TITLE_FONT)  # fontsize of the figure title


def set_plt_info(tar_ax, _set_y_ticks=True):
    tar_ax.set_xlabel("距离 / m", fontdict={"size": SIZE_AXIS_LABEL_FONT})
    tar_ax.set_xticks(ALL_X_TICKS), tar_ax.set_xticklabels(ALL_X_TICK_LABELS, fontsize=SIZE_AXIS_TICK_FONT)
    tar_ax.set_ylabel("比率", fontdict={"size": SIZE_AXIS_LABEL_FONT})
    if _set_y_ticks:
        tar_ax.set_yticks(ALL_Y_TICKS), tar_ax.set_yticklabels(ALL_Y_TICK_LABELS, fontsize=SIZE_AXIS_TICK_FONT)
    tar_ax.set_xlim(ALL_X_TICKS[0], ALL_X_TICKS[-1])
    tar_ax.set_ylim(ALL_Y_TICKS[0], ALL_Y_TICKS[-1])
    tar_ax.legend(prop={"size": SIZE_LEGEND_FONT})


def get_setting_str(scale=None, ratio=None, delta=None, zero=None, lines=None, pure=False):
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

    res = ""
    if "" != board_setting_str:
        res += board_setting_str
    if "" != decode_setting_str:
        if "" != res:
            res += "; "
        res += decode_setting_str

    if pure is True:
        return res

    if "" != res:
        res = acc_str + "\n" + res
    else:
        res = acc_str + res

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


# === #1 === 【ver2】三种指示牌 不同距离下 正确率（一级/一级&二级） (all #### comb)
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
                        data = df_v2.loc[(df_v2["形状"] == shape)
                                         & (df_v2["双行"] == ALL_SETTING_BOOL_2_VAL_STR[bool_scale])
                                         & (df_v2["比例"] == ALL_SETTING_BOOL_2_VAL_STR[bool_ratio])
                                         & (df_v2["数量差"] == ALL_SETTING_BOOL_2_VAL_STR[bool_delta])
                                         & (df_v2["行首零"] == ALL_SETTING_BOOL_2_VAL_STR[bool_zero])]
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
                    fig.subplots_adjust(left=0.093, bottom=0.083, right=0.983)
                    # plt.show()
                    fn = PATH + "[%d] %d%d-%d%d_三种指示牌_正确率.png" % \
                         (PLOT_GROUP_IDX, int(bool_scale), int(bool_ratio), int(bool_delta), int(bool_zero))
                    plt.savefig(fn, dpi=200)
                    plt.close()
                    print("SAVED:", fn)

# === #2 === 【ver2】三种指示牌 不同距离下 是否使用【行首零信息】正确率差值 (一级/一级&二级) (是-否) (all ###1 - ###0 comb)
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
                    data_yes = df_v2.loc[(df_v2["形状"] == shape)
                                         & (df_v2["双行"] == ALL_SETTING_BOOL_2_VAL_STR[bool_scale])
                                         & (df_v2["比例"] == ALL_SETTING_BOOL_2_VAL_STR[bool_ratio])
                                         & (df_v2["数量差"] == ALL_SETTING_BOOL_2_VAL_STR[bool_delta])
                                         & (df_v2["行首零"] == ALL_SETTING_BOOL_2_VAL_STR[True])]
                    data_yes = data_yes[["1正确率", "2正确率"]]
                    data_yes = data_yes.values  # <np.ndarray> of shape (cnt_group, 2)

                    data_no = df_v2.loc[(df_v2["形状"] == shape)
                                        & (df_v2["双行"] == ALL_SETTING_BOOL_2_VAL_STR[bool_scale])
                                        & (df_v2["比例"] == ALL_SETTING_BOOL_2_VAL_STR[bool_ratio])
                                        & (df_v2["数量差"] == ALL_SETTING_BOOL_2_VAL_STR[bool_delta])
                                        & (df_v2["行首零"] == ALL_SETTING_BOOL_2_VAL_STR[False])]
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
                fig.subplots_adjust(left=0.093, bottom=0.083, right=0.983)
                # plt.show()
                fn = PATH + "[%d] %d%d-%d#_三种指示牌_行首零_正确率差值.png" % \
                     (PLOT_GROUP_IDX, int(bool_scale), int(bool_ratio), int(bool_delta))
                plt.savefig(fn, dpi=200)
                plt.close()
                print("SAVED:", fn)

# === #3 === 【ver2】三种指示牌 不同距离下 是否使用【采样点数量差值】 正确率差值 (一级/一级&二级) (是-否) (all ##1# - ##0# comb)
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
                    data_yes = df_v2.loc[(df_v2["形状"] == shape)
                                         & (df_v2["双行"] == ALL_SETTING_BOOL_2_VAL_STR[bool_scale])
                                         & (df_v2["比例"] == ALL_SETTING_BOOL_2_VAL_STR[bool_ratio])
                                         & (df_v2["数量差"] == ALL_SETTING_BOOL_2_VAL_STR[True])
                                         & (df_v2["行首零"] == ALL_SETTING_BOOL_2_VAL_STR[bool_zero])]
                    data_yes = data_yes[["1正确率", "2正确率"]]
                    data_yes = data_yes.values  # <np.ndarray> of shape (cnt_group, 2)

                    data_no = df_v2.loc[(df_v2["形状"] == shape)
                                        & (df_v2["双行"] == ALL_SETTING_BOOL_2_VAL_STR[bool_scale])
                                        & (df_v2["比例"] == ALL_SETTING_BOOL_2_VAL_STR[bool_ratio])
                                        & (df_v2["数量差"] == ALL_SETTING_BOOL_2_VAL_STR[False])
                                        & (df_v2["行首零"] == ALL_SETTING_BOOL_2_VAL_STR[bool_zero])]
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
                fig.subplots_adjust(left=0.093, bottom=0.083, right=0.983)
                # plt.show()
                fn = PATH + "[%d] %d%d-#%d_三种指示牌_数量差_正确率差值.png" % \
                     (PLOT_GROUP_IDX, int(bool_scale), int(bool_ratio), int(bool_zero))
                plt.savefig(fn, dpi=200)
                plt.close()
                print("SAVED:", fn)

# === #4 === 【ver2】三种指示牌 不同距离下 是否使用【双倍高度】 正确率差值 (一级/一级&二级) (是-否) (all 1### - 0### comb)
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
                    data_yes = df_v2.loc[(df_v2["形状"] == shape)
                                         & (df_v2["双行"] == ALL_SETTING_BOOL_2_VAL_STR[True])
                                         & (df_v2["比例"] == ALL_SETTING_BOOL_2_VAL_STR[bool_ratio])
                                         & (df_v2["数量差"] == ALL_SETTING_BOOL_2_VAL_STR[bool_delta])
                                         & (df_v2["行首零"] == ALL_SETTING_BOOL_2_VAL_STR[bool_zero])]
                    data_yes = data_yes[["1正确率", "2正确率"]]
                    data_yes = data_yes.values  # <np.ndarray> of shape (cnt_group, 2)

                    data_no = df_v2.loc[(df_v2["形状"] == shape)
                                        & (df_v2["双行"] == ALL_SETTING_BOOL_2_VAL_STR[False])
                                        & (df_v2["比例"] == ALL_SETTING_BOOL_2_VAL_STR[bool_ratio])
                                        & (df_v2["数量差"] == ALL_SETTING_BOOL_2_VAL_STR[bool_delta])
                                        & (df_v2["行首零"] == ALL_SETTING_BOOL_2_VAL_STR[bool_zero])]
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
                fig.subplots_adjust(left=0.093, bottom=0.083, right=0.983)
                # plt.show()
                fn = PATH + "[%d] #%d-%d%d_三种指示牌_高度比_正确率差值.png" % \
                     (PLOT_GROUP_IDX, int(bool_ratio), int(bool_delta), int(bool_zero))
                plt.savefig(fn, dpi=200)
                plt.close()
                print("SAVED:", fn)

# === #5 === 【ver2】三种指示牌 不同距离下 是否使用【高宽比】 正确率差值 (一级/一级&二级) (是-否) (all 1### - 0### comb)
PLOT_GROUP_IDX += 1
do_draw_this_idx = PLOT_DO_DRAW_REDRAW_ALL is True or PLOT_DO_DRAW[PLOT_GROUP_IDX] is True
print("===== IDX=%d: %s =====" % (PLOT_GROUP_IDX, "DO DRAW" if do_draw_this_idx is True else "SKIPPED"))
if do_draw_this_idx:
    y_tick_step = 0.1
    for bool_scale in ALL_SETTING_BOOL:
        for bool_delta in ALL_SETTING_BOOL:
            for bool_zero in ALL_SETTING_BOOL:
                # plt.clf()
                fig, ax = plt.subplots()
                colors = cm.get_cmap("rainbow")(np.linspace(0, 1, len(ALL_SHAPES)))
                y_max, y_min = -99, 99
                for shape, c in zip(ALL_SHAPES, colors):
                    data_yes = df_v2.loc[(df_v2["形状"] == shape)
                                         & (df_v2["双行"] == ALL_SETTING_BOOL_2_VAL_STR[bool_scale])
                                         & (df_v2["比例"] == ALL_SETTING_BOOL_2_VAL_STR[True])
                                         & (df_v2["数量差"] == ALL_SETTING_BOOL_2_VAL_STR[bool_delta])
                                         & (df_v2["行首零"] == ALL_SETTING_BOOL_2_VAL_STR[bool_zero])]
                    data_yes = data_yes[["1正确率", "2正确率"]]
                    data_yes = data_yes.values  # <np.ndarray> of shape (cnt_group, 2)

                    data_no = df_v2.loc[(df_v2["形状"] == shape)
                                        & (df_v2["双行"] == ALL_SETTING_BOOL_2_VAL_STR[bool_scale])
                                        & (df_v2["比例"] == ALL_SETTING_BOOL_2_VAL_STR[False])
                                        & (df_v2["数量差"] == ALL_SETTING_BOOL_2_VAL_STR[bool_delta])
                                        & (df_v2["行首零"] == ALL_SETTING_BOOL_2_VAL_STR[bool_zero])]
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

                plt.title(get_setting_str(scale=bool_scale, ratio=None, delta=bool_delta, zero=bool_zero,
                                          lines=["提升值 = 使用该高宽比的正确率 - 不使用该高宽比的正确率"]),
                          fontsize=SIZE_SUB_TITLE_SUB_FONT)  # sub-title
                fig.suptitle("理想位高宽比对指示牌遍历法解码正确率的影响", fontsize=SIZE_TITLE_FONT)  # title
                fig.subplots_adjust(top=0.85)
                fig.subplots_adjust(left=0.093, bottom=0.083, right=0.983)
                # plt.show()
                fn = PATH + "[%d] %d#-%d%d_三种指示牌_高宽比_正确率差值.png" % \
                     (PLOT_GROUP_IDX, int(bool_scale), int(bool_delta), int(bool_zero))
                plt.savefig(fn, dpi=200)
                plt.close()
                print("SAVED:", fn)

# === #6 === 【ver3】三种指示牌 不同距离下 正确率（一级/一级&二级） (all #### comb)
PLOT_GROUP_IDX += 1
do_draw_this_idx = PLOT_DO_DRAW_REDRAW_ALL is True or PLOT_DO_DRAW[PLOT_GROUP_IDX] is True
print("===== IDX=%d: %s =====" % (PLOT_GROUP_IDX, "DO DRAW" if do_draw_this_idx is True else "SKIPPED"))
if do_draw_this_idx:
    for bool_scale in ALL_SETTING_BOOL:
        for bool_ratio in ALL_SETTING_BOOL:
            # plt.clf()
            fig, ax = plt.subplots()
            colors = cm.get_cmap("rainbow")(np.linspace(0, 1, len(ALL_SHAPES)))
            for shape, c in zip(ALL_SHAPES, colors):
                data = df_v3.loc[(df_v3["形状"] == shape)
                                 & (df_v3["双行"] == ALL_SETTING_BOOL_2_VAL_STR[bool_scale])
                                 & (df_v3["比例"] == ALL_SETTING_BOOL_2_VAL_STR[bool_ratio])]
                data = data[["1正确率", "2正确率"]]
                data = data.values  # <np.ndarray> of shape (cnt_group, 2)

                labels = ["%s-大类信息正确率" % shape, "%s-全部信息正确率" % shape]
                line_styles = ["-", "--"]
                for _d, _l, _ls in zip(data.T, labels, line_styles):
                    ax.plot(_d, label=_l, linestyle=_ls, color=c, linewidth=SIZE_LINE)
                    ax.scatter(ALL_X_TICKS, _d, color=c, s=SIZE_SCATTER)
                    # print(_d)
            set_plt_info(tar_ax=ax)
            plt.title(get_setting_str(scale=bool_scale, ratio=bool_ratio, delta=None, zero=None),
                      fontsize=SIZE_SUB_TITLE_SUB_FONT)  # sub-title
            fig.suptitle("指示牌不同距离下回溯法解码正确率", fontsize=SIZE_TITLE_FONT)  # title
            fig.subplots_adjust(left=0.093, bottom=0.083, right=0.983)
            # plt.show()
            fn = PATH + "[%d] %d%d-#_三种指示牌_正确率.png" % (PLOT_GROUP_IDX, int(bool_scale), int(bool_ratio))
            plt.savefig(fn, dpi=200)
            plt.close()
            print("SAVED:", fn)

# === #7 === 【ver3】三种指示牌 不同距离下 是否使用【双倍高度】 正确率差值 (一级/一级&二级) (是-否) (all 1## - 0## comb)
PLOT_GROUP_IDX += 1
do_draw_this_idx = PLOT_DO_DRAW_REDRAW_ALL is True or PLOT_DO_DRAW[PLOT_GROUP_IDX] is True
print("===== IDX=%d: %s =====" % (PLOT_GROUP_IDX, "DO DRAW" if do_draw_this_idx is True else "SKIPPED"))
if do_draw_this_idx:
    y_tick_step = 0.1
    for bool_ratio in ALL_SETTING_BOOL:
        # plt.clf()
        fig, ax = plt.subplots()
        colors = cm.get_cmap("rainbow")(np.linspace(0, 1, len(ALL_SHAPES)))
        y_max, y_min = -99, 99
        for shape, c in zip(ALL_SHAPES, colors):
            data_yes = df_v3.loc[(df_v3["形状"] == shape)
                                 & (df_v3["双行"] == ALL_SETTING_BOOL_2_VAL_STR[True])
                                 & (df_v3["比例"] == ALL_SETTING_BOOL_2_VAL_STR[bool_ratio])]
            data_yes = data_yes[["1正确率", "2正确率"]]
            data_yes = data_yes.values  # <np.ndarray> of shape (cnt_group, 2)

            data_no = df_v3.loc[(df_v3["形状"] == shape)
                                & (df_v3["双行"] == ALL_SETTING_BOOL_2_VAL_STR[False])
                                & (df_v3["比例"] == ALL_SETTING_BOOL_2_VAL_STR[bool_ratio])]
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

        plt.title(get_setting_str(scale=None, ratio=bool_ratio, delta=None, zero=None,
                                  lines=["提升值 = 使用该高度比的正确率 - 不使用该高度比的正确率"]),
                  fontsize=SIZE_SUB_TITLE_SUB_FONT)  # sub-title
        fig.suptitle("理想级间高度比对指示牌回溯法解码正确率的影响", fontsize=SIZE_TITLE_FONT)  # title
        fig.subplots_adjust(top=0.85)
        fig.subplots_adjust(left=0.093, bottom=0.083, right=0.983)
        # plt.show()
        fn = PATH + "[%d] #%d-#_三种指示牌_高度比_正确率差值.png" % (PLOT_GROUP_IDX, int(bool_ratio))
        plt.savefig(fn, dpi=200)
        plt.close()
        print("SAVED:", fn)

# === #8 === 【ver3】三种指示牌 不同距离下 是否使用【高宽比】 正确率差值 (一级/一级&二级) (是-否) (all 1## - 0## comb)
PLOT_GROUP_IDX += 1
do_draw_this_idx = PLOT_DO_DRAW_REDRAW_ALL is True or PLOT_DO_DRAW[PLOT_GROUP_IDX] is True
print("===== IDX=%d: %s =====" % (PLOT_GROUP_IDX, "DO DRAW" if do_draw_this_idx is True else "SKIPPED"))
if do_draw_this_idx:
    y_tick_step = 0.1
    for bool_scale in ALL_SETTING_BOOL:
        # plt.clf()
        fig, ax = plt.subplots()
        colors = cm.get_cmap("rainbow")(np.linspace(0, 1, len(ALL_SHAPES)))
        y_max, y_min = -99, 99
        for shape, c in zip(ALL_SHAPES, colors):
            data_yes = df_v3.loc[(df_v3["形状"] == shape)
                                 & (df_v3["双行"] == ALL_SETTING_BOOL_2_VAL_STR[bool_scale])
                                 & (df_v3["比例"] == ALL_SETTING_BOOL_2_VAL_STR[True])]
            data_yes = data_yes[["1正确率", "2正确率"]]
            data_yes = data_yes.values  # <np.ndarray> of shape (cnt_group, 2)

            data_no = df_v3.loc[(df_v3["形状"] == shape)
                                & (df_v3["双行"] == ALL_SETTING_BOOL_2_VAL_STR[bool_scale])
                                & (df_v3["比例"] == ALL_SETTING_BOOL_2_VAL_STR[False])]
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

        plt.title(get_setting_str(scale=bool_scale, ratio=None, delta=None, zero=None,
                                  lines=["提升值 = 使用该高宽比的正确率 - 不使用该高宽比的正确率"]),
                  fontsize=SIZE_SUB_TITLE_SUB_FONT)  # sub-title
        fig.suptitle("理想位高宽比对指示牌回溯法解码正确率的影响", fontsize=SIZE_TITLE_FONT)  # title
        fig.subplots_adjust(top=0.85)
        fig.subplots_adjust(left=0.093, bottom=0.083, right=0.983)
        # plt.show()
        fn = PATH + "[%d] %d#-#_三种指示牌_高宽比_正确率差值.png" % (PLOT_GROUP_IDX, int(bool_scale))
        plt.savefig(fn, dpi=200)
        plt.close()
        print("SAVED:", fn)

# === #9 === 【ver2】每种指示牌 不同距离下 正确率（一级/一级&二级）+筛选率 (all #### comb)
PLOT_GROUP_IDX += 1
do_draw_this_idx = PLOT_DO_DRAW_REDRAW_ALL is True or PLOT_DO_DRAW[PLOT_GROUP_IDX] is True
print("===== IDX=%d: %s =====" % (PLOT_GROUP_IDX, "DO DRAW" if do_draw_this_idx is True else "SKIPPED"))
if do_draw_this_idx:
    colors = cm.get_cmap("rainbow")(np.linspace(0, 1, 3))
    # ax_tree_color, ax_tol_color = "grey", "green"
    ax_tree_color, ax_tol_color, c = colors
    for bool_scale in ALL_SETTING_BOOL:
        for bool_ratio in ALL_SETTING_BOOL:
            for bool_delta in ALL_SETTING_BOOL:
                for bool_zero in ALL_SETTING_BOOL:
                    for shape in ALL_SHAPES:
                        # plt.clf()
                        fig, ax = plt.subplots()
                        ax_tree = ax.twinx()
                        ax_tol = ax.twinx()
                        # acc lines and points
                        data_all = df_v2.loc[(df_v2["形状"] == shape)
                                             & (df_v2["双行"] == ALL_SETTING_BOOL_2_VAL_STR[bool_scale])
                                             & (df_v2["比例"] == ALL_SETTING_BOOL_2_VAL_STR[bool_ratio])
                                             & (df_v2["数量差"] == ALL_SETTING_BOOL_2_VAL_STR[bool_delta])
                                             & (df_v2["行首零"] == ALL_SETTING_BOOL_2_VAL_STR[bool_zero])]
                        data = data_all[["1正确率", "2正确率"]]
                        data = data.values  # <np.ndarray> of shape (cnt_group, 2)

                        labels = ["大类信息正确率", "全部信息正确率"]
                        line_styles = ["-", "--"]
                        for _d, _l, _ls in zip(data.T, labels, line_styles):
                            ax.plot(_d, label=_l, linestyle=_ls, color=c, linewidth=SIZE_LINE)
                            ax.scatter(ALL_X_TICKS, _d, color=c, s=SIZE_SCATTER)
                            # print(_d)
                        ax.set_xlabel("距离 / m")
                        ax.set_xticks(ALL_X_TICKS), ax.set_xticklabels(ALL_X_TICK_LABELS)
                        ax.set_ylabel("比率")
                        ax.set_yticks(ALL_Y_TICKS), ax.set_yticklabels(ALL_Y_TICK_LABELS)
                        ax.set_xlim(ALL_X_TICKS[0], ALL_X_TICKS[-1])
                        ax.set_ylim(ALL_Y_TICKS[0], ALL_Y_TICKS[-1])

                        # filter ratio bars
                        # tree
                        data = data_all["语义筛选"]
                        data = data.values  # <np.ndarray> of shape (1, 2)
                        ax_tree.bar(ALL_X_TICKS, height=data, width=ALL_X_TICKS[-1] - ALL_X_TICKS[-2],
                                    label="语义剪枝模块筛选率", bottom=0, color=ax_tree_color, alpha=0.2)
                        ax_tree.set_ylabel("语义剪枝筛选率", loc="bottom", color=ax_tree_color)
                        ax_tree_step = 0.1
                        ax_tree_lim = (0, get_lim(np.max(data), step=ax_tree_step))
                        ax_tree.set_yticks(np.arange(ax_tree_lim[0], ax_tree_lim[1] + ax_tree_step, ax_tree_step))
                        ax_tree.set_yticklabels(get_percentage_y_ticks(lim=ax_tree_lim, step=ax_tree_step),
                                                color=ax_tree_color)
                        ax_tree.set_ylim(ax_tree_lim[0], ax_tree_lim[1] * 2 + ax_tree_step * 2)
                        # combine
                        data = data_all["合并筛选"]
                        data = data.values  # <np.ndarray> of shape (1, 2)
                        ax_tol.bar(ALL_X_TICKS, height=-1 * data, width=ALL_X_TICKS[-1] - ALL_X_TICKS[-2],
                                   label="可能合并模块合并率", bottom=0, color=ax_tol_color, alpha=0.2)
                        ax_tol.set_ylabel("合并率", loc="top", color=ax_tol_color)
                        ax_tol_step = 0.1
                        ax_tol_lim = (-1 * get_lim(np.max(data), step=ax_tol_step), 0)
                        ax_tol.set_yticks(np.arange(ax_tol_lim[0], ax_tol_lim[1] + ax_tol_step, ax_tol_step))
                        ax_tol.set_yticklabels([i[1:] if "-" == i[0] else i
                                                for i in get_percentage_y_ticks(lim=ax_tol_lim, step=ax_tol_step)],
                                               color=ax_tol_color)
                        ax_tol.set_ylim(ax_tol_lim[0] * 2 - ax_tol_step * 2, ax_tol_lim[1])

                        plt.title(get_setting_str(scale=bool_scale, ratio=bool_ratio, delta=bool_delta, zero=bool_zero,
                                                  lines=["模块筛选率(合并率) = 1 - 进入模块数/离开模块数, 除数为零结果按 0 计"]),
                                  fontsize=SIZE_SUB_TITLE_SUB_FONT)  # sub-title
                        fig.suptitle("%s指示牌不同距离下遍历法解码正确率,语义剪枝筛选率,可能合并率" % shape)  # title
                        fig.legend(loc="upper right", bbox_to_anchor=(1, 1), bbox_transform=ax.transAxes)
                        fig.subplots_adjust(top=0.85)
                        fig.subplots_adjust(left=0.093, bottom=0.083, right=0.92)
                        # plt.show()
                        fn = PATH + "[%d] %s-%d%d-%d%d_正确率+模块筛选率.png" % \
                             (PLOT_GROUP_IDX, shape, int(bool_scale), int(bool_ratio), int(bool_delta), int(bool_zero))
                        plt.savefig(fn, dpi=200)
                        plt.close()
                        print("SAVED:", fn)

# === #10 === 【ver2】每种指示牌 不同距离下 【两个信息的四个组合】 正确率（一级） (##11-##10-##01-##00)
PLOT_GROUP_IDX += 1
do_draw_this_idx = PLOT_DO_DRAW_REDRAW_ALL is True or PLOT_DO_DRAW[PLOT_GROUP_IDX] is True
print("===== IDX=%d: %s =====" % (PLOT_GROUP_IDX, "DO DRAW" if do_draw_this_idx is True else "SKIPPED"))
if do_draw_this_idx:
    colors = cm.get_cmap("rainbow")(np.linspace(0, 1, 4))
    for shape in ALL_SHAPES:
        for bool_scale in ALL_SETTING_BOOL:
            for bool_ratio in ALL_SETTING_BOOL:
                _color_idx = 4
                # plt.clf()
                fig, ax = plt.subplots()
                data_all = df_v2.loc[(df_v2["形状"] == shape)
                                     & (df_v2["双行"] == ALL_SETTING_BOOL_2_VAL_STR[bool_scale])
                                     & (df_v2["比例"] == ALL_SETTING_BOOL_2_VAL_STR[bool_ratio])]
                y_tick_step = 0.05
                y_min = 99
                for bool_delta in ALL_SETTING_BOOL:
                    for bool_zero in ALL_SETTING_BOOL:
                        _color_idx -= 1
                        data = data_all.loc[(df_v2["数量差"] == ALL_SETTING_BOOL_2_VAL_STR[bool_delta])
                                            & (df_v2["行首零"] == ALL_SETTING_BOOL_2_VAL_STR[bool_zero])]
                        data = data[["1正确率"]]
                        data = data.values  # <np.ndarray> of shape (cnt_group, 2)

                        y_min = min(y_min, get_lim(np.min(data), y_tick_step) - y_tick_step)

                        is_11 = bool_delta is True and bool_zero is True
                        labels = [
                            get_setting_str(scale=None, ratio=None, delta=bool_delta, zero=bool_zero, pure=True), ]
                        line_styles = ["--", ]
                        for _d, _l, _ls in zip(data.T, labels, line_styles):
                            ax.plot(_d, label=_l, linestyle=_ls if is_11 is False else "-",
                                    color=colors[_color_idx],
                                    linewidth=SIZE_LINE if is_11 is False else SIZE_LINE + 2)
                            ax.scatter(ALL_X_TICKS, _d, color=colors[_color_idx], s=SIZE_SCATTER)
                            # print(_d, y_min)

                set_plt_info(ax)
                ax_ylim = (max(0, min(0.65, y_min)), 1)
                ax.set_yticks(np.arange(ax_ylim[0], ax_ylim[1] + y_tick_step, y_tick_step))
                ax.set_yticklabels(get_percentage_y_ticks(ax_ylim, y_tick_step), fontsize=SIZE_AXIS_TICK_FONT)
                ax.set_ylim(ax_ylim[0], ax_ylim[1])

                plt.title(get_setting_str(scale=bool_scale, ratio=bool_ratio, delta=None, zero=None),
                          fontsize=SIZE_SUB_TITLE_SUB_FONT)  # sub-title
                fig.suptitle("%s指示牌不同距离下不同信息组合遍历法解码大类信息正确率" % shape)  # title
                fig.subplots_adjust(left=0.093, bottom=0.083, right=0.983)
                # fig.subplots_adjust(top=0.85)
                # plt.show()
                # exit()
                fn = PATH + "[%d] %s-%d%d-##_一级正确率.png" % \
                     (PLOT_GROUP_IDX, shape, int(bool_scale), int(bool_ratio))
                plt.savefig(fn, dpi=200)
                plt.close()
                print("SAVED:", fn)

# === #11 === 【ver2】每种指示牌 不同距离下 【两个信息的四个组合】 正确率（一级&二级） (##11-##10-##01-##00)
PLOT_GROUP_IDX += 1
do_draw_this_idx = PLOT_DO_DRAW_REDRAW_ALL is True or PLOT_DO_DRAW[PLOT_GROUP_IDX] is True
print("===== IDX=%d: %s =====" % (PLOT_GROUP_IDX, "DO DRAW" if do_draw_this_idx is True else "SKIPPED"))
if do_draw_this_idx:
    colors = cm.get_cmap("rainbow")(np.linspace(0, 1, 4))
    for shape in ALL_SHAPES:
        for bool_scale in ALL_SETTING_BOOL:
            for bool_ratio in ALL_SETTING_BOOL:
                _color_idx = 4
                # plt.clf()
                fig, ax = plt.subplots()
                data_all = df_v2.loc[(df_v2["形状"] == shape)
                                     & (df_v2["双行"] == ALL_SETTING_BOOL_2_VAL_STR[bool_scale])
                                     & (df_v2["比例"] == ALL_SETTING_BOOL_2_VAL_STR[bool_ratio])]
                y_tick_step = 0.05
                y_min = 99
                for bool_delta in ALL_SETTING_BOOL:
                    for bool_zero in ALL_SETTING_BOOL:
                        _color_idx -= 1
                        data = data_all.loc[(df_v2["数量差"] == ALL_SETTING_BOOL_2_VAL_STR[bool_delta])
                                            & (df_v2["行首零"] == ALL_SETTING_BOOL_2_VAL_STR[bool_zero])]
                        data = data[["2正确率"]]
                        data = data.values  # <np.ndarray> of shape (cnt_group, 2)

                        y_min = min(y_min, get_lim(np.min(data), y_tick_step) - y_tick_step)

                        is_11 = bool_delta is True and bool_zero is True
                        labels = [
                            get_setting_str(scale=None, ratio=None, delta=bool_delta, zero=bool_zero, pure=True), ]
                        line_styles = ["--", ]
                        for _d, _l, _ls in zip(data.T, labels, line_styles):
                            ax.plot(_d, label=_l, linestyle=_ls if is_11 is False else "-",
                                    color=colors[_color_idx],
                                    linewidth=SIZE_LINE if is_11 is False else SIZE_LINE + 2)
                            ax.scatter(ALL_X_TICKS, _d, color=colors[_color_idx], s=SIZE_SCATTER)
                            # print(_d, y_min)

                set_plt_info(ax)
                ax_ylim = (max(0, min(0.65, y_min)), 1)
                ax.set_yticks(np.arange(ax_ylim[0], ax_ylim[1] + y_tick_step, y_tick_step))
                ax.set_yticklabels(get_percentage_y_ticks(ax_ylim, y_tick_step), fontsize=SIZE_AXIS_TICK_FONT)
                ax.set_ylim(ax_ylim[0], ax_ylim[1])

                plt.title(get_setting_str(scale=bool_scale, ratio=bool_ratio, delta=None, zero=None),
                          fontsize=SIZE_SUB_TITLE_SUB_FONT)  # sub-title
                fig.suptitle("%s指示牌不同距离下不同信息组合遍历法解码全部信息正确率" % shape)  # title
                fig.subplots_adjust(left=0.093, bottom=0.083, right=0.983)
                # fig.subplots_adjust(top=0.85)
                # plt.show()
                # exit()
                fn = PATH + "[%d] %s-%d%d-##_全部正确率.png" % \
                     (PLOT_GROUP_IDX, shape, int(bool_scale), int(bool_ratio))
                plt.savefig(fn, dpi=200)
                plt.close()
                print("SAVED:", fn)

# === #12 === 【ver2】每种指示牌 不同距离下 【两个比例的四个组合】 正确率（一级） (11##-10##-01##-00##)
PLOT_GROUP_IDX += 1
do_draw_this_idx = PLOT_DO_DRAW_REDRAW_ALL is True or PLOT_DO_DRAW[PLOT_GROUP_IDX] is True
print("===== IDX=%d: %s =====" % (PLOT_GROUP_IDX, "DO DRAW" if do_draw_this_idx is True else "SKIPPED"))
if do_draw_this_idx:
    colors = cm.get_cmap("rainbow")(np.linspace(0, 1, 4))
    for shape in ALL_SHAPES:
        for bool_delta in ALL_SETTING_BOOL:
            for bool_zero in ALL_SETTING_BOOL:
                _color_idx = 4
                # plt.clf()
                fig, ax = plt.subplots()
                data_all = df_v2.loc[(df_v2["形状"] == shape)
                                     & (df_v2["数量差"] == ALL_SETTING_BOOL_2_VAL_STR[bool_delta])
                                     & (df_v2["行首零"] == ALL_SETTING_BOOL_2_VAL_STR[bool_zero])]
                y_tick_step = 0.05
                y_min = 99
                for bool_scale in ALL_SETTING_BOOL:
                    for bool_ratio in ALL_SETTING_BOOL:
                        _color_idx -= 1
                        data = data_all.loc[(df_v2["双行"] == ALL_SETTING_BOOL_2_VAL_STR[bool_scale])
                                            & (df_v2["比例"] == ALL_SETTING_BOOL_2_VAL_STR[bool_ratio])]
                        data = data[["1正确率"]]
                        data = data.values  # <np.ndarray> of shape (cnt_group, 2)

                        y_min = min(y_min, get_lim(np.min(data), y_tick_step) - y_tick_step)

                        is_11 = bool_scale is True and bool_ratio is True
                        labels = [
                            get_setting_str(scale=bool_scale, ratio=bool_ratio, delta=None, zero=None, pure=True), ]
                        line_styles = ["--", ]
                        for _d, _l, _ls in zip(data.T, labels, line_styles):
                            ax.plot(_d, label=_l, linestyle=_ls if is_11 is False else "-",
                                    color=colors[_color_idx],
                                    linewidth=SIZE_LINE if is_11 is False else SIZE_LINE + 2)
                            ax.scatter(ALL_X_TICKS, _d, color=colors[_color_idx], s=SIZE_SCATTER)
                            # print(_d, y_min)

                set_plt_info(ax)
                ax_ylim = (max(0, min(0.65, y_min)), 1)
                ax.set_yticks(np.arange(ax_ylim[0], ax_ylim[1] + y_tick_step, y_tick_step))
                ax.set_yticklabels(get_percentage_y_ticks(ax_ylim, y_tick_step), fontsize=SIZE_AXIS_TICK_FONT)
                ax.set_ylim(ax_ylim[0], ax_ylim[1])

                plt.title(get_setting_str(scale=None, ratio=None, delta=bool_delta, zero=bool_zero),
                          fontsize=SIZE_SUB_TITLE_SUB_FONT)  # sub-title
                fig.suptitle("%s指示牌不同距离下不同比例组合遍历法解码大类信息正确率" % shape)  # title
                fig.subplots_adjust(left=0.093, bottom=0.083, right=0.983)
                # fig.subplots_adjust(top=0.85)
                # plt.show()
                # exit()
                fn = PATH + "[%d] %s-##-%d%d_一级正确率.png" % (PLOT_GROUP_IDX, shape, int(bool_delta), int(bool_zero))
                plt.savefig(fn, dpi=200)
                plt.close()
                print("SAVED:", fn)

# === #13 === 【ver2】每种指示牌 不同距离下 【两个比例的四个组合】 正确率（一级&二级） (11##-10##-01##-00##)
PLOT_GROUP_IDX += 1
do_draw_this_idx = PLOT_DO_DRAW_REDRAW_ALL is True or PLOT_DO_DRAW[PLOT_GROUP_IDX] is True
print("===== IDX=%d: %s =====" % (PLOT_GROUP_IDX, "DO DRAW" if do_draw_this_idx is True else "SKIPPED"))
if do_draw_this_idx:
    colors = cm.get_cmap("rainbow")(np.linspace(0, 1, 4))
    for shape in ALL_SHAPES:
        for bool_delta in ALL_SETTING_BOOL:
            for bool_zero in ALL_SETTING_BOOL:
                _color_idx = 4
                # plt.clf()
                fig, ax = plt.subplots()
                data_all = df_v2.loc[(df_v2["形状"] == shape)
                                     & (df_v2["数量差"] == ALL_SETTING_BOOL_2_VAL_STR[bool_delta])
                                     & (df_v2["行首零"] == ALL_SETTING_BOOL_2_VAL_STR[bool_zero])]
                y_tick_step = 0.05
                y_min = 99
                for bool_scale in ALL_SETTING_BOOL:
                    for bool_ratio in ALL_SETTING_BOOL:
                        _color_idx -= 1
                        data = data_all.loc[(df_v2["双行"] == ALL_SETTING_BOOL_2_VAL_STR[bool_scale])
                                            & (df_v2["比例"] == ALL_SETTING_BOOL_2_VAL_STR[bool_ratio])]
                        data = data[["2正确率"]]
                        data = data.values  # <np.ndarray> of shape (cnt_group, 2)

                        y_min = min(y_min, get_lim(np.min(data), y_tick_step) - y_tick_step)

                        is_11 = bool_scale is True and bool_ratio is True
                        labels = [
                            get_setting_str(scale=bool_scale, ratio=bool_ratio, delta=None, zero=None, pure=True), ]
                        line_styles = ["--", ]
                        for _d, _l, _ls in zip(data.T, labels, line_styles):
                            ax.plot(_d, label=_l, linestyle=_ls if is_11 is False else "-",
                                    color=colors[_color_idx],
                                    linewidth=SIZE_LINE if is_11 is False else SIZE_LINE + 2)
                            ax.scatter(ALL_X_TICKS, _d, color=colors[_color_idx], s=SIZE_SCATTER)
                            # print(_d, y_min)

                set_plt_info(ax)
                ax_ylim = (max(0, min(0.65, y_min)), 1)
                ax.set_yticks(np.arange(ax_ylim[0], ax_ylim[1] + y_tick_step, y_tick_step))
                ax.set_yticklabels(get_percentage_y_ticks(ax_ylim, y_tick_step), fontsize=SIZE_AXIS_TICK_FONT)
                ax.set_ylim(ax_ylim[0], ax_ylim[1])

                plt.title(get_setting_str(scale=None, ratio=None, delta=bool_delta, zero=bool_zero),
                          fontsize=SIZE_SUB_TITLE_SUB_FONT)  # sub-title
                fig.suptitle("%s指示牌不同距离下不同信息组合遍历法解码全部信息正确率" % shape)  # title
                fig.subplots_adjust(left=0.093, bottom=0.083, right=0.983)
                # fig.subplots_adjust(top=0.85)
                # plt.show()
                # exit()
                fn = PATH + "[%d] %s-##-%d%d_全部正确率.png" % (PLOT_GROUP_IDX, shape, int(bool_delta), int(bool_zero))
                plt.savefig(fn, dpi=200)
                plt.close()
                print("SAVED:", fn)

# === #14 === 【ver3】每种指示牌 不同距离下 正确率（一级/一级&二级）+筛选率 (all ### comb)
PLOT_GROUP_IDX += 1
do_draw_this_idx = PLOT_DO_DRAW_REDRAW_ALL is True or PLOT_DO_DRAW[PLOT_GROUP_IDX] is True
print("===== IDX=%d: %s =====" % (PLOT_GROUP_IDX, "DO DRAW" if do_draw_this_idx is True else "SKIPPED"))
if do_draw_this_idx:
    colors = cm.get_cmap("rainbow")(np.linspace(0, 1, 3))
    # ax_tree_color, ax_tol_color = "grey", "green"
    ax_tree_color, ax_tol_color, c = colors
    for bool_scale in ALL_SETTING_BOOL:
        for bool_ratio in ALL_SETTING_BOOL:
            for shape in ALL_SHAPES:
                # plt.clf()
                fig, ax = plt.subplots()
                ax_tree = ax.twinx()
                ax_tol = ax.twinx()
                # acc lines and points
                data_all = df_v3.loc[(df_v3["形状"] == shape)
                                     & (df_v3["双行"] == ALL_SETTING_BOOL_2_VAL_STR[bool_scale])
                                     & (df_v3["比例"] == ALL_SETTING_BOOL_2_VAL_STR[bool_ratio])]
                data = data_all[["1正确率", "2正确率"]]
                data = data.values  # <np.ndarray> of shape (cnt_group, 2)

                labels = ["大类信息正确率", "全部信息正确率"]
                line_styles = ["-", "--"]
                for _d, _l, _ls in zip(data.T, labels, line_styles):
                    ax.plot(_d, label=_l, linestyle=_ls, color=c, linewidth=SIZE_LINE)
                    ax.scatter(ALL_X_TICKS, _d, color=c, s=SIZE_SCATTER)
                    # print(_d)
                ax.set_xlabel("距离 / m")
                ax.set_xticks(ALL_X_TICKS), ax.set_xticklabels(ALL_X_TICK_LABELS)
                ax.set_ylabel("比率")
                ax.set_yticks(ALL_Y_TICKS), ax.set_yticklabels(ALL_Y_TICK_LABELS)
                ax.set_xlim(ALL_X_TICKS[0], ALL_X_TICKS[-1])
                ax.set_ylim(ALL_Y_TICKS[0], ALL_Y_TICKS[-1])

                # filter ratio bars
                # tree
                data = data_all["语义筛选"]
                data = data.values  # <np.ndarray> of shape (1, 2)
                ax_tree.bar(ALL_X_TICKS, height=data, width=ALL_X_TICKS[-1] - ALL_X_TICKS[-2],
                            label="语义剪枝模块筛选率", bottom=0, color=ax_tree_color, alpha=0.2)
                ax_tree.set_ylabel("语义剪枝筛选率", loc="bottom", color=ax_tree_color)
                ax_tree_step = 0.1
                ax_tree_lim = (0, get_lim(np.max(data), step=ax_tree_step))
                ax_tree.set_yticks(np.arange(ax_tree_lim[0], ax_tree_lim[1] + ax_tree_step, ax_tree_step))
                ax_tree.set_yticklabels(get_percentage_y_ticks(lim=ax_tree_lim, step=ax_tree_step),
                                        color=ax_tree_color)
                ax_tree.set_ylim(ax_tree_lim[0], ax_tree_lim[1] * 2 + ax_tree_step * 2)
                # combine
                data = data_all["合并筛选"]
                data = data.values  # <np.ndarray> of shape (1, 2)
                ax_tol.bar(ALL_X_TICKS, height=-1 * data, width=ALL_X_TICKS[-1] - ALL_X_TICKS[-2],
                           label="可能合并模块合并率", bottom=0, color=ax_tol_color, alpha=0.2)
                ax_tol.set_ylabel("合并率", loc="top", color=ax_tol_color)
                ax_tol_step = 0.1
                ax_tol_lim = (-1 * get_lim(np.max(data), step=ax_tol_step), 0)
                ax_tol.set_yticks(np.arange(ax_tol_lim[0], ax_tol_lim[1] + ax_tol_step, ax_tol_step))
                ax_tol.set_yticklabels([i[1:] if "-" == i[0] else i
                                        for i in get_percentage_y_ticks(lim=ax_tol_lim, step=ax_tol_step)],
                                       color=ax_tol_color)
                ax_tol.set_ylim(ax_tol_lim[0] * 2 - ax_tol_step * 2, ax_tol_lim[1])

                plt.title(get_setting_str(scale=bool_scale, ratio=bool_ratio, delta=None, zero=None,
                                          lines=["模块筛选率(合并率) = 1 - 进入模块数/离开模块数, 除数为零结果按 0 计"]),
                          fontsize=SIZE_SUB_TITLE_SUB_FONT)  # sub-title
                fig.suptitle("%s指示牌不同距离下回溯法解码正确率,语义剪枝筛选率,可能合并率" % shape)  # title
                fig.legend(loc="upper right", bbox_to_anchor=(1, 1), bbox_transform=ax.transAxes)
                fig.subplots_adjust(top=0.85)
                fig.subplots_adjust(left=0.093, bottom=0.083, right=0.92)
                # plt.show()
                fn = PATH + "[%d] %s-%d%d-#_正确率+模块筛选率.png" % \
                     (PLOT_GROUP_IDX, shape, int(bool_scale), int(bool_ratio))
                plt.savefig(fn, dpi=200)
                plt.close()
                print("SAVED:", fn)

"""
# === #14 === 【ver3】每种指示牌 不同距离下 正确率（一级/一级&二级）+筛选率 (all ### comb)
PLOT_GROUP_IDX += 1
do_draw_this_idx = PLOT_DO_DRAW_REDRAW_ALL is True or PLOT_DO_DRAW[PLOT_GROUP_IDX] is True
print("===== IDX=%d: %s =====" % (PLOT_GROUP_IDX, "DO DRAW" if do_draw_this_idx is True else "SKIPPED"))
if do_draw_this_idx:
    colors = cm.get_cmap("rainbow")(np.linspace(0, 1, 3))
    # ax_tree_color, ax_tol_color = "grey", "green"
    ax_tree_color, ax_tol_color, c = colors
    for bool_scale in [True]:  # ALL_SETTING_BOOL:
        for bool_ratio in [True]:  # ALL_SETTING_BOOL:
            for shape in ["圆形"]:  # ALL_SHAPES:
                # plt.clf()
                fig, ax = plt.subplots()
                ax_tree = ax.twinx()
                ax_tol = ax.twinx()
                # acc lines and points
                data_all = df_v3.loc[(df_v3["形状"] == shape)
                                     & (df_v3["双行"] == ALL_SETTING_BOOL_2_VAL_STR[bool_scale])
                                     & (df_v3["比例"] == ALL_SETTING_BOOL_2_VAL_STR[bool_ratio])]
                data = data_all[["1正确率", "2正确率"]]
                data = data.values  # <np.ndarray> of shape (cnt_group, 2)

                labels = ["大类信息正确率", "全部信息正确率"]
                line_styles = ["-", "--"]
                for _d, _l, _ls in zip(data.T, labels, line_styles):
                    ax.plot(_d, label=_l, linestyle=_ls, color=c, linewidth=SIZE_LINE)
                    ax.scatter(ALL_X_TICKS, _d, color=c, s=SIZE_SCATTER)
                    # print(_d)
                ax.set_xlabel("距离 / m", fontsize=13)
                ax.set_xticks(ALL_X_TICKS), ax.set_xticklabels(ALL_X_TICK_LABELS)
                ax.set_ylabel("比率", fontsize=13)
                ax.set_yticks(ALL_Y_TICKS), ax.set_yticklabels(ALL_Y_TICK_LABELS)
                ax.set_xlim(ALL_X_TICKS[0], ALL_X_TICKS[-1])
                ax.set_ylim(ALL_Y_TICKS[0], ALL_Y_TICKS[-1])

                # filter ratio bars
                # tree
                data = data_all["语义筛选"]
                data = data.values  # <np.ndarray> of shape (1, 2)
                ax_tree.bar(ALL_X_TICKS, height=data, width=ALL_X_TICKS[-1] - ALL_X_TICKS[-2],
                            label="语义剪枝模块筛选率", bottom=0, color=ax_tree_color, alpha=0.2)
                ax_tree.set_ylabel("语义剪枝筛选率", loc="bottom", color=ax_tree_color, fontsize=13)
                ax_tree_step = 0.1
                ax_tree_lim = (0, get_lim(np.max(data), step=ax_tree_step))
                ax_tree.set_yticks(np.arange(ax_tree_lim[0], ax_tree_lim[1] + ax_tree_step, ax_tree_step))
                ax_tree.set_yticklabels(get_percentage_y_ticks(lim=ax_tree_lim, step=ax_tree_step),
                                        color=ax_tree_color)
                ax_tree.set_ylim(ax_tree_lim[0], ax_tree_lim[1] * 2 + ax_tree_step * 2)
                # combine
                data = data_all["合并筛选"]
                data = data.values  # <np.ndarray> of shape (1, 2)
                ax_tol.bar(ALL_X_TICKS, height=-1 * data, width=ALL_X_TICKS[-1] - ALL_X_TICKS[-2],
                           label="可能合并模块合并率", bottom=0, color=ax_tol_color, alpha=0.2)
                ax_tol.set_ylabel("合并率", loc="top", color=ax_tol_color, fontsize=13)
                ax_tol_step = 0.1
                ax_tol_lim = (-1 * get_lim(np.max(data), step=ax_tol_step), 0)
                ax_tol.set_yticks(np.arange(ax_tol_lim[0], ax_tol_lim[1] + ax_tol_step, ax_tol_step))
                ax_tol.set_yticklabels([i[1:] if "-" == i[0] else i
                                        for i in get_percentage_y_ticks(lim=ax_tol_lim, step=ax_tol_step)],
                                       color=ax_tol_color)
                ax_tol.set_ylim(ax_tol_lim[0] * 2 - ax_tol_step * 2, ax_tol_lim[1])

                # plt.title(get_setting_str(scale=bool_scale, ratio=bool_ratio, delta=None, zero=None,
                #                           # lines=["模块筛选率(合并率) = 1 - 进入模块数/离开模块数, 除数为零结果按 0 计"]
                #                           ),
                #           fontsize=SIZE_SUB_TITLE_SUB_FONT)  # sub-title
                # fig.suptitle("%s指示牌不同距离下回溯法解码正确率,语义剪枝筛选率,可能合并率" % shape)  # title
                # fig.legend(loc="upper right", bbox_to_anchor=(1, 1), bbox_transform=ax.transAxes)
                fig.legend(loc="lower right", bbox_to_anchor=(0.85, 0.1), bbox_transform=ax.transAxes,
                           prop={"size": 10})
                # fig.subplots_adjust(top=0.85)
                # fig.subplots_adjust(left=0.093, bottom=0.083, right=0.92)
                fig.subplots_adjust(top=0.95, left=0.1, bottom=0.1, right=0.9)
                # plt.show()
                # fn = PATH + "[%d] %s-%d%d-#_正确率+模块筛选率.png" % \
                #      (PLOT_GROUP_IDX, shape, int(bool_scale), int(bool_ratio))
                # plt.savefig(fn, dpi=200)
                fn = r"C:\Users\John\Downloads\1.png"
                plt.savefig(fn, dpi=500)
                plt.close()
                print("SAVED:", fn)
"""  # no titles + larger labels version, for circle-11X only

# === #15 === 【ver3】每种指示牌 不同距离下 【两个比例的四个组合】 正确率（一级） (11#-10#-01#-00#)
PLOT_GROUP_IDX += 1
do_draw_this_idx = PLOT_DO_DRAW_REDRAW_ALL is True or PLOT_DO_DRAW[PLOT_GROUP_IDX] is True
print("===== IDX=%d: %s =====" % (PLOT_GROUP_IDX, "DO DRAW" if do_draw_this_idx is True else "SKIPPED"))
if do_draw_this_idx:
    colors = cm.get_cmap("rainbow")(np.linspace(0, 1, 4))
    for shape in ALL_SHAPES:
        _color_idx = 4
        # plt.clf()
        fig, ax = plt.subplots()
        data_all = df_v3.loc[(df_v3["形状"] == shape)]
        y_tick_step = 0.05
        y_min = 99
        for bool_scale in ALL_SETTING_BOOL:
            for bool_ratio in ALL_SETTING_BOOL:
                _color_idx -= 1
                data = data_all.loc[(df_v3["双行"] == ALL_SETTING_BOOL_2_VAL_STR[bool_scale])
                                    & (df_v3["比例"] == ALL_SETTING_BOOL_2_VAL_STR[bool_ratio])]
                data = data[["1正确率"]]
                data = data.values  # <np.ndarray> of shape (cnt_group, 2)

                y_min = min(y_min, get_lim(np.min(data), y_tick_step) - y_tick_step)

                is_11 = bool_scale is True and bool_ratio is True
                labels = [
                    get_setting_str(scale=bool_scale, ratio=bool_ratio, delta=None, zero=None, pure=True), ]
                line_styles = ["--", ]
                for _d, _l, _ls in zip(data.T, labels, line_styles):
                    ax.plot(_d, label=_l, linestyle=_ls if is_11 is False else "-",
                            color=colors[_color_idx],
                            linewidth=SIZE_LINE if is_11 is False else SIZE_LINE + 2)
                    ax.scatter(ALL_X_TICKS, _d, color=colors[_color_idx], s=SIZE_SCATTER)
                    # print(_d, y_min)

        set_plt_info(ax)
        ax_ylim = (max(0, min(0.65, y_min)), 1)
        ax.set_yticks(np.arange(ax_ylim[0], ax_ylim[1] + y_tick_step, y_tick_step))
        ax.set_yticklabels(get_percentage_y_ticks(ax_ylim, y_tick_step), fontsize=SIZE_AXIS_TICK_FONT)
        ax.set_ylim(ax_ylim[0], ax_ylim[1])

        plt.title(get_setting_str(scale=None, ratio=None, delta=None, zero=None),
                  fontsize=SIZE_SUB_TITLE_SUB_FONT)  # sub-title
        fig.suptitle("%s指示牌不同距离下不同比例组合回溯法解码大类信息正确率" % shape)  # title
        fig.subplots_adjust(left=0.093, bottom=0.083, right=0.983)
        # fig.subplots_adjust(top=0.85)
        # plt.show()
        # exit()
        fn = PATH + "[%d] %s-##-#_一级正确率.png" % (PLOT_GROUP_IDX, shape)
        plt.savefig(fn, dpi=200)
        plt.close()
        print("SAVED:", fn)

# === #16 === 【ver3】每种指示牌 不同距离下 【两个比例的四个组合】 正确率（一级&二级） (11#-10#-01#-00#) todo
PLOT_GROUP_IDX += 1
do_draw_this_idx = PLOT_DO_DRAW_REDRAW_ALL is True or PLOT_DO_DRAW[PLOT_GROUP_IDX] is True
print("===== IDX=%d: %s =====" % (PLOT_GROUP_IDX, "DO DRAW" if do_draw_this_idx is True else "SKIPPED"))
if do_draw_this_idx:
    colors = cm.get_cmap("rainbow")(np.linspace(0, 1, 4))
    for shape in ALL_SHAPES:
        _color_idx = 4
        # plt.clf()
        fig, ax = plt.subplots()
        data_all = df_v3.loc[(df_v3["形状"] == shape)]
        y_tick_step = 0.05
        y_min = 99
        for bool_scale in ALL_SETTING_BOOL:
            for bool_ratio in ALL_SETTING_BOOL:
                _color_idx -= 1
                data = data_all.loc[(df_v3["双行"] == ALL_SETTING_BOOL_2_VAL_STR[bool_scale])
                                    & (df_v3["比例"] == ALL_SETTING_BOOL_2_VAL_STR[bool_ratio])]
                data = data[["2正确率"]]
                data = data.values  # <np.ndarray> of shape (cnt_group, 2)

                y_min = min(y_min, get_lim(np.min(data), y_tick_step) - y_tick_step)

                is_11 = bool_scale is True and bool_ratio is True
                labels = [
                    get_setting_str(scale=bool_scale, ratio=bool_ratio, delta=None, zero=None, pure=True), ]
                line_styles = ["--", ]
                for _d, _l, _ls in zip(data.T, labels, line_styles):
                    ax.plot(_d, label=_l, linestyle=_ls if is_11 is False else "-",
                            color=colors[_color_idx],
                            linewidth=SIZE_LINE if is_11 is False else SIZE_LINE + 2)
                    ax.scatter(ALL_X_TICKS, _d, color=colors[_color_idx], s=SIZE_SCATTER)
                    # print(_d, y_min)

        set_plt_info(ax)
        ax_ylim = (max(0, min(0.65, y_min)), 1)
        ax.set_yticks(np.arange(ax_ylim[0], ax_ylim[1] + y_tick_step, y_tick_step))
        ax.set_yticklabels(get_percentage_y_ticks(ax_ylim, y_tick_step), fontsize=SIZE_AXIS_TICK_FONT)
        ax.set_ylim(ax_ylim[0], ax_ylim[1])

        plt.title(get_setting_str(scale=None, ratio=None, delta=None, zero=None),
                  fontsize=SIZE_SUB_TITLE_SUB_FONT)  # sub-title
        fig.suptitle("%s指示牌不同距离下不同比例组合回溯法解码全部信息正确率" % shape)  # title
        fig.subplots_adjust(left=0.093, bottom=0.083, right=0.983)
        # fig.subplots_adjust(top=0.85)
        # plt.show()
        # exit()
        fn = PATH + "[%d] %s-##-#_全部正确率.png" % (PLOT_GROUP_IDX, shape)
        plt.savefig(fn, dpi=200)
        plt.close()
        print("SAVED:", fn)

print()
