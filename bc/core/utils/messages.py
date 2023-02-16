from dataclasses import dataclass


@dataclass
class MastodonTemplate:
    number_of_links: int
    character_count: int
    str_template: str

    def __len__(self):
        return self.number_of_links * 23 + self.character_count


POST_TEMPLATE = MastodonTemplate(
    number_of_links=2,
    character_count=32,
    str_template="""New filing in {docket}: {desc}

PDF: {pdf_link}
Docket: {docket_link}""",
)
