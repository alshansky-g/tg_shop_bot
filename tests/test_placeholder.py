import struct

from bot.utils.placeholder import BANNER_GRADIENTS, create_placeholder_png


def parse_ihdr(png: bytes) -> dict:
    width, height, bit_depth, color_type = struct.unpack('>IIBB', png[16:26])
    return {'width': width, 'height': height, 'bit_depth': bit_depth, 'color_type': color_type}


def test_png_signature():
    result = create_placeholder_png()
    assert result[:8] == b'\x89PNG\r\n\x1a\n'


def test_png_ends_with_iend():
    result = create_placeholder_png()
    assert result[-12:] == b'\x00\x00\x00\x00IEND\xaeB`\x82'


def test_default_dimensions():
    result = create_placeholder_png()
    ihdr = parse_ihdr(result)
    assert ihdr['width'] == 800
    assert ihdr['height'] == 400


def test_custom_dimensions():
    result = create_placeholder_png(width=100, height=50)
    ihdr = parse_ihdr(result)
    assert ihdr['width'] == 100
    assert ihdr['height'] == 50


def test_rgb_color_type():
    result = create_placeholder_png()
    ihdr = parse_ihdr(result)
    assert ihdr['color_type'] == 2  # RGB
    assert ihdr['bit_depth'] == 8


def test_returns_bytes():
    assert isinstance(create_placeholder_png(), bytes)


def test_all_known_banners_produce_output():
    for name in BANNER_GRADIENTS:
        result = create_placeholder_png(banner_name=name)
        assert result[:8] == b'\x89PNG\r\n\x1a\n', f'Невалидный PNG для баннера: {name}'


def test_unknown_banner_uses_default_gradient():
    result = create_placeholder_png(banner_name='Несуществующий')
    assert result[:8] == b'\x89PNG\r\n\x1a\n'


def test_different_banners_produce_different_images():
    img1 = create_placeholder_png(banner_name='Главная')
    img2 = create_placeholder_png(banner_name='Оплата')
    assert img1 != img2
