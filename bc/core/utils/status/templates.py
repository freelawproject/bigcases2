import re

from .base import (
    BlueskyTemplate,
    MastodonTemplate,
    ThreadsTemplate,
)

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

MASTODON_FOLLOW_A_NEW_CASE = MastodonTemplate(
    link_placeholders=["docket_link", "initial_complaint_link", "article_url"],
    str_template="""{% autoescape off %}I'm now following {{docket}}:{% if date_filed %}

Filed: {{date_filed}}{% endif %}

Docket: {{docket_link}}{% if initial_complaint_type and initial_complaint_link %}

{{initial_complaint_type}}: {{initial_complaint_link}}{% endif %}{% if article_url %}

Context: {{article_url}}{% endif %}

#CL{{docket_id}}{% endautoescape %}""",
)


BLUESKY_FOLLOW_A_NEW_CASE = BlueskyTemplate(
    link_placeholders=["docket_link", "article_url", "initial_complaint_link"],
    # Remove extra newlines caused by empty template blocks
    str_template="""{% autoescape off %}I'm now following {{docket}}:{% if date_filed %}

Filed: {{date_filed}}{% endif %}

[View Full Case]({{docket_link}}){% if article_url %} | [Background Info]({{article_url}}){% endif %}{% if initial_complaint_type and initial_complaint_link %} | [{{initial_complaint_type}}]({{initial_complaint_link}}){% endif %}

#CL{{docket_id}}{% endautoescape %}""",
)

BLUESKY_POST_TEMPLATE = BlueskyTemplate(
    link_placeholders=["pdf_link", "docket_link"],
    str_template="""New filing: "{docket}"
Doc #{doc_num}: {description}

[Download PDF]({pdf_link}) | [View Full Case]({docket_link})

#CL{docket_id}""",
)

BLUESKY_MINUTE_TEMPLATE = BlueskyTemplate(
    link_placeholders=["docket_link"],
    str_template="""New minute entry in {docket}: {description}

[View Full Case]({docket_link})

#CL{docket_id}""",
)

THREADS_POST_TEMPLATE = ThreadsTemplate(
    link_placeholders=["pdf_link", "docket_link"],
    str_template="""New filing: "{docket}"
Doc #{doc_num}: {description}

PDF: {pdf_link}
Docket: {docket_link}

#CL{docket_id}""",
)

THREADS_MINUTE_TEMPLATE = ThreadsTemplate(
    link_placeholders=["docket_link"],
    str_template="""New minute entry in {docket}: {description}

Docket: {docket_link}

#CL{docket_id}""",
)

THREADS_FOLLOW_A_NEW_CASE = ThreadsTemplate(
    link_placeholders=["docket_link", "initial_complaint_link", "article_url"],
    str_template="""{% autoescape off %}I'm now following {{docket}}:{% if date_filed %}

Filed: {{date_filed}}{% endif %}

Docket: {{docket_link}}{% if initial_complaint_type and initial_complaint_link %}

{{initial_complaint_type}}: {{initial_complaint_link}}{% endif %}{% if article_url %}

Context: {{article_url}}{% endif %}

#CL{{docket_id}}{% endautoescape %}""",
)
