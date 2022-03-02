import numpy as np


def degree_2_radian(deg: float) -> float:
    return (deg / 180.) * np.pi


def radian_2_degree(rad: float) -> float:
    return (rad / np.pi) * 180.
