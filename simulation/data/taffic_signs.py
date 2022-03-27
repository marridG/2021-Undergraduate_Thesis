from typing import List, Dict, Optional, Union, Tuple
import random
import math

from data import constants


class TrafficSignsData:
    def __init__(self):
        print("Initializing Data ...")
        print("\tRaw Acquired")

        # ==1== assign each fixed/"family representative" sign a global index,
        #   & create bi-directional reference for category & fixed/family & sign
        # (1) counts
        self.cnt_sign = 0
        self.cnt_category = 0
        self.cnt_nums = 0
        # (2) num refs
        self._num_idx_2_float = {}
        self._num_float_2_idx = {}
        # (3) family str refs
        self._ff_str_2_idx = {"fixed": 0, "family": 1}  # will not be changed later
        self._ff_idx_2_str = {0: "fixed", 1: "family"}  # will not be changed later
        # (4) category_1 ref
        self._category_str_2_idx = {}
        self._category_idx_2_str = {}
        self._category_str_2_have_family = {}
        # (5) full sign info ref (w.r.t. GLOBAL IDX)
        #   [sign] global idx to str:
        #       {idx: {"ref": [key_refs,], "val": sign_str, "is_family": bool}, ...}
        #   e.g. { 0: {"ref": ["warning", "fixed", 0], "val": "w1", "is_family": False}, ... }
        self._sign_global_idx_2_str = {}
        self._sign_local_idx_2_global_idx = {}
        #   [sign] str to local_ref_idx & global idx:
        #       {sign_str: {"ref_idx": [category_idx, sub_idx], "idx": idx} ...}
        #   e.g. { "pm*": {"ref_idx": [1, 35], "idx": 102}, ... }
        self._sign_str_2_idx = {}

        # (alert: sensitive to NAMEs of fixed/family changes)
        self._init_build_reference()

        assert constants.CNT_SIGNS == self.cnt_sign
        assert constants.CNT_CATEGORY_1 == self.cnt_category
        assert constants.CNT_NUM == self.cnt_nums
        print("\tBi-Directional Reference Built")

        # ==2== build ranges of the global indices of signs, so as to effectively do sampling
        self._sample_range = {}  # {"all":[], 0/1/2: {"all"/0/1: []}}
        self._init_build_sample_range()
        print("=== DONE ===")

    def _init_build_reference(self):
        """[NOT TESTED BUT SHOULD B BE CORRECT]"""
        # (alert: sensitive to NAMEs of fixed/family changes)

        print("\t\tBuilding Bi-Directional Reference for All Traffic Signs...")
        for _cat, _items in constants.ALL_SIGNS_BY_CATEGORY.items():  # e.g., "warning", {"fixed": [], "family": [] }
            # add category bi-directional reference
            self._category_idx_2_str[self.cnt_category] = _cat
            self._category_str_2_have_family[_cat] = False if 0 == len(_items["family"]) else True
            self._category_str_2_idx[_cat] = self.cnt_category
            __fixed_cnt_base = len(_items["fixed"])  # to calculate the real indices of a sign in a category
            for __rep, __items in _items.items():  # e.g. ("family", []) or ("fixed", ["w1", "w2", ...])
                for ___sign_idx, ___sign_item in enumerate(__items):
                    ___sign_is_family = False if "fixed" == __rep else True
                    # add sign bi-directional reference
                    self._sign_global_idx_2_str[self.cnt_sign] = {
                        "ref": [_cat, __rep, ___sign_idx], "val": ___sign_item,
                        "is_family": ___sign_is_family
                    }
                    ___sign_real_idx = ___sign_idx if "fixed" == __rep else ___sign_idx + __fixed_cnt_base
                    self._sign_str_2_idx[___sign_item] = {
                        "ref_idx": [self.cnt_category, ___sign_real_idx], "idx": self.cnt_sign,
                        "is_family": ___sign_is_family
                    }
                    self.cnt_sign += 1
            self.cnt_category += 1

        self._sign_local_idx_2_global_idx = {i: {} for i in range(self.cnt_category)}
        for _sign_gbl_idx in range(self.cnt_sign):
            _sign_str = self._sign_global_idx_2_str[_sign_gbl_idx]["val"]
            _sign_ref_idx = self._sign_str_2_idx[_sign_str]["ref_idx"]  # e.g. [0, 0] for global #0 "w1"
            _sign_cat_1_idx, _sign_cat_2_idx = _sign_ref_idx
            self._sign_local_idx_2_global_idx[_sign_cat_1_idx][_sign_cat_2_idx] = _sign_gbl_idx

        print("\t\t\t=== Done ===")

        print("\t\tBuilding Bi-Directional Reference for All Possible Numbers...")
        _added_nums = set()
        for _num in constants.ALL_NUMS:
            if _num in _added_nums:
                continue
            self._num_float_2_idx[_num] = self.cnt_nums
            self._num_idx_2_float[self.cnt_nums] = _num
            _added_nums.add(_num)
            self.cnt_nums += 1

        print("\t\t\t=== Done ===")

    def _init_build_sample_range(self):
        """
        [TESTED]
        """
        print("\t\tBuilding Sample Ranges ...")

        # res: {"N/A"/0/1/2: {"N/A"/0/1: []}}
        # init template
        for _cat_idx in ["N/A"] + list(self._category_idx_2_str.keys()):
            self._sample_range[_cat_idx] = {"N/A": []}
            for i in self._ff_idx_2_str.keys():
                self._sample_range[_cat_idx][i] = []

        self._sample_range["N/A"]["N/A"] = list(range(self.cnt_sign))
        for _cat_idx, _cat_str in self._category_idx_2_str.items():
            for __ff_idx, __ff_str in self._ff_idx_2_str.items():
                for ___sign_str in constants.ALL_SIGNS_BY_CATEGORY[_cat_str][__ff_str]:
                    ___sign_idx = self._sign_str_2_idx[___sign_str]["idx"]
                    self._sample_range["N/A"][__ff_idx].append(___sign_idx)
                    self._sample_range[_cat_idx]["N/A"].append(___sign_idx)
                    self._sample_range[_cat_idx][__ff_idx].append(___sign_idx)

        print("\t\t\t=== DONE ===")

    def _get_sample_idx_range(self, category_idx: Optional[int] = None, fixed_or_family: Optional[int] = None) \
            -> List[int]:
        """
        [TESTED] Get the global indices of all the possible signs, w.r.t. the specified limitations
        :param category_idx:            only specify to limit the category, 0/1/2 for warning/prohibitory/mandatory
        :param fixed_or_family:         only specify to limit whether is fixed/family, 0/1 for fixed/family
        :return:                        <list>of<int> (possibly be an empty one)
        """
        # ==1== if either category OR fixed/family IS specified
        #   ==> choose from specified range
        if category_idx is not None or fixed_or_family is not None:
            # category specified; fixed/family YES/NO specified
            if category_idx is not None:
                assert 0 <= category_idx <= self.cnt_category - 1
                if fixed_or_family is not None:  # fixed/family specified
                    assert fixed_or_family in self._ff_idx_2_str.keys()
                    return self._sample_range[category_idx][fixed_or_family]
                else:  # fixed/family NOT specified
                    return self._sample_range[category_idx]["N/A"]

            # category NOT specified; fixed/family specified
            if category_idx is None and fixed_or_family is not None:
                assert fixed_or_family in self._ff_idx_2_str.keys()
                return self._sample_range["N/A"][fixed_or_family]

        # ==2== if neither is specified, choose from all signs, by their global indices
        else:
            return self._sample_range["N/A"]["N/A"]

    def _get_random_sign_number(self) -> Tuple[int, float]:
        """
        Sample a random possible number on the traffic sign
        :return:            (1) index of the number; (2) exact number
        """
        # # "continuous"-like version of numbers
        # rand_val = random.random()  # [0, 1)
        # rand_val *= 1. * self.__MAXIMUM_SIGN_NUMBER
        # rand_val = round(rand_val)
        #
        # rand_frac = random.random()  # [0,1)
        # rand_frac = round(rand_frac, self.__MAXIMUM_SIGN_NUMBER_FRACTIONAL_DIGITS)
        #
        # return rand_val + rand_frac

        # "discrete"-like version of numbers
        rand_idx = random.random()  # [0,1)
        rand_idx *= 1. * self.cnt_nums
        rand_idx = int(rand_idx)
        rand_num = self._num_idx_2_float[rand_idx]

        return rand_idx, rand_num

    def get_sample(self, category_idx: Optional[int] = None, fixed_or_family: Optional[int] = None) \
            -> None or Dict[str, Union[str, None, int, Dict[str, int]]]:
        """
        Get the encoding of a sample sign, w/wo limiting the category and/or whether is fixed or family
        :param category_idx:            only specify to limit the category, 0/1/2 for warning/prohibitory/mandatory
        :param fixed_or_family:         only specify to limit whether is fixed/family, 0/1 for fixed/family
        :return:                        if NO sample, None;
                                        if sample exits, a <dict>, as,
                                            { "str": str_of_sign,
                                              "num": None if the sample is fixed, <float>random_number otherwise,
                                              "encoding": {
                                                "category": category_idx, "idx": idx_in_the_category}}
        """
        rand_range = self._get_sample_idx_range(category_idx=category_idx, fixed_or_family=fixed_or_family)
        try:
            res_idx = random.choice(rand_range)
        except IndexError:  # choosing from an empty list, i.e., NO possible samples
            return None

        res_str = self._sign_global_idx_2_str[res_idx]["val"]

        # parse the return data
        _res_is_family = self._sign_str_2_idx[res_str]["is_family"]
        _res_encoding = self._sign_str_2_idx[res_str]["ref_idx"]
        res = {"str": res_str,
               "num": None if not _res_is_family else self._get_random_sign_number()[0],
               "encoding": {"category": _res_encoding[0], "idx": _res_encoding[1]}}
        return res

    def _get_cat_1_str_by_idx(self, cat_1_idx: int) -> None or str:
        if not (0 <= cat_1_idx <= constants.CNT_CATEGORY_1 - 1):
            return None

        res = self._category_idx_2_str[cat_1_idx]
        return res

    def _get_cat_2_str_by_global_idx(self, cat_2_gbl_idx: int) -> None or str:
        # assert that such a sign exists (general)
        if not (0 <= cat_2_gbl_idx <= constants.CNT_SIGNS - 1):
            return None

        sign_info = self._sign_global_idx_2_str[cat_2_gbl_idx]
        res = sign_info["val"]
        return res

    def _get_cat_2_global_idx(self, cat_1_idx: int, cat_2_idx: int) -> None or int:
        try:
            res = self._sign_local_idx_2_global_idx[cat_1_idx][cat_2_idx]
            return res
        except KeyError:
            return None

    def _get_num_str_by_idx(self, num_idx: int) -> None or str:
        if not (0 <= num_idx <= constants.CNT_NUM - 1):
            return None

        res = self._num_idx_2_float[num_idx]  # <float> or <int>
        res = str(res)
        return res

    def get_sign_info_by_idx(self, cat_1_idx: Optional[int] = None,
                             cat_2_idx: Optional[int] = None,
                             num_idx: Optional[int] = None, ) \
            -> None or Dict[str, str]:
        """
        Get sign info by category_1, category_2 (local ref) and/or num indices
        :param cat_1_idx:           [Optional, default as None] category_1 idx
        :param cat_2_idx:           [Optional, default as None] category_2 idx (local ref idx)
        :param num_idx:             [Optional, default as None] num idx
        :return:                    {"category_1"/"category_2"/"num": <str>, "is_complete": <bool>}
                                    where,
                                        empty <str> for unknown fields;
                                        "is_complete" indicates whether all fields are known
        """
        assert ((cat_1_idx is None) and (cat_2_idx is None) and (num_idx is None)) is not True

        """
        # extract all possible info, with single-field validation assured (any invalid idx will return None)
        res = {"category_1": "", "category_2": "", "num": "", "is_complete": False}
        if cat_1_idx is not None:
            _cat_1_str = self._get_cat_1_str_by_idx(cat_1_idx=cat_1_idx)
            if _cat_1_str is None:
                return None
            res["category_1"] = _cat_1_str
        if cat_2_idx is not None:
            _cat_2_gbl_idx = self._get_cat_2_global_idx(cat_1_idx=cat_1_idx, cat_2_idx=cat_2_idx)
            _cat_2_str = self._get_cat_2_str_by_global_idx(cat_2_gbl_idx=_cat_2_gbl_idx)
            if _cat_2_str is None:
                return None
            res["category_2"] = _cat_2_str
        if num_idx is not None:
            _num_str = self._get_num_str_by_idx(num_idx=num_idx)
            if _num_str is None:
                return None
            res["num"] = _num_str
        # now: idx is not None <==> ""!=res[key]

        # needless to validate: cat_1; cat_2 (impossible); num;

        # validate the extracted sign info: category_1 <-> sign & sign <-> have_num_part
        #   (& possibly fill cat_1 res info if not filled, by cat_2 idx)
        #   (& insert is_complete info)
        #   covered: cat_1 + cat_2 + num; cat_1 + cat_2; cat_2 + num;
        if cat_2_idx is not None:
            sign_info = self._sign_global_idx_2_str[cat_2_idx]
            # validation: category_1 <-> sign
            if cat_1_idx is not None:
                if sign_info["ref"][0] != res["category_1"]:
                    return None
            # fill cat_1 info if unfilled
            else:
                res["category_1"] = sign_info["ref"][0]
            # validation: sign <-> have_num_part
            if num_idx is not None:
                if sign_info["is_family"] is False:
                    return None
            # insert is_complete info
            res["is_complete"] = ((sign_info["is_family"] is True) == (num_idx is not None))

        # now: idx is not None ==> ""!=res[key] BUT NOT INVERSELY! (since cat_2 ==> cat_1)

        # validate the extracted sign info: category_1 <-> have_num_part
        #   covered: cat_1 + num; === ALL COVERED ===
        if cat_2_idx is None and "" != res["category_1"] and "" != res["num"]:
            _have_family = self._category_str_2_have_family[res["category_1"]]
            if _have_family is False:
                return None
        """  # codes if cat_2_idx is global idx

        # extract all possible info, with single-field validation assured (any invalid idx will return None)
        res = {"category_1": "", "category_2": "", "num": "", "is_complete": False}
        if cat_1_idx is not None:
            _cat_1_str = self._get_cat_1_str_by_idx(cat_1_idx=cat_1_idx)
            if _cat_1_str is None:
                return None
            res["category_1"] = _cat_1_str
            if cat_2_idx is not None:
                _cat_2_gbl_idx = self._get_cat_2_global_idx(cat_1_idx=cat_1_idx, cat_2_idx=cat_2_idx)
                if _cat_2_gbl_idx is None:
                    return None
                _cat_2_str = self._get_cat_2_str_by_global_idx(cat_2_gbl_idx=_cat_2_gbl_idx)
                if _cat_2_str is None:
                    return None
                res["category_2"] = _cat_2_str
        if num_idx is not None:
            _num_str = self._get_num_str_by_idx(num_idx=num_idx)
            if _num_str is None:
                return None
            res["num"] = _num_str
        # now: idx is not None <==> ""!=res[key]

        # needless to validate: cat_1; cat_2 (impossible); num;

        # validate the extracted sign info: category_1 <-> sign & sign <-> have_num_part
        #   (& insert is_complete info)
        #   covered: cat_1 + cat_2 + num; cat_1 + cat_2; cat_2 + num (meaningless for cat_2, & thus <=);
        if cat_1_idx is not None and cat_2_idx is not None:
            cat_2_gbl_idx = self._get_cat_2_global_idx(cat_1_idx=cat_1_idx, cat_2_idx=cat_2_idx)
            if cat_2_gbl_idx is None:
                return None
            sign_info = self._sign_global_idx_2_str[cat_2_gbl_idx]
            # validation: category_1 <-> sign
            if sign_info["ref"][0] != res["category_1"]:
                return None
            # validation: sign <-> have_num_part
            if num_idx is not None:
                if sign_info["is_family"] is False:
                    return None
            # insert is_complete info
            res["is_complete"] = ((sign_info["is_family"] is True) == (num_idx is not None))

        # validate the extracted sign info: category_1 <-> have_num_part
        #   covered: cat_1 + num; === ALL COVERED ===
        if cat_2_idx is None and cat_1_idx is not None and num_idx is not None:
            _have_family = self._category_str_2_have_family[res["category_1"]]
            if _have_family is False:
                return None

        return res


