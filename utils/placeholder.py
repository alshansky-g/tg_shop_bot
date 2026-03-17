import struct
import zlib


def create_placeholder_png(width: int = 800, height: int = 400) -> bytes:
    """Generate a minimal valid RGB PNG with a dark gradient. No external deps."""
    raw = bytearray()
    for y in range(height):
        raw.append(0)  # filter type: None
        for x in range(width):
            r = 30 + int(x / width * 50)
            g = 30 + int(y / height * 30)
            b = 55
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
