# TODO move to different module?
import pattern_utils
import numpy as np
from agv_info import AGV_info


def create_corner_code(agv_info: AGV_info, corner):
    agv_info.corner = corner
    code = pattern_utils.create_code(agv_info)
    return code


def create_agv_template(agv_info: AGV_info):
    corners = ['UL', 'UR', 'LL', 'LR']
    corner_codes = {}

    for c in corners:
        c_code = create_corner_code(agv_info, c)
        corner_codes.update(c, c_code)

    length = agv_info.length
    width = agv_info.width

    template = np.array(shape=(length, width))

    # TODO find square positions
    # TODO account for measuring units (mm, pixels ?)
    # TODO draw squares
