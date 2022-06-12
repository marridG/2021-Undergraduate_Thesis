_ALL_NUMS_BY_CATEGORY = {
    "speed": [  # cnt = 13
        5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120,  # speed limits ("GB") = 13
    ],
    "height": [  # cnt = 10 (2+8)
        3.5, 4.5,  # height limits ("GB") = 2
        1.8, 1.9, 2.0, 2.2, 2.5, 3, 3.2, 4,  # height limits (web) = 8
    ],
    "width": [  # cnt = 5 (1+4)
        2.5,  # width limits ("GB") = 1
        2.1, 2.2, 2.3, 2.4,  # width limits (web) = 4
    ],
    "weight": [  # cnt = 12 (0+12)
        2, 5, 7, 10, 13, 15, 20, 30, 40, 50, 55, 60,  # weight limits (web) = 12
    ],
}
ALL_SIGNS_BY_CATEGORY = {  # cnt = 198 (67+102+29)
    "warning": [  # cnt = 67 (67+0)
        "w1", "w2", "w3", "w4", "w5", "w6", "w7", "w8", "w9", "w10",
        "w11", "w12", "w13", "w14", "w15", "w16", "w17", "w18", "w19", "w20",
        "w21", "w22", "w23", "w24", "w25", "w26", "w27", "w28", "w29", "w30",
        "w31", "w32", "w33", "w34", "w35", "w36", "w37", "w38", "w39", "w40",
        "w41", "w42", "w43", "w44", "w45", "w46", "w47", "w48", "w49", "w50",
        "w51", "w52", "w53", "w54", "w55", "w56", "w57", "w58", "w59", "w60",
        "w61", "w62", "w63", "w64", "w65", "w66", "w67",  # cnt = 67
        # cnt = 0
    ],
    "prohibitory": [  # cnt = 102 (37+65)
                       "p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8", "p9", "p10",
                       "p11", "p12", "p13", "p14", "p15", "p16", "p17", "p18", "p19", "p20",
                       "p21", "p22", "p23", "p24", "p25", "p26", "p27", "p28",
                       "pd", "pc", "pn", "pnl", "ps", "pg", "pb", "pe", "pne",  # cnt = 37 (28+9)
                   ] +
                   # cnt = 24 (2*12)
                   [_type[:-1] + str(_num) for _type in ["pm*", "pa*", ] for _num in _ALL_NUMS_BY_CATEGORY["weight"]] +
                   # cnt = 26 (2*13)
                   [_type[:-1] + str(_num) for _type in ["pl*", "pr*", ] for _num in _ALL_NUMS_BY_CATEGORY["speed"]] +
                   # cnt = 10 (1*10)
                   [_type[:-1] + str(_num) for _type in ["ph*", ] for _num in _ALL_NUMS_BY_CATEGORY["height"]] +
                   # cnt = 5 (1*5)
                   [_type[:-1] + str(_num) for _type in ["pw*", ] for _num in _ALL_NUMS_BY_CATEGORY["width"]],

    "mandatory": [  # cnt = 29 (16+13)
                     "i1", "i2", "i3", "i4", "i5", "i6", "i7", "i8", "i9", "i10",
                     "i11", "i12", "i13", "i14", "i15", "ip",  # cnt = 16 (15+1)
                 ] +
                 # cnt = 13 (1*13)
                 [_type[:-1] + str(_num) for _type in ["il*"] for _num in _ALL_NUMS_BY_CATEGORY["speed"]],
}

CNT_SIGNS = 198
CNT_CATEGORY_1 = len(ALL_SIGNS_BY_CATEGORY.keys())
CNT_CATEGORY_2 = max(len(_cat_1_items) for _cat_1_items in ALL_SIGNS_BY_CATEGORY.values())
CNT_CATEGORY_2_BY_CAT = {_cat: len(_cat_signs) for _cat, _cat_signs in ALL_SIGNS_BY_CATEGORY.items()}

if "__main__" == __name__:
    pass
