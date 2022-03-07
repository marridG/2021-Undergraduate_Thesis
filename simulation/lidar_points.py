from typing import List
import numpy as np

from visualization import VisualCanvas
import utils

HORI_HZ_2_RESOL = {5: 0.1, 10: 0.2, 20: 0.4}  # in Hz -> degrees
VERT_16_TYPE_2_RESOL = 2  # 16-channel, in degrees


def dist_2_margin(dist: int, angle_resol: float) -> int:
    """
    calculate the HORIZONTAL margin of two adjacent LiDAR points at the given distance
    :param dist:                given distance from the point to the LiDAR (not projection) (in METER's)
    :param angle_resol:         given angle resolution of the LiDAR (in DEGREE's)
    :return:                    horizontal margin as a CEIL-ed int (in MILLI-METERS)
    """
    resol = utils.degree_2_radian(deg=angle_resol)  # in radians
    res = dist * np.tan(resol)  # in meters
    res *= 100. * 10.  # in milli-meters
    res = np.ceil(res).astype(int)
    return res


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
        _board_ref = np.where(np.all(points == self.canvas_obj.color_board, axis=-1))  # <tuple> of 3 np.ndarray
        res[_board_ref[:-1]] = 1
        # print(res)

        # assign BINARY-0 to all points of the shaded parts on the board
        _dark_ref = np.where(np.all(points == self.canvas_obj.color_dark, axis=-1))  # <tuple> of 3 np.ndarray
        res[_dark_ref[:-1]] = 0
        # print(res)

        return res

    def sample_at_distance(self, dist: int) -> List[np.ndarray]:
        """
        Sample the whole canvas at the given distance
        :param dist:                given distance (in METER's)
        :return:                    <list>of<np.ndarray>, containing (height//vert_margin)*(width//hori_margin) elem,
                                        each as a binary representation of the sampled points:
                                        nan=off_board_pts, 1=on_board_pts, 0=dark_on_board_pts
        """
        hori_margin = dist_2_margin(dist=dist, angle_resol=self.hori_angle_resol)  # in mm
        vert_margin = dist_2_margin(dist=dist, angle_resol=self.vert_angle_resol)  # in mm

        res = []
        for _height_start in range(0, vert_margin):  # vertically, each idx=1mm
            for _width_start in range(0, hori_margin):  # horizontally, each idx=1mm
                # do sampling
                __pts = self.canvas_obj.canvas[_height_start::vert_margin, _width_start::hori_margin, :]
                # print(vert_margin, hori_margin, __pts.shape)

                # convert RGB to binary representation
                __pts_binary = self._rgb_2_binary(points=__pts)
                # print(__pts_binary.shape)

                res.append(__pts_binary)

        return res


if "__main__" == __name__:
    c_obj = VisualCanvas(height=130, width=130)
    obj = LiDARSampling(canvas=c_obj)
    a = obj.sample_at_distance(dist=10)
    # print(a)
    # c_obj.render().show()
