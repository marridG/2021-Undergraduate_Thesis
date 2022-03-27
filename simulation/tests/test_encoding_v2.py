from data.taffic_signs import TrafficSignsData
from sign_boards import TrafficSignBoard
from lidar_points import LiDARSampling
from encoding_v2.encode_v2 import encode
from encoding_v2.decode_v2 import decode
import utils
from simulation.exceptions import *

# sample a traffic sign
data_obj = TrafficSignsData()
data_sample = data_obj.get_sample(fixed_or_family=1)
print(data_sample)

# encode the sampled traffic sign
data_sample_encoding = encode(sample=data_sample)
print(data_sample_encoding)
height, width = 400, 100  # milli-meters
data_sample_raw_bar = utils.encoding_2_raw_bar(encoding=data_sample_encoding,
                                               elem_height=height, elem_width=width)

# test draw rectangle
sign_board_obj = TrafficSignBoard(1300, 1300)
sign_board_obj.draw_sign_board(shape="rectangle", rect_height=1200, rect_width=1200)

sign_board_obj.place_encoding(encoding=data_sample_raw_bar)
# sign_board_obj.render().show()
sign_board_obj.render().savefig("./canvas_v2.png")

# sample points on the canvas
distance = 50  # meters
hori_angle_resol, vert_angle_resol = 0.1, 0.33
pt_sample_obj = LiDARSampling(canvas=sign_board_obj,
                              hori_angle_resol=hori_angle_resol, vert_angle_resol=vert_angle_resol)
sample_res, sample_res_loc = pt_sample_obj.sample_at_distance(dist=50)
# print(sample_res)

for _sample, _sample_loc in zip(sample_res, sample_res_loc):
    try:
        _sample_decoded, _sample_decoded_info = decode(
            sign_data_obj=data_obj,
            points=_sample,
            hori_margin=utils.dist_2_margin(dist=distance, angle_resol=hori_angle_resol),
            vert_margin=utils.dist_2_margin(dist=distance, angle_resol=vert_angle_resol),
            height=height, width=width,
            tolerable=True)
        print(_sample_decoded, _sample_decoded_info)
    except DecodeFailure as err:
        print("Decode Failed for Sample Loc (%d,%d): %s" % (_sample_loc["hori"], _sample_loc["vert"], str(err)))
        continue
print()
