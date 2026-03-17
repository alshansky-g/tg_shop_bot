import struct
import zlib

# (from_rgb, to_rgb) — цвет слева направо, сверху вниз добавляет яркость
BANNER_GRADIENTS: dict[str, tuple[tuple[int, int, int], tuple[int, int, int]]] = {
    'Главная': ((20, 30, 60), (60, 80, 140)),  # глубокий синий
    'О нас': ((30, 55, 40), (60, 120, 80)),  # зелёный
    'Оплата': ((55, 30, 20), (130, 70, 40)),  # медный
    'Доставка': ((20, 45, 55), (50, 110, 130)),  # бирюзовый
    'Категории': ((50, 30, 60), (110, 60, 140)),  # фиолетовый
    'Корзина': ((55, 40, 15), (130, 100, 30)),  # золотой
}
DEFAULT_GRADIENT = ((30, 30, 30), (80, 80, 80))


def create_placeholder_png(
    banner_name: str = '',
    width: int = 800,
    height: int = 400,
) -> bytes:
    """Generate a minimal valid RGB PNG with a named gradient. No external deps."""
    from_color, to_color = BANNER_GRADIENTS.get(banner_name, DEFAULT_GRADIENT)

    raw = bytearray()
    for y in range(height):
        raw.append(0)  # filter type: None
        t_y = y / height
        for x in range(width):
            t_x = x / width
            t = (t_x + t_y) / 2
            r = int(from_color[0] + (to_color[0] - from_color[0]) * t)
            g = int(from_color[1] + (to_color[1] - from_color[1]) * t)
            b = int(from_color[2] + (to_color[2] - from_color[2]) * t)
            raw.extend([r, g, b])

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack('>I', len(data))
            + tag
            + data
            + struct.pack('>I', zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    ihdr = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    return (
        b'\x89PNG\r\n\x1a\n'
        + chunk(b'IHDR', ihdr)
        + chunk(b'IDAT', zlib.compress(bytes(raw), 9))
        + chunk(b'IEND', b'')
    )
