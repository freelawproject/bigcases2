import io
from dataclasses import dataclass, field
from math import ceil, sqrt
from pathlib import Path
from textwrap import fill, wrap

from PIL import Image, ImageFont
from PIL.ImageDraw import Draw

from bc.settings import STATIC_GLOBAL_ROOT


@dataclass
class TextImage:
    title: str
    description: str
    title_font_path: Path = (
        STATIC_GLOBAL_ROOT / "fonts" / "CooperHewitt-Bold.otf"
    )
    desc_font_path: Path = (
        STATIC_GLOBAL_ROOT / "fonts" / "CooperHewitt-Light.otf"
    )
    font_size: int = 24
    font_spacing: int = 16
    padding: float = 10.0
    format: str = "png"
    line_height: int = field(init=False)
    width: int = field(init=False)
    height: int = field(init=False)

    def __post_init__(self):
        self.title_font = ImageFont.truetype(
            str(self.title_font_path), size=self.font_size
        )
        self.desc_font = ImageFont.truetype(
            str(self.desc_font_path), size=self.font_size
        )
        self.line_height = self.font_size + self.font_spacing

    def get_text_length(self, str: str) -> int:
        """
        Returns the length(in pixels) of the text when rendered. This methods assumes
        the text will be rendered in a single line and includes extra margins for some
        fonts.

        Args:
            str (str): Text to render.

        Returns:
            int: Length of given text.
        """
        bounding_box = self.desc_font.getbbox(str)
        return bounding_box[2]

    def get_available_space(self, wrapped: list[str]) -> int:
        """
        Returns the number of pixels available in the horizontal axis of the rectangle.
        This method uses the longest line from the given array and subtracts its length
        (in pixels) from the width of the rectangle.

        Args:
            wrapped (list[str]): list of lines without final newlines.

        Returns:
            int: number of available pixels in the horizontal axis
        """
        return self.width - self.get_text_length(max(wrapped, key=len))

    def get_height_approximation(self, length: int) -> int:
        """
        Returns a rough approximation of the minimum height required to render the given
        number of pixels in a 16:9 image. This method does not include padding in the
        equation to keep it simple.

        Args:
            length (int): Number of the pixels of the text when rendered.

        Returns:
            int: height (in pixels)
        """
        return ceil(sqrt((9 / 16) * (self.line_height) * length))

    def get_initial_dimensions(self) -> tuple[int, int]:
        """
        Returns the minimum width and height (in pixels) of a rectangle to render
        the paragraph that includes a title and the description.

        Returns:
            tuple[int, int]: (width, height) initial dimensions
        """
        desc_length = self.get_text_length(self.description)
        title_length = self.get_text_length(self.title)

        approx_desc_height = self.get_height_approximation(desc_length)
        approx_title_height = self.get_height_approximation(title_length)

        height = approx_desc_height + approx_title_height

        return ceil((16 / 9) * height), ceil(height)

    def get_max_character_count(self) -> int:
        """
        Returns the maximum number of characters that should be rendered per line.

        Computing this value requires an extra effort because We want include as many
        characters as possible in each line without overflowing the rectangle but the
        width of the image is expressed in pixels and the number of pixels of a line
        depends on the font and the characters that includes. There's not direct formula
        to get this value.

        This method uses the length(in pixels) of the character 'm' (most fonts follow
        the same conventions, capital W is the widest Uppercase character while the m
        is the widest lowercase) as a reference to get an initial value for the character
        count and then uses a loop to increase it until the available space is less than
        the reference length.

        Returns:
            int: max number of characters
        """
        reference_length = self.get_text_length("m")
        max_character = ceil(self.width / reference_length)

        # create a list of lines which are at most 'max_character' long
        wrapped_desc = wrap(self.description, max_character)

        while self.get_available_space(wrapped_desc) > reference_length:
            increment = (
                self.get_available_space(wrapped_desc) / reference_length
            )
            max_character += ceil(increment)
            wrapped_desc = wrap(self.description, max_character)

        return max_character

    def get_dimensions_with_padding(
        self, wrapped: list[str]
    ) -> tuple[int, int]:
        """
        Returns the dimensions of the rectangle with padding.

        Args:
            wrapped (list[str]): list of lines without final newlines.

        Returns:
            tuple[int, int]: (width, height) dimension with padding
        """
        longest_str_width = self.get_text_length(max(wrapped, key=len))

        # check if any of the lines of the paragraph overflows the rectangle
        if longest_str_width > self.width:
            self.width = longest_str_width

        width = (1 + (self.padding / 100)) * self.width
        height = (9 / 16) * width

        return ceil(width), ceil(height)

    def get_bbox_dimensions(
        self, canvas: Draw, title: str, desc: str
    ) -> tuple[int, int]:
        """
        Returns the dimensions(width and height, in pixels) of the text(title and
        description) when rendered.

        Args:
            canvas (Draw): 2D drawing interface for PIL images.
            title (str): Title to render
            desc (str): Description to render.

        Returns:
            tuple[int,int]: (width, height) dimensions
        """

        title_bbox = canvas.multiline_textbbox(
            (0, 0), title, self.title_font, spacing=self.font_spacing
        )

        desc_bbox = canvas.multiline_textbbox(
            (0, 0), desc, self.desc_font, spacing=self.font_spacing
        )

        *_, height = canvas.multiline_textbbox(
            (0, 0),
            f"{title}\n\n{desc}",
            self.desc_font,
            spacing=self.font_spacing,
        )

        width = title_bbox[2] if title_bbox[2] > desc_bbox[2] else desc_bbox[2]

        return width, height

    def get_anchor_coordinates(
        self, width: int, height: int
    ) -> tuple[int, int]:
        """
        Returns the coordinates of the top left corner of the bounding box that will
        render the whole paragraph in the center of the rectangle

        Args:
            width (int): width of the paragraph
            height (int): height of the paragraph

        Returns:
            tuple[int, int]: (x, y) top left corner coordinates
        """

        x = ceil((self.img.width - width) / 2)
        y = ceil((self.img.height - height) / 2)
        return x, y

    def make_image(self) -> Image:
        self.width, _ = self.get_initial_dimensions()
        max_character_count = self.get_max_character_count()

        # wrap the title and the description using the max_character_count
        wrapped_title = wrap(self.description, max_character_count)
        wrapped_desc = wrap(self.title, max_character_count)

        self.width, self.height = self.get_dimensions_with_padding(
            wrapped_title + wrapped_desc
        )

        self.img = Image.new("RGBA", (self.width, self.height), color="white")
        draw = Draw(self.img)

        multi_line_title = fill(self.title, max_character_count)
        multi_line_desc = fill(self.description, max_character_count)

        bbox_width, bbox_height = self.get_bbox_dimensions(
            draw, multi_line_title, multi_line_desc
        )

        anchor_x, anchor_y = self.get_anchor_coordinates(
            bbox_width, bbox_height
        )

        # Draw the title of the image
        draw.multiline_text(
            (anchor_x, anchor_y),
            multi_line_title,
            fill="black",
            font=self.title_font,
            spacing=self.font_spacing,
        )

        *_, title_height = draw.multiline_textbbox(
            (0, 0),
            multi_line_title,
            self.title_font,
            spacing=self.font_spacing,
        )

        # Draw the description of the image
        draw.multiline_text(
            (anchor_x, anchor_y + title_height + self.line_height),
            multi_line_desc,
            fill=(0, 0, 0),
            font=self.desc_font,
            spacing=self.font_spacing,
        )

        return self.img

    def to_bytes(self) -> bytes:
        buffer = io.BytesIO()

        # image.save expects a file-like as a argument
        image = self.make_image()
        image.save(buffer, format=self.format)

        # Turn the BytesIO object back into a bytes object
        return buffer.getvalue()
