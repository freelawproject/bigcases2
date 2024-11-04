import logging

import boto3

from bc.settings.third_party.aws import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
)

logger = logging.getLogger(__name__)


def put_object_in_bucket(
    media: bytes,
    file_name: str,
    bucket_name: str,
    region: str = "us-east-1",
    content_type: str = "image/jpeg",
    acl: str = "public-read",
) -> str:
    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )
    s3.put_object(
        Body=media,
        Bucket=bucket_name,
        Key=file_name,
        ContentType=content_type,
        ACL=acl,
    )
    bucket_base_uri = f"https://{bucket_name}.s3.{region}.amazonaws.com"
    return f"{bucket_base_uri}/{file_name}"
