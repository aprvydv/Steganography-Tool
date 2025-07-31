# strego.py
from PIL import Image
import os

END_MARKER = '1111111111111110'
FILE_MARKER = 'FILEHIDE::'
ALLOWED_IMAGE_EXTENSIONS = ('.png', '.bmp', '.jpg', '.jpeg')

def _bits_to_bytes(bits):
    data = bytearray()
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) < 8:
            break
        data.append(int(byte, 2))
    return bytes(data)

def _bytes_to_bits(data):
    return ''.join(f'{byte:08b}' for byte in data)

def max_capacity_bytes(image_path):
    img = Image.open(image_path)
    w, h = img.size
    return (w * h * 3) // 8

def encode_bytes_in_image(input_path, data_bytes, output_path):
    img = Image.open(input_path)
    if img.mode != "RGB":
        img = img.convert("RGB")
    pixels = list(img.getdata())
    bits = _bytes_to_bits(data_bytes) + END_MARKER

    if len(bits) > len(pixels) * 3:
        raise ValueError("Data too large to hide in this image!")

    new_pixels = []
    bit_idx = 0
    for pixel in pixels:
        rgb = list(pixel)
        for channel in range(3):
            if bit_idx < len(bits):
                rgb[channel] = (rgb[channel] & ~1) | int(bits[bit_idx])
                bit_idx += 1
        new_pixels.append(tuple(rgb))
    img.putdata(new_pixels)
    img.save(output_path)

def decode_bytes_from_image(image_path):
    img = Image.open(image_path)
    pixels = list(img.getdata())
    bits = ''
    for pixel in pixels:
        for channel in range(3):
            bits += str(pixel[channel] & 1)
    if END_MARKER in bits:
        bits = bits[:bits.index(END_MARKER)]
    return _bits_to_bytes(bits)

def encode_text(input_image, text, output_image):
    payload = FILE_MARKER.encode() + text.encode()
    encode_bytes_in_image(input_image, payload, output_image)

def encode_file(input_image, file_path, output_image):
    filename = os.path.basename(file_path)
    with open(file_path, 'rb') as f:
        file_bytes = f.read()
    payload = FILE_MARKER.encode() + filename.encode() + b':' + file_bytes
    encode_bytes_in_image(input_image, payload, output_image)

def decode_payload(image_path):
    data = decode_bytes_from_image(image_path)
    try:
        as_str = data.decode(errors='ignore')
        if as_str.startswith(FILE_MARKER):
            after_marker = data[len(FILE_MARKER):]
            if b':' in after_marker:
                filename, filedata = after_marker.split(b':', 1)
                return 'file', filename.decode(), filedata
            else:
                return 'text', '', after_marker.decode(errors='ignore')
        else:
            return 'unknown', '', data
    except Exception:
        return 'unknown', '', data
