CAMERA_NUMBER = 0
STD_WAIT = 5

# Detection
MARKER_TYPE = 'aruco'
DEFAULT_MARKER_SIZE = 4

# Positioning
TOLERANCE = 0

PROJECT_ROOT_DIR = '/Users/ariel/ba_project' #TODO change
DATA_DIR = f'{PROJECT_ROOT_DIR}/data'
# Calobration
PARAMS_DIR = f'{DATA_DIR}/camera_parameters'
TEMPLATE_IMG_PATH = f'{DATA_DIR}/alignment_templates/template.png'
CALIBRATION_IMGS_PATH = f'{DATA_DIR}/calibration_images'
CALIBRATION_RESULTS_PATH = f'{DATA_DIR}/calibration_results'
CALIBRATION_IMGS_FORMAT = 'jpg'

CALIBRATION_CORNERS_X = 6
CALIBRATION_CORNERS_Y = 9