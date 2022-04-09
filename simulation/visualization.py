import numpy as np
from matplotlib import pyplot as plt


class VisualCanvas:
    def __init__(self, height: int = 30, width: int = 50):
        self.height = height  # representing the VERTICAL height in milli-meters
        self.width = width  # representing the horizontal width in milli-meters

        self.color_unfilled = (255, 255, 255)  # white
        self.color_board = (0, 255, 0)  # lime
        # self.color_bright = (255, 0, 0)  # red  # REMOVED: should be identical to that of the board
        self.color_dark = (0, 0, 255)  # blue

        self.canvas = np.full((height, width, 3), self.color_unfilled, dtype=int)  # RGB
        self.canvas_layers = [
            np.full_like(self.canvas, True, dtype=bool)
        ]  # values of each layer are either True or False, acting like a mask
        print("Canvas Initialized with Color RGB =", self.color_unfilled,
              "and Shape (height, width, channel) =", self.canvas.shape)

    def draw_above(self, layer_data: np.ndarray) -> None:
        """
        Draw the given image data on the canvas (only the non-zero pixels of the given image)
        :param layer_data:                  input image to draw above the canvas (-99 for all unfilled pixels)
        """
        assert layer_data.shape == (self.height, self.width, 3)
        assert np.max(layer_data) <= 255 and np.min(layer_data) + 99 >= 0  # note, -99 for unfilled pixels

        layer_data = layer_data.astype(int)

        _layer_filled_ref = np.where(layer_data >= 0)
        # print(_layer_filled_ref[0].shape, _layer_filled_ref[1].shape, _layer_filled_ref[2].shape)
        self.canvas[_layer_filled_ref] = layer_data[_layer_filled_ref]
        # print(self.canvas[_layer_filled_ref].shape)
        # print(self.canvas.shape)
        # print(self.canvas)

        # construct layer mask
        mask = np.full_like(self.canvas, False, dtype=bool)
        mask[_layer_filled_ref] = True
        self.canvas_layers.append(mask)

    def get_canvas_data(self) -> np.ndarray:
        return self.canvas

    def render(self) -> plt:
        plt.imshow(self.canvas)
        plt.xticks([]), plt.yticks([])
        # plt.xlim(0, self.canvas.shape[1])
        # plt.ylim(0, self.canvas.shape[0])
        return plt


if "__main__" == __name__:
    obj = VisualCanvas(300, 500)
    print(obj.canvas.shape)
    # p = obj.render()
    # p.show()
    print()
