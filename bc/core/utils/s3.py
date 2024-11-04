import logging

import boto3

from bc.settings import (
    AWS_ACCESS_KEY_ID,
    AWS_S3_CUSTOM_DOMAIN,
    AWS_SECRET_ACCESS_KEY,
    AWS_SESSION_TOKEN,
    AWS_STORAGE_BUCKET_NAME,
)

logger = logging.getLogger(__name__)


def put_object_in_bucket(
    media: bytes,
    file_name: str,
    content_type: str = "image/jpeg",
    acl: str = "public-read",
) -> str:
    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        aws_session_token=AWS_SESSION_TOKEN,
    )
    s3.put_object(
        Body=media,
        Bucket=AWS_STORAGE_BUCKET_NAME,
        Key=file_name,
        ContentType=content_type,
        ACL=acl,
    )
    return f"{AWS_S3_CUSTOM_DOMAIN}/{file_name}"
