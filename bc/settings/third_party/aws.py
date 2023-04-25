import environ

env = environ.FileAwareEnv()
DEVELOPMENT = env.bool("DEVELOPMENT", default=True)

# S3
if DEVELOPMENT:
    AWS_ACCESS_KEY_ID = env("AWS_DEV_ACCESS_KEY_ID", default="")
    AWS_SECRET_ACCESS_KEY = env("AWS_DEV_SECRET_ACCESS_KEY", default="")
else:
    AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", default="")
    AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY", default="")

AWS_STORAGE_BUCKET_NAME = env(
    "AWS_STORAGE_BUCKET_NAME", default="law-bots-storage"
)
AWS_S3_CUSTOM_DOMAIN = "storage.bots.law"
AWS_DEFAULT_ACL = "public-read"
AWS_QUERYSTRING_AUTH = False
AWS_CLOUDFRONT_DISTRIBUTION_ID = env(
    "AWS_CLOUDFRONT_DISTRIBUTION_ID", default=""
)

if DEVELOPMENT:
    AWS_STORAGE_BUCKET_NAME = "dev-law-bots-storage"
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
