import io
from dataclasses import dataclass, field
from math import ceil, sqrt
from textwrap import fill, wrap

from django.contrib.staticfiles import finders
from PIL import Image, ImageFont, ImageOps
from PIL.ImageDraw import Draw


@dataclass
class TextImage:
    title: str
    description: str
    title_font_path: str | None = finders.find("fonts/CooperHewitt-Bold.otf")
    desc_font_path: str | None = finders.find("fonts/CooperHewitt-Light.otf")
    font_size: int = 24
    line_spacing: int = 16
    padding: float = 10.0
    format: str = "png"
    max_width: int = 700
    line_height: int = field(init=False)
    width: int = field(init=False)
    height: int = field(init=False)

    def __post_init__(self):
        self.title_font = ImageFont.truetype(
            self.title_font_path, size=self.font_size
        )
        self.desc_font = ImageFont.truetype(
            self.desc_font_path, size=self.font_size
        )
        self.line_height = self.font_size + self.line_spacing

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

        A detailed explanation with all the math involved to get this approximation can be
        found in https://github.com/freelawproject/bigcases2/pull/91#discussion_r1116395882

        Args:
            length (int): Number of the pixels of the text when rendered.

        Returns:
            int: height (in pixels)
        """
        return ceil(sqrt((9 / 16) * self.line_height * length))

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

        height = ceil(approx_desc_height + approx_title_height)

        width = (
            ceil((16 / 9) * height)
            if height < (9 / 16) * self.max_width
            else self.max_width
        )

        return width, height

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
            wrapped_desc = wrap(
                self.description, max_character + ceil(increment)
            )
            wrapped_title = wrap(self.title, max_character + ceil(increment))
            # check if the new max number of characters won't overflow the rectangle
            if (
                self.get_available_space(wrapped_desc) <= 0
                or self.get_available_space(wrapped_title) <= 0
            ):
                break
            max_character += ceil(increment)

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

        if height < self.line_height * len(wrapped):
            height = self.line_height * len(wrapped)

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
            (0, 0), title, self.title_font, spacing=self.line_spacing
        )

        desc_bbox = canvas.multiline_textbbox(
            (0, 0), desc, self.desc_font, spacing=self.line_spacing
        )

        *_, height = canvas.multiline_textbbox(
            (0, 0),
            f"{title}\n\n{desc}",
            self.desc_font,
            spacing=self.line_spacing,
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
            spacing=self.line_spacing,
        )

        *_, title_height = draw.multiline_textbbox(
            (0, 0),
            multi_line_title,
            self.title_font,
            spacing=self.line_spacing,
        )

        # Draw the description of the image
        draw.multiline_text(
            (anchor_x, anchor_y + title_height + self.line_height),
            multi_line_desc,
            fill=(0, 0, 0),
            font=self.desc_font,
            spacing=self.line_spacing,
        )

        return ImageOps.expand(self.img, border=10, fill=(243, 195, 62))

    def to_bytes(self) -> bytes:
        buffer = io.BytesIO()

        # image.save expects a file-like as a argument
        image = self.make_image()
        image.save(buffer, format=self.format)

        # Turn the BytesIO object back into a bytes object
        return buffer.getvalue()


@dataclass
class SponsoredThumbnail:
    title: str
    thumbnail: bytes
    format: str = "png"
    margin: int = 40
    small_text: str | None = None
    title_font_path: str | None = finders.find("fonts/CooperHewitt-Bold.otf")
    small_font_path: str | None = finders.find("fonts/CooperHewitt-Medium.otf")
    text_box: Image = field(init=False)
    background: Image = field(init=False)
    overlay_layer: Image = field(init=False)

    def __post_init__(self) -> None:
        self.title_font = ImageFont.truetype(self.title_font_path, 46)
        self.small_font = ImageFont.truetype(self.small_font_path, 22)
        self.background = Image.open(io.BytesIO(self.thumbnail)).convert(
            "RGBA"
        )
        # make a transparent image for the text
        self.overlay_layer = Image.new(
            "RGBA", self.background.size, (255, 255, 255, 0)
        )
        if not self.small_text:
            self.small_text = "Learn more about supporting Free Law Project at https://bots.law/sponsors/"

    def get_text_box_dimensions(self) -> tuple[int, int]:
        """
        Returns the dimensions(width and height, in pixels) of a text box to render
        the sponsored text.

        Returns:
            tuple[int,int]: (width, height) dimensions
        """
        title_w, title_h = self.title_font.getbbox(self.title)[-2:]
        small_w, small_h = self.small_font.getbbox(self.small_text)[-2:]

        bbox_height = title_h + small_h
        bbox_width = max(title_w, small_w)

        return (bbox_width, bbox_height)

    def _fill_text_box(self) -> Image:
        """
        Creates a canvas for the text box and draw the sponsored text inside it

        This method computes the anchors for each line of the sponsor message so
        the whole message looks centered in the text box.

        Returns:
            Image: text box image filled with the sponsored text.
        """
        text_box_width, text_box_height = self.get_text_box_dimensions()

        text_box_w_padding = (
            int(text_box_width * 1.1),
            int(text_box_height * 1.1),
        )

        text_box = Image.new(
            "RGBA",
            text_box_w_padding,
            (255, 255, 255, 0),
        )
        # get a drawing context
        text_box_draw = Draw(text_box)

        # Draw the title centered in the text box
        title_w, title_h = self.title_font.getbbox(self.title)[-2:]
        text_box_draw.text(
            (
                (text_box_w_padding[0] - title_w) // 2,
                0.1 * text_box_height // 2,
            ),
            self.title,
            fill=(25, 25, 25, 128),
            font=self.title_font,
        )

        # Draw the small text centered in the text box
        small_w, _ = self.small_font.getbbox(self.small_text)[-2:]
        text_box_draw.text(
            (
                (text_box_w_padding[0] - small_w) // 2,
                0.1 * text_box_height // 2 + title_h + 5,
            ),
            self.small_text,
            fill=(25, 25, 25, 164),
            font=self.small_font,
        )

        return text_box

    def add_sponsored_text(self) -> None:
        """
        Adds the sponsored text to the thumbnail.

        This method gets the text box and rotates it 270 degree CCW
        to place it along the left edge of the thumbnail.

        If We paste the text box directly into the thumbnail, the
        sponsored message won't use the opacity property. The PIL docs
        has an example to draw partial opacity text and shows that this
        is a two-step process:

        - Drawing with opacity on a blank canvas that has the same dimensions
        as the background image.
        - Alpha composite these two images(the blank canvas and the background)
        together to obtain the desired result.

        This function pastes the text box into a canvas called overlay_layer(the
        blank canvas described in the first step above) and then uses the
        alpha_composite method to get the desired result.
        """
        # Get the text box
        self.text_box = self._fill_text_box()

        # Rotate the text box
        rotated_text_box = self.text_box.rotate(
            angle=270, expand=True, fillcolor=(0, 0, 0, 0)
        )
        rotated_text_box_size = rotated_text_box.size

        # Compute the coordinates to place the text in the overlay layer
        overlay_size = self.overlay_layer.size
        x = overlay_size[0] - rotated_text_box_size[0] - self.margin
        y = (overlay_size[1] - rotated_text_box_size[1]) // 2

        # Place the text in the
        self.overlay_layer.paste(rotated_text_box, (x, y))

        # Combine the overlay layer and the background
        self.background = Image.alpha_composite(
            self.background, self.overlay_layer
        )

    def to_bytes(self) -> bytes:
        """
        Returns the byte representation of the thumbnail

        Returns:
            bytes: byte representation of the thumbnail
        """
        buffer = io.BytesIO()
        self.background.save(buffer, format="png")

        return buffer.getvalue()


def add_sponsored_text_to_thumbnails(
    files: list[bytes], text: str
) -> list[bytes]:
    watermarked_thumbnails = []
    for file in files:
        thumbnail = SponsoredThumbnail(thumbnail=file, title=text)
        thumbnail.add_sponsored_text()
        watermarked_thumbnails.append(thumbnail.to_bytes())
    return watermarked_thumbnails
