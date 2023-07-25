from dataclasses import dataclass


@dataclass
class Document:
    description: str
    page_count: int
    docket_number: str
    court_name: str
    court_id: str

    def get_note(self):
        return f"Purchase {self.description}({self.docket_number}) in {self.court_name}({self.court_id})"

    def get_price(self):
        return 3.0 if self.page_count >= 30 else self.page_count * 0.10
