import re

# HEX color:
#   RGB / RGBA / RRGGBB / RRGGBBAA /
#   #RGB / #RGBA / #RRGGBB / #RRGGBBAA
re_hexa = re.compile(r"#?([\dA-Fa-f]{3,4}|[\dA-Fa-f]{6}|[\dA-Fa-f]{8})")


def get_tuple_from_hex(value: str) -> tuple[int, ...]:
    """
    Examples:
      "bda" => (187, 221, 170, 255)
      "4fcd" => (68, 255, 204, 221)
      "60B0C4" => (96, 176, 196, 255)
      "2BEA40D0" => (43, 234, 64, 208)
    """
    length = len(value)
    if length not in {3, 4, 6, 8}:
        raise ValueError(value)

    if length in {3, 4}:
        value = "".join(s * 2 for s in value)
        length *= 2

    # split the hex string into pairs
    hex_parts = [value[i : (i + 2)] for i in range(0, length, 2)]

    # create tuple of ints using the hex pairs
    return tuple(int(v, 16) for v in hex_parts)


def format_color_str(value: str) -> tuple[int, ...] | None:
    """
    :param value: HEX color
    :return: 3-tuple of (R, G, B,)
    """
    hexa_match = re_hexa.fullmatch(value)
    if hexa_match is None:
        return None
    return get_tuple_from_hex(hexa_match.group(1))[:3]
