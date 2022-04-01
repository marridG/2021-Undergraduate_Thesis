ALL_SIGNS_BY_CATEGORY = {  # cnt = 127
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
ALL_NUMS = [
    5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120,  # speed limits
    3.5, 4.5,  # height limits ("GB")
    1.8, 1.9, 2.0, 2.2, 2.5, 3, 3.2, 4,  # height limits (web)
    2.5,  # width limits ("GB")
    2.2, 2.3, 2.4,  # weight limits (web)
    2, 5, 7, 10, 13, 15, 20, 30, 40, 50, 55, 60,  # weight limits (web)
]

CNT_SIGNS = 127
CNT_CATEGORY_1 = len(ALL_SIGNS_BY_CATEGORY.keys())
CNT_CATEGORY_2 = max(len(_cat_1_items) for _cat_1_items in ALL_SIGNS_BY_CATEGORY.values())
CNT_NUM = len(set(ALL_NUMS))

# limits of draft version of numbers on traffic signs
MAXIMUM_SIGN_NUMBER = 200
MAXIMUM_SIGN_NUMBER_FRACTIONAL_DIGITS = 1
