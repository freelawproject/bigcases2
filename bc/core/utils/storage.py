from storages.backends.s3boto3 import S3ManifestStaticStorage


class SubDirectoryS3ManifestStaticStorage(S3ManifestStaticStorage):
    location = "static"
