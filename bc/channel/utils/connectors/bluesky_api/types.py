from dataclasses import dataclass
from typing import Literal, NotRequired, TypedDict


@dataclass
class Session:
    accessJwt: str
    did: str
    handle: str
    refreshJwt: str
    didDoc: dict
    email: str
    emailConfirmed: bool
    emailAuthFactor: bool


@dataclass
class RegexMatch:
    start: int
    end: int
    text: str


class ByteSlice(TypedDict):
    byteStart: int
    byteEnd: int


ImageBlobRef = TypedDict("ImageBlobRef", {"$link": str})

ImageBlob = TypedDict(
    "ImageBlob",
    {
        "$type": Literal["blob"],
        "mimeType": str,
        "size": int,
        "ref": ImageBlobRef,
    },
)


class Thumbnail(TypedDict):
    alt: str
    image: ImageBlob


ImageEmbed = TypedDict(
    "ImageEmbed",
    {"$type": Literal["app.bsky.embed.images"], "images": list[Thumbnail]},
)


class SocialCard(TypedDict):
    uri: str
    title: str
    description: str
    thumb: ImageBlob


ExternalEmbed = TypedDict(
    "ExternalEmbed",
    {"$type": Literal["app.bsky.embed.external"], "external": SocialCard},
)

LinkFacet = TypedDict(
    "LinkFacet", {"$type": Literal["app.bsky.richtext.facet#link"], "uri": str}
)

TagFacet = TypedDict(
    "TagFacet", {"$type": Literal["app.bsky.richtext.facet#tag"], "tag": str}
)


class TextAnnotation(TypedDict):
    index: ByteSlice
    features: list[LinkFacet | TagFacet]


Record = TypedDict(
    "Record",
    {
        "$type": Literal["app.bsky.feed.post"],
        "text": str,
        "facets": list[TextAnnotation],
        "createdAt": str,
        "embed": NotRequired[ImageEmbed | ExternalEmbed],
    },
)
