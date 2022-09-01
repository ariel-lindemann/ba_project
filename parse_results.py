from points_utils import zx_positions_centroids


def parse_result_position(result, segment_position):
    position = result.position
    position_center = zx_positions_centroids([position])[0]
    # determine position on the image (segment postion being the UL corner of the segment)
    x = position_center[0] + segment_position[0]
    y = position_center[1] + segment_position[1]

    return (x, y)
