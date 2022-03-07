# from sign_boards import TrafficSignBoard
# from visualization import VisualCanvas
#
# obj = TrafficSignBoard()
# print(type(obj))
# print(isinstance(obj, VisualCanvas))


from data.taffic_signs import TrafficSignsData
from encoding_v1 import encode

obj = TrafficSignsData()
s = obj.get_sample(fixed_or_family=1)
print(s)
print(encode.encode(sample=s))
