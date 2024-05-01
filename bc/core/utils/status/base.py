import re
from dataclasses import dataclass, field
from string import Formatter

from django.template import Context, NodeList, Template
from django.template.base import VariableNode
from django.template.defaulttags import IfNode

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
    post_replace: list[tuple[str, str]] = field(default_factory=list)
    is_valid: bool = True
    _django_template: Template | None = None

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
        if self.django_template:
            clean_template = self.django_template.render(
                Context(AlwaysBlankValueDict())
            )
        else:
            clean_template = self.str_template.format_map(
                AlwaysBlankValueDict()
            )

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
                for field_name in self.template_fields
                if field_name and field_name not in excluded
            ]
        )
        if self.django_template:
            # Remove flow control tags from the template
            placeholder_characters += sum(
                [
                    len(x)
                    for x in re.findall(
                        r"{%[^%]*%}", self.str_template, re.MULTILINE
                    )
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
        url_count = len(re.findall(url_pattern, text))
        linkless_output = re.sub(url_pattern, "", text)
        unfilled_template_items = re.findall(r"({\w+}|{%|%})", linkless_output)

        # Twitter and Mastodon both count links as 23 chars at present
        return (
            len(linkless_output) + (23 * url_count) <= self.max_characters
            and len(unfilled_template_items) == 0
        )

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
        if self.django_template:
            text = str(self.django_template.render(Context(kwargs)))
        else:
            text = self.str_template.format(**kwargs)

        for find_str, sub_str in self.post_replace:
            text = text.replace(find_str, sub_str)

        self.is_valid = self._check_output_validity(text)

        return text, image

    @property
    def _is_django_template(self) -> bool:
        """Checks if the template is a Django template

        Returns:
            bool: True if the template is a Django template, False otherwise.
        """

        return "{%" in self.str_template or "{{" in self.str_template

    @property
    def django_template(self) -> Template | None:
        """Returns the Django template object

        Returns:
            Template: Django template object
        """

        if not self._django_template and self._is_django_template:
            self._django_template = Template(self.str_template)
        return self._django_template

    @property
    def template_fields(self) -> list[str]:
        """Returns the template fields

        Returns:
            list[str]: list of fields in the template
        """
        if self.django_template:
            return _get_node_list_fields(
                self.django_template.compile_nodelist()
            )
        else:
            return [
                field_name
                for _, field_name, *_ in Formatter().parse(self.str_template)
                if field_name
            ]


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
        unfilled_template_items = re.findall(r"({\w+}|{%|%})", cleaned_text)

        return (
            len(cleaned_text) <= self.max_characters
            and len(unfilled_template_items) == 0
        )


def _get_node_list_fields(nodelist: NodeList) -> list[str]:
    fields: list[str] = []
    for node in nodelist:
        if isinstance(node, VariableNode):
            fields.append(str(node.filter_expression))
        if isinstance(node, IfNode):
            fields.extend(_get_node_list_fields(node.nodelist))
    return fields
