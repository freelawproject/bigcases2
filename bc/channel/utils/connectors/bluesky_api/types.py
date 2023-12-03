from dataclasses import dataclass
from typing import Dict, Literal, TypedDict


@dataclass
class Session:
    accessJwt: str
    did: str
    handle: str
    refreshJwt: str
    didDoc: dict
    email: str
    emailConfirmed: bool


@dataclass
class RegexMatch:
    start: int
    end: int
    text: str


class ByteSlice(TypedDict):
    byteStart: int
    byteEnd: int


ImageBlob = TypedDict(
    "ImageBlob",
    {
        "$type": Literal["blob"],
        "mimeType": str,
        "size": int,
        "ref": TypedDict("ref", {"$link": str}),
    },
)

LinkFacet = TypedDict(
    "LinkFacet", {"$type": Literal["app.bsky.richtext.facet#link"], "uri": str}
)


class TextAnnotation(TypedDict):
    index: ByteSlice
    features: list[LinkFacet]


class Thumbnail(TypedDict):
    alt_text: str
    image: ImageBlob
