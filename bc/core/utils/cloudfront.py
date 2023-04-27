from time import time

import boto3
from django.conf import settings

client = boto3.client("cloudfront")


def create_cache_invalidation(path: str) -> None:
    client.create_invalidation(
        DistributionId=settings.AWS_CLOUDFRONT_DISTRIBUTION_ID,
        InvalidationBatch={
            "Paths": {
                "Quantity": 1,
                "Items": [path],
            },
            "CallerReference": str(time()).replace(".", ""),
        },
    )