if "__main__" == __name__:
    obj = TrafficSignsData()
    # print(len(obj._get_sample_idx_range(category_idx=None, fixed_or_family=None)))  # 127
    # print(len(obj._get_sample_idx_range(category_idx=None, fixed_or_family=0)))  # 120
    # print(len(obj._get_sample_idx_range(category_idx=None, fixed_or_family=1)))  # 7
    # print(len(obj._get_sample_idx_range(category_idx=0, fixed_or_family=None)))  # 67
    # print(len(obj._get_sample_idx_range(category_idx=0, fixed_or_family=0)))  # 67
    # print(len(obj._get_sample_idx_range(category_idx=0, fixed_or_family=1)))  # 0
    # print(len(obj._get_sample_idx_range(category_idx=1, fixed_or_family=None)))  # 43
    # print(len(obj._get_sample_idx_range(category_idx=1, fixed_or_family=0)))  # 37
    # print(len(obj._get_sample_idx_range(category_idx=1, fixed_or_family=1)))  # 6
    # print(len(obj._get_sample_idx_range(category_idx=2, fixed_or_family=None)))  # 17
    # print(len(obj._get_sample_idx_range(category_idx=2, fixed_or_family=0)))  # 16
    # print(len(obj._get_sample_idx_range(category_idx=2, fixed_or_family=1)))  # 1
    print("===== Sampling =====")
    print(obj.get_sample())  # {'str': 'w36', 'num': None, 'encoding': {'category': 0, 'idx': 35}}
    print(obj.get_sample(category_idx=1))  # {'str': 'pb', 'num': None, 'encoding': {'category': 1, 'idx': 34}}
    print(obj.get_sample(fixed_or_family=1))  # {'str': 'pr*', 'num': 8, 'encoding': {'category': 1, 'idx': 40}}
    print(obj.get_sample(category_idx=1, fixed_or_family=1))  # {'str': 'pa*', 'num': 3, '..': {'.': 1, 'idx': 38}}
    print(obj.get_sample(category_idx=0, fixed_or_family=1))  # None
    print()

    print("===== Interpreting =====")
    print(obj.get_sign_info_by_idx(cat_1_idx=1))  # {'c1': 'proh', 'c2': '', 'num': '', 'comp': False}
    print(obj.get_sign_info_by_idx(cat_1_idx=-2))  # [invalid] None
    print(obj.get_sign_info_by_idx(cat_1_idx=3))  # [invalid] None
    print(obj.get_sign_info_by_idx(cat_2_idx=12))  # {'c1': 'warning', 'c2': 'w13', 'num': '', 'comp': True}
    print(obj.get_sign_info_by_idx(cat_2_idx=-2))  # [invalid] None
    print(obj.get_sign_info_by_idx(cat_2_idx=129))  # [invalid] None
    print(obj.get_sign_info_by_idx(num_idx=15))  # {'c1': '', 'c2': '', 'num': '1.8', 'comp': False}
    print(obj.get_sign_info_by_idx(num_idx=-2))  # [invalid] None
    print(obj.get_sign_info_by_idx(num_idx=29))  # [invalid] None
    print(obj.get_sign_info_by_idx(cat_1_idx=0, cat_2_idx=3))  # {'c1': 'warning', 'c2': 'w4', 'num': '', 'comp': True}
    print(obj.get_sign_info_by_idx(cat_1_idx=1, cat_2_idx=106))  # {'c1': 'proh', 'c2': 'pl*', 'num': '', 'comp': False}
    print(obj.get_sign_info_by_idx(cat_1_idx=1, cat_2_idx=3))  # [invalid] None
    print(obj.get_sign_info_by_idx(cat_1_idx=1, num_idx=15))  # {'c1': 'proh', 'c2': '', 'num': '1.8', 'comp': False}
    print(obj.get_sign_info_by_idx(cat_1_idx=0, num_idx=15))  # [invalid] None
    print(obj.get_sign_info_by_idx(cat_2_idx=106, num_idx=15))  # {'c1': 'proh', 'c2': 'pl*', 'num': '1.8', 'cp': True}
    print(obj.get_sign_info_by_idx(cat_2_idx=102, num_idx=15))  # [invalid] None
    print(obj.get_sign_info_by_idx(cat_1_idx=1, cat_2_idx=106, num_idx=15))  # {1: 'p', 2: 'pl*', 'n': '1.8', 'c': T}
    print(obj.get_sign_info_by_idx(cat_1_idx=1, cat_2_idx=102, num_idx=15))  # [invalid] None
    print(obj.get_sign_info_by_idx(cat_1_idx=2, cat_2_idx=106, num_idx=15))  # [invalid] None

    print()
