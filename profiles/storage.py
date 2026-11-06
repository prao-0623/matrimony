from storages.backends.s3boto3 import S3Boto3Storage


class ProfileMediaStorage(S3Boto3Storage):
    location = 'profiles'
    file_overwrite = False
    default_acl = None
    querystring_auth = False
