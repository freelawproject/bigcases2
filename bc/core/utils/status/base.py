import re
from dataclasses import dataclass
from string import Formatter

from bc.core.utils.string_utils import trunc

from ..images import TextImage


class InvalidTemplate(Exception):
    pass


class AlwaysBlankValueDict(dict):
    """Just return blank, regardless of the key"""

    def __getitem__(self, key):
        return ""


@dataclass
class BaseTemplate:
    str_template: str
    link_placeholders: list[str]
    max_characters: int
    border_color: tuple[int, ...] = (243, 195, 62)
    is_valid: bool = True

    def __len__(self) -> int:
        """Returns the length of the template without the placeholders

        Returns:
            int: number of characters
        """
        return self.count_fixed_characters()

    def count_fixed_characters(self):
        """Returns the number of fixed characters

        this method removes all the placerholders in the str_template
        using a dictionary that returns a blank string for each key
        and then computes the len of the new string.
        """
        clean_template = self.str_template.format_map(AlwaysBlankValueDict())
        return len(clean_template)

    def _available_space(self, *args, **kwargs) -> int:
        """Returns the number of available characters

        this method ignores all the links in the str_template because Mastodon
        uses a fixed length for them.
        """
        excluded = self.link_placeholders.copy()
        excluded.append("description")

        placeholder_characters = sum(
            [
                len(str(kwargs.get(field_name)))
                for text, field_name, *_ in Formatter().parse(
                    self.str_template
                )
                if field_name and field_name not in excluded
            ]
        )

        return self.max_characters - len(self) - placeholder_characters

    def _check_output_validity(self, text: str) -> bool:
        """
        Checks whether the provided text exceeds the maximum allowed length.

        Strips links from the output text since they use a fixed character
        count.

        Args:
            text (str): The text to be evaluated.

        Returns:
            bool: True if the text length is within the limit, False otherwise.
        """
        url_pattern = r"https?://\S+"
        url_match = re.findall(url_pattern, text)
        output = re.sub(url_pattern, "", text)

        return len(output) + 23 * len(url_match) <= self.max_characters

    def format(self, *args, **kwargs) -> tuple[str, TextImage | None]:
        image = None

        if "description" in kwargs:
            available_space = self._available_space("description", **kwargs)
            if len(kwargs["description"]) > available_space:
                docket = kwargs.get("docket")
                image = TextImage(
                    f"{docket}",
                    kwargs["description"],
                    border_color=self.border_color,
                )
                kwargs["description"] = trunc(
                    kwargs["description"],
                    available_space,
                    "…\n\n[full entry below 👇]",
                )

        text = self.str_template.format(**kwargs)

        self.is_valid = self._check_output_validity(text)

        return text, image


@dataclass
class MastodonTemplate(BaseTemplate):
    max_characters: int = 300

    def __len__(self) -> int:
        """This method overrides `Template.__len__`.

        All links count as 23 characters in mastodon no matter how long
        they really are.
        """
        return 23 * len(self.link_placeholders) + self.count_fixed_characters()


@dataclass
class TwitterTemplate(BaseTemplate):
    max_characters: int = 280

    def __len__(self) -> int:
        """This method overrides `Template.__len__`.

        All links (URLs) posted in Tweets are shortened using t.co service.
        They count as 23 characters.
        """
        return 23 * len(self.link_placeholders) + self.count_fixed_characters()


@dataclass
class BlueskyTemplate(BaseTemplate):
    max_characters: int = 300

    def _check_output_validity(self, text: str) -> bool:
        """This method overrides `Template._check_output_validity`.

        Strips links from the output text since they form part of the custom
        markup language.
        """
        cleaned_text = re.sub(r"(?<=])\(\S+\)", "", text)
        return len(cleaned_text) <= self.max_characters
