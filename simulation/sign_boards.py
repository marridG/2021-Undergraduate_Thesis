from typing import *
import numpy as np
import raster_geometry as rg
from matplotlib import pyplot as plt

from visualization import VisualCanvas


class TrafficSignBoard(VisualCanvas):
    def __init__(self, height: int = 30, width: int = 50):
        super().__init__(height, width)

    @staticmethod
    def full_triangle(a, b, c):
        # reference: [CC BY-SA 4.0] https://stackoverflow.com/a/61015383
        ab = rg.bresenham_line(a, b, endpoint=True)
        for x in set(ab):
            yield from rg.bresenham_line(c, x, endpoint=True)
        ac = rg.bresenham_line(a, c, endpoint=True)
        for x in set(ac):
            yield from rg.bresenham_line(b, x, endpoint=True)
        bc = rg.bresenham_line(b, c, endpoint=True)
        for x in set(bc):
            yield from rg.bresenham_line(a, x, endpoint=True)

    def _get_triangle_board(self, length: int, orientation: str = "center") -> np.ndarray:
        assert "center" == orientation

        center = (self.height // 2, self.width // 2)  # (height, width)
        _sqrt_3 = np.sqrt(3)
        top_middle = (round(center[0] - length / _sqrt_3), center[1])
        bottom_left = (round(center[0] + length / 2 / _sqrt_3), center[1] - length // 2)
        bottom_right = (round(center[0] + length / 2 / _sqrt_3), center[1] + length // 2)

        assert top_middle[0] >= 0, \
            "Top-Left Indices Out-Of-Range: (height, width)=(%d,%d) exceeds (0,-)" % (top_middle[0], top_middle[1])
        assert bottom_left[0] <= self.height - 1 and bottom_left[1] >= 0, \
            "Bottom-Left Indices Out-Of-Range: (height, width)=(%d,%d) exceeds (%d, %d)" \
            % (bottom_left[0], bottom_left[1], self.height - 1, 0)
        assert bottom_right[1] <= self.width - 1, \
            "Bottom-Right Indices Out-Of-Range: (height, width)=(%d,%d) exceeds (-, %d)" \
            % (bottom_right[0], bottom_right[1], self.width - 1)

        # draw a triangular mask in 2D, reference: [CC BY-SA 4.0] https://stackoverflow.com/a/61015383
        print("Calculating Points by Bresenham Algorithm ...", end="")
        coords = set(self.full_triangle(top_middle, bottom_left, bottom_right))
        # print(coords)
        tri_mask = rg.render_at((self.height, self.width), coords)
        tri_mask = tri_mask.astype(int)  # 0 for non-triangle points, 1 for triangle points
        print(" Done")
        # print(tri_mask)

        print("Drawing Triangle of length=%d, with Vertices at (%d,%d),(%d,%d),(%d,%d)" %
              (length, top_middle[0], top_middle[1], bottom_left[0], bottom_left[1], bottom_right[0], bottom_right[1]))
        canvas = np.full_like(self.canvas, -99, dtype=int)
        canvas[np.where(tri_mask > 0)] = self.color_board
        return canvas

    def _get_rectangle_board(self, height: int, width: int, orientation: str = "center") -> np.ndarray:
        assert "center" == orientation

        center = (self.height // 2, self.width // 2)  # (height, width)
        # top_left = (center[0] - height // 2 - int(0 == height % 2), center[1] - width // 2 - int(0 == width % 2))
        # bottom_right = (center[0] + height // 2 + int(0 == height % 2), center[1] + width // 2 + int(0 == width % 2))
        top_left = (center[0] - height // 2, center[1] - width // 2)
        bottom_right = (center[0] + height // 2, center[1] + width // 2)

        assert top_left[0] >= 0 and top_left[1] >= 0, \
            "Top-Left Indices Out-Of-Range: (height, width)=(%d,%d) !>= (0,0)" % (top_left[0], top_left[1])
        assert bottom_right[0] <= self.height and bottom_right[1] <= self.width, \
            "Bottom-Right Indices Out-Of-Range: (height, width)=(%d,%d) !<= (%d, %d)" \
            % (bottom_right[0], bottom_right[1], self.height, self.width)

        print("Drawing Rectangle of (height,width)=(%d,%d) at (%d,%d)~(%d,%d)"
              % (height, width, top_left[0], top_left[1], bottom_right[0], bottom_right[1]))
        canvas = np.full_like(self.canvas, -99, dtype=int)
        canvas[top_left[0]: bottom_right[0], top_left[1]:bottom_right[1], :] = self.color_board
        return canvas

    def _get_circle_board(self, radius: int, orientation: str = "center") -> np.ndarray:
        assert "center" == orientation

        center = (self.height // 2, self.width // 2)  # (height, width)

        # reference:
        #   draw a circle (stroke only): [CC BY-SA 4.0] https://stackoverflow.com/a/10032271
        #   [√] draw a circular mask: [CC BY-SA 4.0] https://stackoverflow.com/a/44874588
        y_grid, x_grid = np.ogrid[:self.height, :self.width]
        dist_from_center = np.sqrt((x_grid - center[0]) ** 2 + (y_grid - center[1]) ** 2)
        cir_mask = dist_from_center <= radius

        print("Drawing Circle of radius=%d" % radius)
        canvas = np.full_like(self.canvas, -99, dtype=int)
        canvas[np.where(cir_mask > 0)] = self.color_board
        return canvas

    def draw_sign_board(self, shape: str, orientation: str = "center",
                        tri_length: Optional[int] = None,
                        rect_height: Optional[int] = None, rect_width: Optional[int] = None,
                        cir_radius: Optional[int] = None) \
            -> None:
        assert shape in ["triangle", "rectangle", "circle", "tri", "rect", "cir"]
        assert orientation in ["center"]

        if shape.startswith("tri"):
            assert tri_length is not None
            shape_data = self._get_triangle_board(length=tri_length, orientation=orientation)
        elif shape.startswith("rect"):
            assert rect_height is not None and rect_width is not None
            shape_data = self._get_rectangle_board(height=rect_height, width=rect_width, orientation=orientation)
        elif shape.startswith("cir"):
            assert cir_radius is not None
            shape_data = self._get_circle_board(radius=cir_radius, orientation=orientation)
        else:
            raise TypeError("Undefined Shape: %s" % shape)

        self.draw_above(layer_data=shape_data)
        # plt.imshow(shape_data)
        # plt.show()

        return

    def place_encoding(self, encoding: np.ndarray) -> None:
        # === DRAFT VERSION === almost the same as drawing a rectangle
        height, width = encoding.shape

        # translate binary representation to RGB colors
        encoding_color = np.full((encoding.shape[0], encoding.shape[1], 3), -99, dtype=int)
        encoding_color[np.where(encoding == 0)] = self.color_dark
        encoding_color[np.where(encoding == 1)] = self.color_board

        center = (self.height // 2, self.width // 2)  # (height, width)
        # top_left = (center[0] - height // 2 - int(0 == height % 2), center[1] - width // 2 - int(0 == width % 2))
        # bottom_right = (center[0] + height // 2 + int(0 == height % 2), center[1] + width // 2 + int(0 == width % 2))
        top_left = (center[0] - height // 2, center[1] - width // 2)
        bottom_right = (top_left[0] + height, top_left[1] + width)

        assert top_left[0] >= 0 and top_left[1] >= 0, \
            "Top-Left Indices Out-Of-Range: (height, width)=(%d,%d) !>= (0,0)" % (top_left[0], top_left[1])
        assert bottom_right[0] <= self.height and bottom_right[1] <= self.width, \
            "Bottom-Right Indices Out-Of-Range: (height, width)=(%d,%d) !<= (%d, %d)" \
            % (bottom_right[0], bottom_right[1], self.height, self.width)

        # print("Drawing Rectangle of (height,width)=(%d,%d) at (%d,%d)~(%d,%d)"
        #       % (height, width, top_left[0], top_left[1], bottom_right[0], bottom_right[1]))
        self.canvas[top_left[0]: bottom_right[0], top_left[1]:bottom_right[1], :] = encoding_color


if "__main__" == __name__:
    # test draw rectangle
    obj = TrafficSignBoard(6, 8)
    obj.draw_sign_board(shape="rectangle", rect_height=4, rect_width=4)
    obj.render().show()

    # test draw triangle
    obj = TrafficSignBoard(10, 10)
    obj.draw_sign_board(shape="triangle", tri_length=8)
    obj.render().show()

    # test draw triangle
    obj = TrafficSignBoard(10, 10)
    obj.draw_sign_board(shape="circle", cir_radius=4)
    obj.render().show()
