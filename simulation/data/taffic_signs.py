from typing import *
import random
import math


class TrafficSignsData:
    __ALL_SIGNS_BY_CATEGORY = {  # cnt = 127
        "warning": {  # cnt = 67
            "fixed":
                ["w1", "w2", "w3", "w4", "w5", "w6", "w7", "w8", "w9", "w10",
                 "w11", "w12", "w13", "w14", "w15", "w16", "w17", "w18", "w19", "w20",
                 "w21", "w22", "w23", "w24", "w25", "w26", "w27", "w28", "w29", "w30",
                 "w31", "w32", "w33", "w34", "w35", "w36", "w37", "w38", "w39", "w40",
                 "w41", "w42", "w43", "w44", "w45", "w46", "w47", "w48", "w49", "w50",
                 "w51", "w52", "w53", "w54", "w55", "w56", "w57", "w58", "w59", "w60",
                 "w61", "w62", "w63", "w64", "w65", "w66", "w67", ],  # cnt = 67
            "family": [],  # cnt = 0
        },
        "prohibitory": {  # cnt = 43
            "fixed": ["p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8", "p9", "p10",
                      "p11", "p12", "p13", "p14", "p15", "p16", "p17", "p18", "p19", "p20",
                      "p21", "p22", "p23", "p24", "p25", "p26", "p27", "p28",
                      "pd", "pc", "pn", "pnl", "ps", "pg", "pb", "pe", "pne", ],  # cnt = 37 (28+9)
            "family": ["pm*", "pa*", "pl*", "pr*", "ph*", "pw*", ],  # cnt = 6
        },
        "mandatory": {  # cnt = 17
            "fixed": ["i1", "i2", "i3", "i4", "i5", "i6", "i7", "i8", "i9", "i10",
                      "i11", "i12", "i13", "i14", "i15", "ip", ],  # cnt = 16 (15+1)
            "family": ["il*", ],  # cnt = 1
        }
    }
    __ALL_NUMS = [
        5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120,  # speed limits
        3.5, 4.5,  # height limits ("GB")
        1.8, 1.9, 2.0, 2.2, 2.5, 3, 3.2, 4,  # height limits (web)
        2.5,  # width limits ("GB")
        2.2, 2.3, 2.4,  # weight limits (web)
        2, 5, 7, 10, 13, 15, 20, 30, 40, 50, 55, 60,  # weight limits (web)
    ]
    __MAXIMUM_SIGN_NUMBER = 200
    __MAXIMUM_SIGN_NUMBER_FRACTIONAL_DIGITS = 1

    def __init__(self):
        print("Initializing Data ...")
        print("\tRaw Acquired")

        # ==1== assign each fixed/"family representative" sign a global index,
        #   & create bi-directional reference for category & fixed/family & sign
        self.cnt_sign = 0
        self.cnt_category = 0
        self.cnt_nums = 0
        self._num_idx_2_float = {}
        self._num_float_2_idx = {}
        self._ff_str_2_idx = {"fixed": 0, "family": 1}  # will not be changed later
        self._ff_idx_2_str = {0: "fixed", 1: "family"}  # will not be changed later
        self._category_str_2_idx = {}
        self._category_idx_2_str = {}
        #   [sign] global idx to str:
        #       {idx: {"ref": [key_refs,], "val": sign_str, "is_family": bool}, ...}
        #   e.g. { 0: {"ref": ["warning", "fixed", 0], "val": "w1", "is_family": False}, ... }
        self._sign_idx_2_str = {}
        #   [sign] str to global idx:
        #       {sign_str: {"ref_idx": [category_idx, sub_idx], "idx": idx} ...}
        #   e.g. { "pm*": {"ref_idx": [1, 35], "idx": 102}, ... }
        self._sign_str_2_idx = {}

        # (alert: sensitive to NAMEs of fixed/family changes)
        self._init_build_reference()

        assert 127 == self.cnt_sign
        assert 3 == self.cnt_category
        print("\tBi-Directional Reference Built")

        # ==2== build ranges of the global indices of signs, so as to effectively do sampling
        self._sample_range = {}  # {"all":[], 0/1/2: {"all"/0/1: []}}
        self._init_build_sample_range()
        print("=== DONE ===")

    def _init_build_reference(self):
        """[NOT TESTED BUT SHOULD B BE CORRECT]"""
        # (alert: sensitive to NAMEs of fixed/family changes)

        print("\t\tBuilding Bi-Directional Reference for All Traffic Signs...")
        for _cat, _items in self.__ALL_SIGNS_BY_CATEGORY.items():  # e.g., "warning", {"fixed": [], "family": [] }
            # add category bi-directional reference
            self._category_idx_2_str[self.cnt_category] = _cat
            self._category_str_2_idx[_cat] = self.cnt_category
            __fixed_cnt_base = len(_items["fixed"])  # to calculate the real indices of a sign in a category
            for __rep, __items in _items.items():  # e.g. "family", []
                for ___sign_idx, ___sign_item in enumerate(__items):
                    ___sign_is_family = False if "fixed" == __rep else True
                    # add sign bi-directional reference
                    self._sign_idx_2_str[self.cnt_sign] = {
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

        print("\t\t\t=== Done ===")

        print("\t\tBuilding Bi-Directional Reference for All Possible Numbers...")
        _added_nums = set()
        for _num in self.__ALL_NUMS:
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
                for ___sign_str in self.__ALL_SIGNS_BY_CATEGORY[_cat_str][__ff_str]:
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

        res_str = self._sign_idx_2_str[res_idx]["val"]

        # parse the return data
        _res_is_family = self._sign_str_2_idx[res_str]["is_family"]
        _res_encoding = self._sign_str_2_idx[res_str]["ref_idx"]
        res = {"str": res_str,
               "num": None if not _res_is_family else self._get_random_sign_number()[0],
               "encoding": {"category": _res_encoding[0], "idx": _res_encoding[1]}}
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
    print(obj.get_sample())  # {'str': 'w36', 'num': None, 'encoding': {'category': 0, 'idx': 35}}
    print(obj.get_sample(category_idx=1))  # {'str': 'pb', 'num': None, 'encoding': {'category': 1, 'idx': 34}}
    print(obj.get_sample(fixed_or_family=1))  # {'str': 'pr*', 'num': 8, 'encoding': {'category': 1, 'idx': 40}}
    print(obj.get_sample(category_idx=1, fixed_or_family=1))  # {'str': 'pa*', 'num': 3, '..': {'.': 1, 'idx': 38}}
    print(obj.get_sample(category_idx=0, fixed_or_family=1))  # None

    print()
