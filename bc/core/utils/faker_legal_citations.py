# This is a simplified version of `LegalProvider` in CourtListener

import random

from faker import Faker
from faker.providers import BaseProvider

_faker = Faker()


class LegalCitationsProvider(BaseProvider):
    """
    Generates fake legal-like citations, court names, and docket numbers.

    This does not create all possible citation forms; it only creates
    simple citations.
    This uses a combination of fake & farcical words and
    real or real-like words.
    The list of reporters used is quite small.

    As with other Faker providers, you can use this in code by doing:
    # fmt: off
    ```python
        from faker import Faker
        from bc.core.utils.faker_legal_citations import LegalCitationsProvider

        fake = Faker()
        fake.add_provider(LegalCitationsProvider)
    ```
    # fmt: on
    Now the methods in LegalCitationsProvider are available to fake (the
    Faker instance you created).
    Ex:
      `fake.court_name()`
      `fake.docket_number()`
      `fake.citation()`
      etc.
    """


    def citation_with_case(self) -> str:
        """
        Make a randomly generated citation that has a randomly generated
        case name and a randomly citation.

        :returns: the fake citation
        :rtype: str
        """
        return f"{self.case_name()}, {self.citation()}"


    @staticmethod
    def citation() -> str:
        """
        Make a citation of the form "{volume} {reporter} {page}" where:
          - volume is a random number between 1 and 999
          - reporter is randomly selected from the list of known reporters
          - page is a random number between 1 and 999

        Ex: "345 Mass. 76"

        :returns: the fake citation
        :rtype: str
        """
        reporters = [
            'U.S.', 'S. Ct.', 'L. Ed.', 'L. Ed. 2d',
            'F.', 'F.2d', 'F.3d',
            "F. Supp.", "F. Supp. 2d",
            'W.W.d', 'W.W.2d', 'W.W.3d',
            'X.d', 'X.2d', 'X.3d', 'X.4d', 'X.5d',
            'Y.d', 'Y.2d', 'Y.3d', 'Y.4d', 'Y.5d', 'Y.6d',
            'Z.1d', 'Z.2d', 'Z.3d', 'Z.4d', 'Z.5d', 'Z.6d', 'Z.7d', 'Z.8d',
            'Z.9d',
        ]
        reporter = random.choice(reporters)
        volume = random.randint(1, 999)
        page = random.randint(1, 999)
        return f"{volume} {reporter} {page}"


    def case_name(
        self, plaintiff: str | None = None, defendant: str | None
        = None
    ) -> str:
        """
        Make a case name like "O'Neil v. Jordan".

        :param plaintiff: string to use for the plaintiff. If not given,
            a fake `case_party_name()` will be used.
        :param defendant: string to use for the defendant. If not given,
            a fake `case_party_name()` will be used.
        :returns: the fake generated case name
        :rtype: str
        """
        plaint = self.case_party_name() if plaintiff is None else plaintiff
        defend = self.case_party_name() if defendant is None else defendant
        return f"{plaint} v. {defend}"


    @staticmethod
    def case_party_name() -> str:
        """
        Make a name that could be a party to a legal case.
        The name has a 50/50 chance of being either a person or a company.

        :returns: the fake name
        :rtype: str
        """
        do_company = random.choice([True, False])
        if do_company:
            return _faker.company()
        else:
            return _faker.last_name()


    @staticmethod
    def court_name() -> str:
        """
        Make a court names like
          - First circuit for the zoo
          - District court of albatross
          - Appeals court of eczema

        Basic format is <section> <connector> <whole>

        :returns: the fake court name
        :rtype: str
        """
        section = random.choice(
            [
                "Thirteenth circuit",
                "Forty-Second circuit",
                "District court",
                "Appeals court",
                "Superior court",
            ]
        )
        connector = random.choice(["of the", "for the"])
        whole = random.choice(
            [
                "Zoo",
                "Medical Worries",
                "Programming Horrors",
                "dragons",
                "Dirty Dishes",
                "Eruptanyom",  # Kelvin's pretend world
            ]
        )
        return " ".join([section, connector, whole])


    def docket_number(self) -> str:
        """
        Make either a simple docket number or a federal district docket
        number. There is an equal chance (50/50) of returning one or the other.

        :returns: the fake docket number
        :rtype:   str
        """
        use_simple = random.choice([True, False])
        if use_simple:
            return self.simple_docket_number()
        else:
            return self.federal_district_docket_number()


    @staticmethod
    def simple_docket_number() -> str:
        """
        Make a docket number of the form NN-NXXXX, where:
             * 'N' is a number 1 - 9,
             * 'X' is a number 0-9

            Examples:
                '17-78721'
                '90-20018'

        :returns: the fake  docket number
        :rtype:   str
        """
        return _faker.numerify(text='%%-%####')


    @staticmethod
    def federal_district_docket_number() -> str:
        """
        Make a docket number like you'd see in a district court
            of the form <office>:<year>-<2 characters>-<5 digits>

        Ex: "2:13-cv-03239"

        :returns: a docket number
        :rtype: str
        """
        office = random.randint(1, 7)
        year = random.randint(0, 99)
        letters = random.choice(["cv", "bk", "cr", "ms"])
        number = random.randint(1, 200_000)
        return f"{office}:{year:02}-{letters}-{number:05}"


    @staticmethod
    def humanized_join(
        items: None | list = None, conjunction: str = " and ",
        separator: str = ", "
    ) -> str:
        """
        Join together items in a human-readable list, each item separated
        by `separator` and the last item is preceded by the `conjunction`.
          Ex: `humanized_join(['one','two','three'])`
             - uses the default separator ", "
             - uses the default conjunction " and "
             returns `"one, two, and three"`

             `humanized_join(['one','two','three'], " or ")`
             returns `"one, two, or three"`

        All items in the list are converted to strings.

        :param items: The list to be joined together.
        :param conjunction: The word to join the items together with
            (typically " and "), but any string can be used (e.g. " & ").
            Note the spaces: This does not add any spaces. You *should* include
            spaces in the conjunction string if you want it to be readable.
            If you don't include them, you'll get something like
             "item1, item2, anditem3"

        :param separator: The separator between the items. Default = ', '
        :returns: a string with the items in the list joined together.
        :rtype:  str
        """
        if items is None:
            return ''

        joined_str = ''
        str_items = list(map(str, items))
        num_items = len(str_items)
        if num_items==0:
            joined_str = ""
        elif num_items==1:
            joined_str = str_items[0]
        elif num_items==2:
            joined_str = f"{str_items[0]} {conjunction} {str_items[1]}"
        elif num_items > 2:
            last_item = str_items.pop()
            joined_str = f"{separator.join(str_items)} {conjunction} {last_item}"
        return joined_str
