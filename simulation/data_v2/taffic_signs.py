from typing import List, Dict, Optional, Union, Tuple
import random
import math

from data_v2 import constants


class TrafficSignsData:
    def __init__(self):
        print("Initializing Data ...")
        print("\tRaw Acquired")

        # ==1== assign each fixed/"family representative" sign a global index,
        #   & create bi-directional reference for category & fixed/family & sign
        # (1) counts
        self.cnt_sign = 0
        self.cnt_category = 0
        # (4) category_1 ref
        self._category_str_2_idx = {}
        self._category_idx_2_str = {}
        # (5) full sign info ref
        #   [sign] global idx to local info:
        #       {idx: {"ref": [key_refs,], "val": sign_str, }, ...}
        #   e.g. { 0: {"ref": [0, 1], "val": "w2"}, ... }
        self._sign_global_idx_2_local_info = {}
        self._sign_local_idx_2_global_idx = {}

        # (alert: sensitive to NAMEs of fixed/family changes)
        self._init_build_reference()

        assert constants.CNT_SIGNS == self.cnt_sign
        assert constants.CNT_CATEGORY_1 == self.cnt_category
        print("\tBi-Directional Reference Built")

        # ==2== build ranges of the global indices of signs, so as to effectively do sampling
        self._sample_range = {}  # {"all":[], 0/1/2: {"all"/0/1: []}}
        self._init_build_sample_range()
        print("=== DONE ===")

    def _init_build_reference(self):
        """[NOT TESTED BUT SHOULD B BE CORRECT]"""
        # (alert: sensitive to NAMEs of fixed/family changes)

        print("\t\tBuilding Bi-Directional Reference for All Traffic Signs...")
        for _cat, _items in constants.ALL_SIGNS_BY_CATEGORY.items():  # e.g., "warning", []
            # add category bi-directional reference
            self._category_idx_2_str[self.cnt_category] = _cat
            self._category_str_2_idx[_cat] = self.cnt_category
            self._sign_local_idx_2_global_idx[self.cnt_category] = {}
            for __sign_idx, __sign in enumerate(_items):
                # add sign bi-directional reference
                self._sign_global_idx_2_local_info[self.cnt_sign] = {
                    "ref": [self.cnt_category, __sign_idx], "val": __sign,
                }
                self._sign_local_idx_2_global_idx[self.cnt_category][__sign_idx] = self.cnt_sign
                self.cnt_sign += 1
            self.cnt_category += 1

        print("\t\t\t=== Done ===")

    def _init_build_sample_range(self):
        """
        [TESTED]
        """
        print("\t\tBuilding Sample Ranges ...")

        # res: {"N/A"/0/1/2: []}
        # init template
        for _cat_idx in ["N/A"] + list(self._category_idx_2_str.keys()):
            self._sample_range[_cat_idx] = []

        self._sample_range["N/A"] = list(range(self.cnt_sign))
        for _cat_idx, _cat_str in self._category_idx_2_str.items():
            for __sign_idx in range(len(constants.ALL_SIGNS_BY_CATEGORY[_cat_str])):
                __sign_global_idx = self._sign_local_idx_2_global_idx[_cat_idx][__sign_idx]
                self._sample_range[_cat_idx].append(__sign_global_idx)

        print("\t\t\t=== DONE ===")

    def _get_sample_idx_range(self, category_idx: Optional[int] = None, sign_idx: Optional[int] = None) \
            -> List[int]:
        """
        [TESTED] Get the global indices of all the possible signs, w.r.t. the specified limitations
        :param category_idx:            only specify to limit the category, 0/1/2 for warning/prohibitory/mandatory
        :param sign_idx:                only specify to limit the local idx of the sign
        :return:                        <list>of<int> (possibly be an empty one)
        """
        # ==1== if category IS specified
        if category_idx is not None:
            _all_signs_this_cat = constants.ALL_SIGNS_BY_CATEGORY[self._category_idx_2_str[category_idx]]
            # sign specified  ==> choose the specified sign
            if sign_idx is not None:
                assert 0 <= sign_idx <= len(_all_signs_this_cat) - 1
                return [self._sign_local_idx_2_global_idx[category_idx][sign_idx]]
            # sign NOT specified  ==> choose from specified range
            else:
                return self._sample_range[category_idx]
        # ==2== if category is NOT specified, choose from all signs, by their global indices
        else:
            return self._sample_range["N/A"]

    def get_sample(self, category_idx: Optional[int] = None, sign_idx: Optional[int] = None) \
            -> None or Dict[str, Union[str, None, int, Dict[str, int]]]:
        """
        Get the encoding of a sample sign, w/wo limiting the category and/or whether is fixed or family
        :param category_idx:            only specify to limit the category, 0/1/2 for warning/prohibitory/mandatory
        :param sign_idx:                only specify to limit the local idx of the sign
        :return:                        if NO sample, None;
                                        if sample exits, a <dict>, as,
                                            { "str": str_of_sign,
                                              "encoding": {"category": category_idx, "idx": idx_in_the_category}}
        """
        rand_range = self._get_sample_idx_range(category_idx=category_idx, sign_idx=sign_idx)
        try:
            res_global_idx = random.choice(rand_range)
        except IndexError:  # choosing from an empty list, i.e., NO possible samples
            return None

        res_local_info = self._sign_global_idx_2_local_info[res_global_idx]
        res_str = res_local_info["val"]
        _res_encoding = res_local_info["ref"]
        res = {"str": res_str,
               "encoding": {"category": _res_encoding[0], "idx": _res_encoding[1]}}
        return res

    def _get_cat_1_str_by_idx(self, cat_1_idx: int) -> None or str:
        if not (0 <= cat_1_idx <= constants.CNT_CATEGORY_1 - 1):
            return None

        res = self._category_idx_2_str[cat_1_idx]
        return res

    def get_sign_info_by_idx(self, cat_1_idx: Optional[int] = None,
                             cat_2_idx: Optional[int] = None) \
            -> None or Dict[str, str]:
        """
        Get sign info by category_1, category_2 (local ref) and/or num indices
        :param cat_1_idx:           [Optional, default as None] category_1 idx
        :param cat_2_idx:           [Optional, default as None] category_2 idx (local ref idx)
        :return:                    {"category_1"/"category_2": <str>, "is_complete": <bool>}
                                    where,
                                        empty <str> for unknown fields;
                                        "is_complete" indicates whether all fields are known
        """
        assert ((cat_1_idx is None) and (cat_2_idx is None)) is not True

        # extract all possible info, with single-field validation assured (any invalid idx will return None)
        res = {"category_1": "", "category_2": "", "is_complete": False}
        if cat_1_idx is not None:
            _cat_1_str = self._get_cat_1_str_by_idx(cat_1_idx=cat_1_idx)
            if _cat_1_str is None:
                return None
            _cat_1_all_signs = constants.ALL_SIGNS_BY_CATEGORY[_cat_1_str]
            res["category_1"] = _cat_1_str
            if cat_2_idx is not None:
                if 0 <= cat_2_idx <= len(_cat_1_all_signs) - 1:
                    _cat_2_str = _cat_1_all_signs[cat_2_idx]
                else:
                    return None
                res["category_2"] = _cat_2_str
                res["is_complete"] = True

        return res


