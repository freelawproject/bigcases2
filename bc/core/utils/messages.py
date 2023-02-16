from dataclasses import dataclass

from bc.core.utils.string_utils import trunc


@dataclass
class MastodonTemplate:
    character_count: int
    str_template: str
    link_placeholders: list[str]
    max_characters: int = 500

    def __len__(self):
        """Returns the length of the template without the placeholders

        All links count as 23 characters in mastodon no matter how long
        they really are.
        """
        return 23 * len(self.link_placeholders) + self.character_count

    def _available_space(self, *args, **kwargs) -> int:
        """Returns the number of available characters

        this methods ignores all the links in the str_template because Mastodon
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

    def format(self, *args, **kwargs) -> str:
        if "description" in kwargs:
            available_space = self._available_space("description", **kwargs)
            if len(kwargs["description"]) > available_space:
                kwargs["description"] = trunc(
                    kwargs["description"], available_space, "…"
                )

        return self.str_template.format(**kwargs)


POST_TEMPLATE = MastodonTemplate(
    character_count=38,
    link_placeholders=["pdf_link", "docket_link"],
    str_template="""New filing in {docket}
Doc #{doc_num}: {description}

PDF: {pdf_link}
Docket: {docket_link}""",
)
