import json


def json_to_agv_info(json_data, for_calibration=True):
    '''
    Convert a JSON representation into an `AGV_info` object

    Parameters
    ----------

    json_data:
        the `AGV_data` object in JSON form

    for_calibration: bool
        if the code is used for camera calibration, no corner information is given
    '''
    as_dict = json.loads(json_data)

    if for_calibration:
        return AGV_info(as_dict['length'], as_dict['width'], as_dict['height'], as_dict['raster_x'], as_dict['raster_y'], as_dict['serial_no'])
    else:
        return AGV_info(as_dict['length'], as_dict['width'], as_dict['height'], as_dict['raster_x'], as_dict['raster_y'], as_dict['serial_no'], as_dict['corner'])


class AGV_info:
    '''
    Informations related to the AGV

    length:
        Length of AGV in mm

    width:
        Width of AGV in mm

    height:
        Height of AGV in mm

    raster_x:
        Raster space on X axis in mm

    raster_y:
        Raster space on Y axis in mm
    
    serial_no:
        Additional information the user wants to store. Not used in this application

    corner: str, optional
        The corner on which this information is placed. Should be `'UL'`, `'UR'`, `'LL'`, `'LR'` or `None`
   '''
    def __init__(self, length, width, height, raster_x, raster_y, serial_no, corner=None):
        self.length = length
        self.width = width
        self.height = height
        self.raster_x = raster_x
        self.raster_y = raster_y
        self.serial_no = serial_no
        self.corner = corner

    def to_json(self):
        return json.dumps(self.__dict__)
