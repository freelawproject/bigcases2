# This is a simplified version of `LegalProvider` in CourtListener

import random

from faker import Faker
from faker.providers import BaseProvider

_faker = Faker()


class LegalProvider(BaseProvider):
    """
    Generates fake legal-like case names, party names, court names,
    and docket numbers.

    This uses a combination of fake & farcical words and
    real or real-like words.
    The list of reporters used is quite small.

    As with other Faker providers, you can use this in code by doing:
    # fmt: off
    ```python
        from faker import Faker
        from bc.core.utils.legal_provider import LegalProvider

        fake = Faker()
        fake.add_provider(LegalProvider)
    ```
    # fmt: on
    Now the methods in LegalProvider are available to fake (the
    Faker instance you created).
    Ex:
      `fake.case_name()`
      `fake.court_name()`
      `fake.docket_number()`
      etc.

    Because the methods are static, you can also use LegalProvider by
    itself (without Faker). Ex:
    # fmt: off
    ```python
        from bc.core.utils.legal_provider import LegalProvider

        some_case_name = LegalProvider.case_name()
        some_court = LegalProvider.court_name()
    ```
    # fmt: on
    """

    # Number of parties to create if creating a full (long) list of parties.
    NUM_PARTIES = 5

    @staticmethod
    def case_name(
        full: bool = False,
        plaintiff: str | None = None,
        defendant: str | None = None,
    ) -> str:
        """
        Make a case name like "O'Neil v. Jordan".
        Ex: `LegalProvider.case_name()`
            returns "Mendoza-Page v. Smith"
            or possibly "Curtis, Davis and Atkins v. Hughes"
        Ex: `LegalProvider.case_name(True)`
            returns "Aguirre-Patrick, Brown, Carter and Bell, Robinson Ltd, Campos, Miller and Wiley, and Thomas-Avila v. Wagner, Rodriguez, Glover, Kim, and Moore"
        Ex: `LegalProvider.case_name(False, "Doe")`
            returns "Doe v. Wright-Davis"
        Ex: `LegalProvider.case_name(True,None,"Doe2")`
            returns "Knox, Campbell, Alexander, Morse, and Branch v. Doe2"

        :param full: Whether to make a full (long) list of names for the parties
            Default = False
        :type: bool
        :param plaintiff: string to use for the plaintiff. If not given,
            a fake `LegalProvider.party_name()` will be used.
        :param defendant: string to use for the defendant. If not given,
            a fake `LegalProvider.party_name()` will be used.
        :returns: the fake generated case name
        :rtype: str
        """
        if plaintiff is None:
            plaint = LegalProvider.party_name(full)
        else:
            plaint = plaintiff
        if defendant is None:
            defend = LegalProvider.party_name(full)
        else:
            defend = defendant
        return f"{plaint} v. {defend}"

    @staticmethod
    def party_name(full: bool = False) -> str:
        """
                Make a name that could be a party to a legal case.
                The name has a 50/50 chance of being either a person or a company.
                Ex: `LegalProvider.party_name()`
                    returns "Smith"
                    or possibly "Campbell, Mercado and Dickerson"
                Ex: create a party with a 'full' list of names:
                    `LegalProvider.party_name(True)`
                        returns "Perez-Wolfe, Brennan LLC, Harris, Harris and Parrish, Davila, Peterson and Miller, and Joseph, Griffin and Coleman"
                        or possibly "Bender, Ryan, Wilson, Rodriguez, and Carroll"
        "

                :param full: Whether to make a long (full) list of parties.
                  If True, will make a list LegalProvider.NUM_PARTIES long.
                  Default = False
                :type: bool
                :returns: the fake name
                :rtype: str
        """
        do_company = random.choice([True, False])
        if do_company:
            if full:
                return LegalProvider.humanized_join(
                    [
                        _faker.company()
                        for _ in range(LegalProvider.NUM_PARTIES)
                    ]
                )
            else:
                return _faker.company()
        else:
            if full:
                return LegalProvider.humanized_join(
                    [
                        _faker.last_name()
                        for _ in range(LegalProvider.NUM_PARTIES)
                    ]
                )
            else:
                return _faker.last_name()

    @staticmethod
    def court_name() -> str:
        """
        Make a fake court name in the format <section> <connector> <whole>
        Ex: `LegalProvider.court_name()`
            returns "First circuit for the zoo"
            or possibly "District court of albatross"
            or possibly "Appeals court of Eruptanyom"

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
                "Albatross",
                "eczema",
            ]
        )
        return " ".join([section, connector, whole])

    @staticmethod
    def docket_number() -> str:
        """
        Make either a simple docket number or a federal district docket
        number. There is an equal chance (50/50) of returning one or the other.

        :returns: the fake docket number
        :rtype:   str
        """
        use_simple = random.choice([True, False])
        if use_simple:
            return LegalProvider.simple_docket_number()
        else:
            return LegalProvider.federal_district_docket_number()

    @staticmethod
    def simple_docket_number() -> str:
        """
        Make a docket number of the form NN-NXXXX, where:
             * 'N' is a number 1 - 9,
             * 'X' is a number 0 - 9
        Ex: `LegalProvider.simple_docket_number()`
            returns "17-78721"

        :returns: the fake  docket number
        :rtype:   str
        """
        return _faker.numerify(text="%%-%####")

    @staticmethod
    def federal_district_docket_number() -> str:
        """
        Make a docket number like you'd see in a district court
            of the form <office>:<year>-<2 characters>-<5 digits>
        Ex: `LegalProvider.federal_district_docket_number()`
            returns "2:13-cv-03239"

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
        items: None | list = None,
        conjunction: str = "and",
        separator: str = ",",
    ) -> str:
        """
        Join together items in a human-readable list, each item separated
        by `separator` and the last item is preceded by the `conjunction`.
        This uses an "Oxford comma": it puts a comma before the conjunction.
        Adds a space after the separator and before and after the
        conjunction.
        All items in the list are converted to strings.

        Ex: `LegalProvider.humanized_join(['one','two','three'])`
          - uses the default conjunction "and"
          - uses the default separator ","
            returns `"one, two, and three"`

          `LegalProvider.humanized_join(['one','two','three'], "or")`
            returns `"one, two, or three"`

        :param items: The list to be joined together.
        :param conjunction: The word to join the items together with
            (typically "and"), but any string can be used (e.g. "&").
            Default = "and"
        :param separator: The separator between the items. Default = ","
        :returns: a string with the items in the list joined together.
        :rtype:  str
        """
        if items is None:
            return ""

        joined_str = ""
        str_items = list(map(str, items))
        num_items = len(str_items)
        sep_space = f"{separator} "
        if num_items == 0:
            joined_str = ""
        elif num_items == 1:
            joined_str = str_items[0]
        elif num_items == 2:
            joined_str = f"{str_items[0]} {conjunction} {str_items[1]}"
        elif num_items > 2:
            last_item = str_items.pop()
            joined_str = (
                f"{sep_space.join(str_items)}"
                f"{sep_space}{conjunction} {last_item}"
            )
        return joined_str
