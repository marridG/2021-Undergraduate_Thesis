from typing import List, Dict
import numpy as np

from visualization import VisualCanvas
import utils


class LiDARSampling:
    def __init__(self, canvas: VisualCanvas,
                 hori_angle_resol: float = 0.1, vert_angle_resol: float = 0.33):
        self.canvas_obj = canvas
        self.hori_angle_resol = hori_angle_resol
        self.vert_angle_resol = vert_angle_resol

    def _rgb_2_binary(self, points: np.ndarray) -> np.ndarray:
        """
        :param points:                  given array of sampled points, in shape (pt_cnt_in_height, pt_cnt_in_width, 3)
        :return:                        converted BINARY representation, in shape (pt_cnt_in_height, pt_cnt_in_width):
                                            nan=off_board_pts,
                                            1=on_board_pts,
                                            0=dark_on_board_pts
        """
        assert 3 == points.shape[2]  # points: shape (pt_cnt_in_height, pt_cnt_in_width, 3)

        res = np.full((points.shape[0], points.shape[1]), np.nan)

        # find (x,y) of given RGB: https://stackoverflow.com/a/12138972
        # note, direct np.where(arr==color) will fail, e.g.: (returns a non-empty tuple)
        # white = np.full((4,3,3),255)
        # np.where(white==(0,255,0))

        # assign BINARY-1 to all points of the board
        _board_ref = np.where(np.all(points == self.canvas_obj.color_board, axis=-1))  # <tuple> of 2 np.ndarray
        res[_board_ref] = 1
        # print(res)

        # assign BINARY-0 to all points of the shaded parts on the board
        _dark_ref = np.where(np.all(points == self.canvas_obj.color_dark, axis=-1))  # <tuple> of 2 np.ndarray
        res[_dark_ref] = 0
        # print(res)

        return res

    def sample_at_distance(self, dist: int, vert_step: int = 1, hori_step: int = 1) \
            -> (List[np.ndarray], List[Dict[str, int]]):
        """
        Sample the whole canvas at the given distance
        :param dist:                given distance (in METER's)
        :param vert_step:           step size of vertical sampling
        :param hori_step:           step size of horizontal sampling
        :return:                    (1) <list>of<np.ndarray>,
                                        containing (height//vert_margin)*(width//hori_margin) elements,
                                        each as a binary representation of the sampled points:
                                        nan=off_board_pts, 1=on_board_pts, 0=dark_on_board_pts
                                    (2) <list>of{"hori"/"vert": <int>},
                                        of the same length as that of the first returned <list>,
                                        where the i-th element is the starting location of the i-th sample,
                                        and the location settings are given in millimeters
        """
        hori_margin = utils.dist_2_margin(dist=dist, angle_resol=self.hori_angle_resol)  # in mm
        vert_margin = utils.dist_2_margin(dist=dist, angle_resol=self.vert_angle_resol)  # in mm

        print("Start Sampling at %dm, with Vertical/Horizontal Margin %d/%d mm ..." % (dist, vert_margin, hori_margin))
        res = []
        res_loc = []
        res_shape_min, res_shape_max = (self.canvas_obj.height, self.canvas_obj.width), (0, 0)
        for _height_start in range(0, vert_margin, vert_step):  # vertically, each idx=1mm
            for _width_start in range(0, hori_margin, hori_step):  # horizontally, each idx=1mm
                # do sampling
                __pts = self.canvas_obj.canvas[_height_start::vert_margin, _width_start::hori_margin, :]
                # print(vert_margin, hori_margin, __pts.shape)

                # convert RGB to binary representation
                __pts_binary = self._rgb_2_binary(points=__pts)
                # print(__pts_binary.shape)

                res.append(__pts_binary)
                res_loc.append({"hori": _height_start, "vert": _width_start})
                # update min/max shape
                res_shape_min = (min(res_shape_min[0], __pts_binary.shape[0]),
                                 min(res_shape_min[1], __pts_binary.shape[1]))
                res_shape_max = (max(res_shape_max[0], __pts_binary.shape[0]),
                                 max(res_shape_max[1], __pts_binary.shape[1]))

        print("=== DONE === with %d Groups of Sample Points, Shaped (%d,%d)~(%d,%d)"
              % (len(res), res_shape_min[0], res_shape_min[1], res_shape_max[0], res_shape_max[1]))
        return res, res_loc


if "__main__" == __name__:
    c_obj = VisualCanvas(height=130, width=130)
    obj = LiDARSampling(canvas=c_obj)
    a = obj.sample_at_distance(dist=10)
    # print(a)
    # c_obj.render().show()
