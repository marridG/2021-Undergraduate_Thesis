from typing import List, Dict
import itertools
import numpy as np


class Lv1DuplicateCheck:
    def __init__(self, all_lv1_seq: List[List[int]], pt_per_bar: int = 1, col_width: int = 100):
        """
        :param all_lv1_seq:        list of all possible level 1 combinations
                                        e.g. [ [1, 1, 0, 1, 1], [1, 0, 1, 0, 1], [1, 0, 0, 0, 1], ]
        :param pt_per_bar:          number of sample points per bar, must be >=1
        :param col_width:           ratio of the column width versus the sampling step-size
                                        e.g. if `col_width=100`, then there will be 100 possible
                                        starting location of the first sample point
        :return:
        """
        assert 1 == len(set([len(_comb) for _comb in all_lv1_seq]))
        assert pt_per_bar >= 1

        self.SEQ_COL_WIDTH = col_width

        # interpret problem: assuring multiple sample points per bar => assuring ONE sample point per bar
        if pt_per_bar > 1:
            all_lv1_seq = [[__bar for __bar in _comb for _ in range(pt_per_bar)] for _comb in all_lv1_seq]
            print("Points Count per Bar: %d => 1" % pt_per_bar)
        else:
            print("Points Count per Bar: 1 Maintained")
        self.SEQ_ALL = all_lv1_seq
        self.SEQ_CNT = len(all_lv1_seq)
        self.SEQ_LEN = len(self.SEQ_ALL[0])

        self.SEQ_TO_SAMPLE = self._gen_seq_to_sample()
        self.SEQ_MAX_LOC_IDX = len(self.SEQ_TO_SAMPLE[0]) - 1

    def _gen_seq_to_sample(self) -> np.ndarray:
        # generate the to-be-sampled target, by all the lv1 combinations and the width of each bar
        seq_to_sample = []
        for _seq in self.SEQ_ALL:
            _to_sam = []
            for __seq_bit in _seq:
                for i in range(self.SEQ_COL_WIDTH):
                    _to_sam.append(__seq_bit)
            seq_to_sample.append(_to_sam)

        res = np.array(seq_to_sample)
        print("To-be-Sampled Sequence Generated (with column_width=%d)" % self.SEQ_COL_WIDTH)
        return res

    def _gen_all_sample_plans(self) -> Dict[int, Dict[int, List[int]]]:
        # <dict>: { margin: { start: [<int>], ... } }
        sample_plans = {}
        for _margin in range(1, self.SEQ_COL_WIDTH):
            sample_plans[_margin] = {}
            for __start_loc in range(self.SEQ_COL_WIDTH):
                __all_loc = self._gen_all_loc(start=__start_loc, margin=_margin)
                __plan_is_valid = self._plan_is_valid(all_loc=__all_loc)
                if __plan_is_valid is True:
                    sample_plans[_margin][__start_loc] = __all_loc

        print("All Sample Plans Generated")
        return sample_plans

    def _gen_all_loc(self, start, margin) -> np.ndarray:
        """get the location of all sample points by the starting location of the first sample point and the margin"""
        res = []
        _crt_loc = start
        while _crt_loc <= self.SEQ_MAX_LOC_IDX:
            res.append(_crt_loc)
            _crt_loc += margin

        res = np.array(res)
        return res

    def _plan_is_valid(self, all_loc: np.ndarray) -> bool:
        all_loc_bin_idx = np.floor(all_loc * 1. / self.SEQ_COL_WIDTH)
        _arr_ptr = 0
        for _bin_idx in range(self.SEQ_LEN):
            if 0 == np.where(all_loc_bin_idx == _bin_idx)[0].size:
                return False
        return True

    @staticmethod
    def _sample_arr_2_str(sample_arr: np.ndarray) -> str:
        res = "".join([str(i) for i in sample_arr])
        return res

    def _search_all_possible_dup(self):
        """search all possible duplicate sampling results"""
        sample_plans = self._gen_all_sample_plans()

        # {comparison_str: {"no_dup": <bool>, "dups": [
        #   {"res": <str>,"margin": <int>, "start_left":[<int>], "start_right": [<int>] }
        # ] }, ...}
        intersect_all_res = {}
        for _margin, _margin_plans in sample_plans.items():
            _sample_res_set = [set() for _ in range(self.SEQ_CNT)]
            _sample_res_str_2_loc = [{} for _ in range(self.SEQ_CNT)]
            for __plan_start, __plan in _margin_plans.items():
                for __seq_idx in range(self.SEQ_CNT):
                    __seq = self.SEQ_TO_SAMPLE[__seq_idx]
                    __seq_sample_arr = __seq[__plan]
                    __seq_sample_str = self._sample_arr_2_str(sample_arr=__seq_sample_arr)
                    _sample_res_set[__seq_idx].add(__seq_sample_str)
                    try:
                        _sample_res_str_2_loc[__seq_idx][__seq_sample_str].append(
                            {"start": __plan_start, "loc": __plan})
                    except KeyError:
                        _sample_res_str_2_loc[__seq_idx][__seq_sample_str] = [
                            {"start": __plan_start, "loc": __plan}]

            for __res_idx_1 in range(self.SEQ_CNT):
                for __res_idx_2 in range(__res_idx_1, self.SEQ_CNT):
                    __comp_str = "%d-%d" % (__res_idx_1, __res_idx_2)
                    if __comp_str not in intersect_all_res.keys():
                        intersect_all_res[__comp_str] = {"no_dup": True, "dups": []}

                    __intersect = _sample_res_set[__res_idx_1].intersection(_sample_res_set[__res_idx_2])

                    if 0 != len(__intersect):
                        intersect_all_res[__comp_str]["no_dup"] = False
                        for ___dup in __intersect:
                            intersect_all_res[__comp_str]["dups"].append({
                                "res": ___dup, "margin": _margin,
                                "start_left": [i["start"] for i in _sample_res_str_2_loc[__res_idx_1][___dup]],
                                "start_right": [i["start"] for i in _sample_res_str_2_loc[__res_idx_2][___dup]]
                            })

        print("All Intersections Calculated")
        return intersect_all_res

    def check(self, show_dup: bool = False):
        intersect_res = self._search_all_possible_dup()

        if show_dup:
            for _comp_str, _comp_res in intersect_res.items():
                if _comp_res["no_dup"] is True:
                    print("[%s]\tNO Duplicates" % _comp_str)
                else:
                    print("[%s]\t%d Duplicates" % (_comp_str, len(_comp_res["dups"])))
                    print("\t", _comp_res["dups"][0], "...")

        selection_comb = itertools.combinations(list(range(self.SEQ_CNT)), 3)
        selection_comb = list(selection_comb)
        selection_comb_all_ok = []
        for _slt_comb in selection_comb:
            _slt_comb_is_ok = True
            _slt_comb_all_to_check_pairs = itertools.combinations(_slt_comb, 2)
            for __to_check_pair in _slt_comb_all_to_check_pairs:
                __comp_str = "%d-%d" % (__to_check_pair[0], __to_check_pair[1])
                if __comp_str not in intersect_res.keys():
                    __comp_str = "%d-%d" % (__to_check_pair[1], __to_check_pair[0])
                    if __comp_str not in intersect_res.keys():
                        raise KeyError("Intersection Results for %d & %d NOT FOUND"
                                       % (__to_check_pair[0], __to_check_pair[1]))

                if intersect_res[__comp_str]["no_dup"] is False:
                    _slt_comb_is_ok = False
                    break
            if _slt_comb_is_ok is True:
                selection_comb_all_ok.append(_slt_comb)

        print("All Possible No-Duplicate Selections: (altogether %d)" % len(selection_comb_all_ok))
        for _slt_comb in selection_comb_all_ok:
            print("\t", _slt_comb)


if "__main__" == __name__:
    # kwargs = {  # 2*5, 1 per bar
    #     "all_lv1_seq": [[1, 1, 0, 1, 1],
    #                     [1, 0, 1, 0, 1],
    #                     [1, 0, 0, 0, 1], ],
    #     "pt_per_bar": 1,
    #     "col_width": 100,
    # }
    # kwargs = {  # 2*4, 2 per bar
    #     "all_lv1_seq": [
    #         [1, 1, 0, 1],
    #         [1, 0, 1, 1],
    #         [1, 0, 0, 1],
    #         [1, 1, 1, 1],
    #     ],
    #     "pt_per_bar": 2,
    #     "col_width": 100,
    # }
    kwargs = {  # 2*2, 2 per bar
        "all_lv1_seq": [
            [0, 0],
            [0, 1],
            [1, 0],
            [1, 1],
        ],
        "pt_per_bar": 2,
        "col_width": 100,
    }

    obj = Lv1DuplicateCheck(**kwargs)
    obj.check()
