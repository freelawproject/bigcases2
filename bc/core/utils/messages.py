from dataclasses import dataclass


@dataclass
class MastodonTemplate:
    number_of_links: int
    character_count: int
    str_template: str

    def __len__(self):
        """Returns the length of the template without the placeholders

        All links count as 23 characters in mastodon no matter how long
        they really are.
        """
        return self.number_of_links * 23 + self.character_count


POST_TEMPLATE = MastodonTemplate(
    number_of_links=2,
    character_count=32,
    str_template="""New filing in {docket}: {desc}

PDF: {pdf_link}
Docket: {docket_link}""",
)
