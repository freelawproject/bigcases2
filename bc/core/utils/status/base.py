from dataclasses import dataclass

from bc.core.utils.string_utils import trunc

from ..images import TextImage


class AlwaysBlankValueDict(dict):
    """Just return blank, regardless of the key"""

    def __getitem__(self, key):
        return ""


@dataclass
class BaseTemplate:
    str_template: str
    link_placeholders: list[str]
    max_characters: int

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
                len(str(val))
                for key, val in kwargs.items()
                if key not in excluded
            ]
        )

        return self.max_characters - len(self) - placeholder_characters

    def format(self, *args, **kwargs) -> tuple[str, TextImage | None]:
        image = None

        if "description" in kwargs:
            available_space = self._available_space("description", **kwargs)
            if len(kwargs["description"]) > available_space:
                docket = kwargs.get("docket")
                image = TextImage(f"Case: {docket}", kwargs["description"])
                kwargs["description"] = trunc(
                    kwargs["description"],
                    available_space,
                    "…full entry below 👇",
                )

        return self.str_template.format(**kwargs), image


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
