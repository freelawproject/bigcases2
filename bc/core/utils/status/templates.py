import re

from .base import BaseTemplate, MastodonTemplate, TwitterTemplate

DO_NOT_POST = re.compile(
    r"""(
    pro\shac\svice|                 #pro hac vice
    notice\sof\sappearance|         #notice of appearance
    certificate\sof\sdisclosure|    #certificate of disclosure
    corporate\sdisclosure|          #corporate disclosure
    add\sand\sterminate\sattorneys| #add and terminate attorneys
    none                            #entries with bad data
    )""",
    re.VERBOSE | re.IGNORECASE,
)

DO_NOT_PAY = re.compile(
    r"""(
    withdraw\sas\sattorney|         # withdraw as attorney
    summons\s.*\sexecuted|          # summons .* executed
    none
    )""",
    re.VERBOSE | re.IGNORECASE,
)

MASTODON_POST_TEMPLATE = MastodonTemplate(
    link_placeholders=["pdf_link", "docket_link"],
    str_template="""New filing: "{docket}"
Doc #{doc_num}: {description}

PDF: {pdf_link}
Docket: {docket_link}

#CL{docket_id}""",
)


MASTODON_MINUTE_TEMPLATE = MastodonTemplate(
    link_placeholders=["docket_link"],
    str_template="""New minute entry in {docket}: {description}

Docket: {docket_link}

#CL{docket_id}""",
)

TWITTER_POST_TEMPLATE = TwitterTemplate(
    link_placeholders=["pdf_link"],
    str_template="""New filing: "{docket}"
Doc #{doc_num}: {description}

PDF: {pdf_link}""",
)

TWITTER_MINUTE_TEMPLATE = TwitterTemplate(
    link_placeholders=["docket_link"],
    str_template="""New minute entry in {docket}: {description}

Docket: {docket_link}""",
)


FOLLOW_A_NEW_CASE_TEMPLATE = BaseTemplate(
    link_placeholders=[],
    max_characters=280,
    str_template="""I'm now following {docket}:

{docket_link}""",
)
