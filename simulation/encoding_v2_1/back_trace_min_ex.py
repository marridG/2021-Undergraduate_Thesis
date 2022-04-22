import numpy as np

data = np.array(
    [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 1., 1., 1., 1., 1., 0., 0., 0., 1., 1., 1., 1., 1., 1., 1.,
     1., 0., 0., 0., 0., 1., 1., 1., 1., np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan])  # tri11 20m


# data = np.array([1., 1., 1., 1., 1.,
#                  0., 0., 0., 1., 1., 1., 1., 1., 1., 1., 1., 0., 0., 0., 0., 1., 1., 1., 1., ])
# data = np.array([1., 1., 1., 1., 1.,
#                  0., 0., 0., 1., 1., 1., 1., 1., 1., 1., 1., 0., 0., 0., 1., 1., 1., 1., ])
# data = np.array([1., 1., 1., 1., 1.,
#                  0., 0., 0., 1., 1., 1., 1., 1., 1., 1., 1., 0., 1., 1., 1., 1., ])


def cal(points, max_cnt_per_bar=2):
    ALLOW_END_1 = False
    points = points.astype(int)
    pts_l_neq_r = np.concatenate(([True], points[:-1] != points[1:], [True]))
    pts_l_neq_r_start_idx = np.where(True == pts_l_neq_r)[0]
    pts_l_neq_r_start_idx_is_one_idx = np.where(1 == points[pts_l_neq_r_start_idx[:-1]])
    pts_conti_cnt = np.diff(pts_l_neq_r_start_idx)
    pts_conti_cnt[pts_l_neq_r_start_idx_is_one_idx] *= -1
    # now, in variable `pts_conti_cnt`, each element is the number of continuous 1/0's (cnt_1<0, cnt_0>0)
    if pts_conti_cnt[0] < 0:
        pts_conti_cnt = pts_conti_cnt[1:]

    _empty_val = -99
    all_possibilities = []  # [{"seq"/"pt_cnt": []}, ...]
    seq = [_empty_val] * 8
    seq_pt_cnt = [_empty_val] * 8

    def back_trace(_seq_ptr, _conti_ptr):
        if 8 == _seq_ptr:
            # === assuming the last digit of the pattern can NOT be 1 ===
            if ALLOW_END_1 is False:
                # last digit is 1
                if 1 == seq[-1]:
                    return False
                # unused zeros at _conti_ptr+2
                if _conti_ptr <= (len(pts_conti_cnt) - 1) - 2:
                    return False
                # unused zeros at _conti_ptr
                if 0 < pts_conti_cnt[_conti_ptr]:
                    return False
            # === assuming the last digit of the pattern CAN be 1 ===
            else:  # i.e., ALLOW_END_1 is True:
                if 0 == seq[-1]:
                    # unused zeros at _conti_ptr+2
                    if _conti_ptr <= (len(pts_conti_cnt) - 1) - 2:
                        return False
                    # unused zeros at _conti_ptr
                    if 0 < pts_conti_cnt[_conti_ptr]:
                        return False
                else:
                    # unused ones/zeros at _conti_ptr+1
                    if _conti_ptr <= (len(pts_conti_cnt) - 1) - 1:
                        return False
            # return True
            all_possibilities.append({"seq": seq.copy(), "pt_cnt": seq_pt_cnt.copy()})
            return False

        for __pt_cnt in range(max_cnt_per_bar - 1, max_cnt_per_bar + 1):
            if __pt_cnt > abs(pts_conti_cnt[_conti_ptr]):
                continue
            if _seq_ptr > 0 and abs(__pt_cnt - seq_pt_cnt[_seq_ptr - 1]) > 1:
                continue
            __pt_is_one = (pts_conti_cnt[_conti_ptr] < 0)
            __pt_val = 1 if __pt_is_one else 0

            seq[_seq_ptr] = __pt_val
            seq_pt_cnt[_seq_ptr] = __pt_cnt
            _seq_ptr += 1
            pts_conti_cnt[_conti_ptr] += __pt_cnt * (1 if __pt_is_one else -1)
            _conti_ptr_moved = (0 == pts_conti_cnt[_conti_ptr])
            _conti_ptr += 1 if _conti_ptr_moved else 0

            _next_res = back_trace(_seq_ptr=_seq_ptr, _conti_ptr=_conti_ptr)  # CHECKPOINT
            if _next_res is True:
                return True
            # restore status
            _conti_ptr -= 1 if _conti_ptr_moved else 0
            pts_conti_cnt[_conti_ptr] -= __pt_cnt * (1 if __pt_is_one else -1)
            _seq_ptr -= 1
            seq_pt_cnt[_seq_ptr] = _empty_val
            seq[_seq_ptr] = _empty_val
            continue  # CHECKPOINT
        return False

    bt_res = back_trace(_seq_ptr=0, _conti_ptr=0)
    print(bt_res)
    print(all_possibilities)

    return


def handle(__line):
    schema_length = 8
    __line_not_nan_idx = np.where(False == np.isnan(__line))
    if 0 == len(__line_not_nan_idx[0]) or schema_length > len(__line_not_nan_idx[0]):
        return  # continue
    __line_nan_cnt_head = __line_not_nan_idx[0][0] - 0
    __line_data = __line[__line_not_nan_idx]  # remove nan-s (Note: np.nan != np.nan)
    return cal(__line_data)


handle(data)
