# Copied from CourtListener.  TODO: Should make this a common library

import random
from collections import OrderedDict

from faker import Faker
from faker.providers import BaseProvider

fake = Faker()


class LegalProvider(BaseProvider):
    """
        Generates fake legal-like text. These are simple and certainly don't
        represent any or all of the _real_ citation parts. (It does not
        use anything near a complete list of reporters, for example.)

        To use:
            1. Import it into your file
                `from bc.core.utils.faker_legalese import LegalProvider`
            2. Add it to the providers that Faker knows about:
                `Faker.add_provider(LegalProvider)`
            3. use the methods in ways that makes you happy:
                Faker("case_name")
                Faker("court_name")
                Faker("citation")
                # ...etc...
    """

    def court_name(self) -> str:
        """
        Generate court names like:

         - First circuit for the zoo
         - District court of albatross
         - Appeals court of eczema

        :return: A court name
        """
        first_word = random.choice(
            [
                "Thirteenth circuit",
                "Forty-Second circuit",
                "District court",
                "Appeals court",
                "Superior court",
            ]
        )
        mid_word = random.choice(["of the", "for the"])
        last_word = random.choice(
            [
                "Zoo",
                "Medical Worries",
                "Programming Horrors",
                "dragons",
                "Dirty Dishes",
                "Eruptanyom",  # Kelvin's pretend world
            ]
        )

        return " ".join([first_word, mid_word, last_word])

    def docket_number(self) -> str:
        """
        return either a simple docket number or a federal district docket number
        """
        rand_int = fake.random_int(min=0, max=1)
        if rand_int == 0:
            return self.simple_docket_number()
        else:
            return self.federal_district_docket_number()



    def simple_docket_number(self) -> str:
        """make a docket number of the form NN-NXXXX,
            where 'N' is a number 1 - 9,
                  'X' is a number 0-9
        """
        return fake.numerify(text='%%-%####')

    def federal_district_docket_number(self) -> str:
        """Make a docket number like you'd see in a district court, of the
        form, "2:13-cv-03239"
        """
        office = random.randint(1, 7)
        year = random.randint(0, 99)
        letters = random.choice(["cv", "bk", "cr", "ms"])
        number = random.randint(1, 200_000)
        return f"{office}:{year:02}-{letters}-{number:05}"

    def case_name(self, full: bool = False) -> str:
        """Makes a clean case name like "O'Neil v. Jordan" """
        plaintiff = self._make_random_party(full)
        defendant = self._make_random_party(full)
        return (f"{plaintiff} v. {defendant}")

    def citation_with_case(self) -> str:
        """
        Make a citation, including the case name
        :return citation as a string
        """
        return f"{self.case_name()}, {self.citation()}"

    def citation(self) -> str:
        """
        Make a citation e.g. 345 Mass. 76
        :return Citation as a string
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

    @staticmethod
    def humanized_join(items=[], conjunction="and", separator=",") -> str:
        """Join together items in a human-readable list
            This is cheap and easy version of CourtListener's `oxford_join`
            This does use negative indexing, so does _not_work on django querysets.

        :param items: The list to be joined together.
        :param conjunction: The word to join the items together with (typically
            'and', but can be swapped for another word like 'but', or 'or'.
        :param separator: The separator between the items. Typically a comma.

        :returns joined_str: A string with the items in the list joined together.
        """
        joined_str = ''
        num_items = len(items)
        if num_items == 0:
            joined_str = ""
        elif num_items == 1:
            joined_str = items[0]
        elif num_items == 2:
            joined_str = f"{items[0]} {conjunction} {items[1]}"
        elif num_items > 2:
            for i in range(0, num_items - 1):
                joined_str += f"{items[i]}{separator} "
            joined_str += f"{conjunction} {items[num_items - 1]}"

        return joined_str

    @staticmethod
    def _make_random_party(self, full: bool = False) -> str:
        do_company = random.choice([True, False])
        if do_company:
            if full:
                return self.humanized_join()
            else:
                return fake.company()
        else:
            if full:
                return self.humanized_join()
            else:
                return fake.last_name()