if "__main__" == __name__:
    # === ALL TODO, ALL NOT TESTED ===
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
    print(obj.get_sample(sign_idx=1))  # {'str': 'pr*', 'num': 8, 'encoding': {'category': 1, 'idx': 40}}
    print(obj.get_sample(category_idx=1, sign_idx=1))  # {'str': 'pa*', 'num': 3, '..': {'.': 1, 'idx': 38}}
    print(obj.get_sample(category_idx=0, sign_idx=1))  # None
    print()

    print("===== Interpreting =====")
    print(obj.get_sign_info_by_idx(cat_1_idx=1))  # {'c1': 'proh', 'c2': '', 'num': '', 'comp': False}
    print(obj.get_sign_info_by_idx(cat_1_idx=-2))  # [invalid] None
    print(obj.get_sign_info_by_idx(cat_1_idx=3))  # [invalid] None
    print(obj.get_sign_info_by_idx(cat_2_idx=12))  # {'c1': 'warning', 'c2': 'w13', 'num': '', 'comp': True}
    print(obj.get_sign_info_by_idx(cat_2_idx=-2))  # [invalid] None
    print(obj.get_sign_info_by_idx(cat_2_idx=129))  # [invalid] None
    print(obj.get_sign_info_by_idx(cat_1_idx=0, cat_2_idx=3))  # {'c1': 'warning', 'c2': 'w4', 'num': '', 'comp': True}
    print(obj.get_sign_info_by_idx(cat_1_idx=1, cat_2_idx=106))  # {'c1': 'proh', 'c2': 'pl*', 'num': '', 'comp': False}
    print(obj.get_sign_info_by_idx(cat_1_idx=1, cat_2_idx=3))  # [invalid] None

    print()
