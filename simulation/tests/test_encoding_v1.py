from data.taffic_signs import TrafficSignsData
from sign_boards import TrafficSignBoard
from lidar_points import LiDARSampling
from encoding_v1.encode_v1 import encode
import utils

# sample a traffic sign
data_obj = TrafficSignsData()
data_sample = data_obj.get_sample(fixed_or_family=1)
print(data_sample)

# encode the sampled traffic sign
data_sample_encoding = encode(sample=data_sample)
print(data_sample_encoding)
data_sample_raw_bar = utils.encoding_2_raw_bar(encoding=data_sample_encoding, elem_height=400, elem_width=100)

# test draw rectangle
sign_board_obj = TrafficSignBoard(1300, 1300)
sign_board_obj.draw_sign_board(shape="rectangle", rect_height=1200, rect_width=1200)

sign_board_obj.place_encoding(encoding=data_sample_raw_bar)
# sign_board_obj.render().show()
sign_board_obj.render().savefig("./canvas_v1.png")

# sample points on the canvas
pt_sample_obj = LiDARSampling(canvas=sign_board_obj, vert_angle_resol=0.33, hori_angle_resol=0.1)
sample_res = pt_sample_obj.sample_at_distance(dist=50)
# print(sample_res)

print()
