import os
import numpy as np


def load_data(file: str):
    assert os.path.exists(file)

    sequence = np.fromfile(file, dtype=np.float32)
    assert sequence.size == 4 * (sequence.size // 4)

    sequence = sequence.reshape(-1, 4)
    print("Point Cloud Loaded from File \"%s\":" % file, sequence.shape)

    return sequence
