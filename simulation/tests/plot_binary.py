import numpy as np
from matplotlib import pyplot as plt
from PIL import Image

data = np.load("sample.npy")

image = np.full((data.shape[0], data.shape[1], 3), 255, dtype=int)
# image[np.where(-1 == data), :] = (0, 0, 0)  # black
# image[np.where(0 == data), :] = (0, 0, 0)  # black
image[np.where(1 == data)] = (0, 0, 0)  # white

im = Image.fromarray(np.uint8(image))
# im.show()
im.save("sample_binarized.png")
print()
