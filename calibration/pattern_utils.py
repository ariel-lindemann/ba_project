import zxingcpp as zx


def place_pattern_on_img(pattern, img, pos):
    offset_x = pos[0]
    offset_y = pos[1]

    pattern_length = pattern.shape[0]
    pattern_width = pattern.shape[1]

    img[offset_x:offset_x+pattern_length,
        offset_y:offset_y+pattern_width] = pattern

    return img


def create_code(data, size=1000, code_type='aztec'):
    barcode_format = None
    if code_type == 'qr':
        barcode_format = zx.BarcodeFormat.QRCode
    elif code_type == 'aztec':
        barcode_format = zx.BarcodeFormat.Aztec
    elif code_type == 'datamatrix':
        barcode_format = zx.BarcodeFormat.DataMatrix
    else:
        raise RuntimeError(f'{code_type} is not a supported code type')

    return zx.write_barcode(barcode_format, data, width=size, height=size)
