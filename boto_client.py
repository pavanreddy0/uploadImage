import io
import logging
import os

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv(verbose=True)

REGION = os.getenv("REGION")
SERVICE_NAME = os.getenv("SERVICE_NAME")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME")


# REGION = "us-east-2"
# SERVICE_NAME = "s3"
# AWS_ACCESS_KEY_ID = "AKIAYDZW2UGY4DXP6Q7D"
# AWS_SECRET_ACCESS_KEY = "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"
# BUCKET_NAME = "cloudcomputing007"


class Boto:
    def __init__(self):
        # print("SERVICE_NAME ", SERVICE_NAME)
        self.bucket_name = BUCKET_NAME
        resource = boto3.resource(
            service_name=SERVICE_NAME,
            region_name=REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )
        self.bucket = resource.Bucket(self.bucket_name)

    def upload_file(self, filedata, filename, content_type):
        """Upload a specific file"""
        self.bucket.upload_fileobj(
            Fileobj=filedata,
            Key=filename,
            ExtraArgs={"ContentType": content_type},
        )

    def download_file(self, filename):
        """Download a specific file"""

        files = [a_file.key for a_file in self.bucket.objects.all()]
        if filename not in files:
            return None

        a_file = io.BytesIO()
        self.bucket.download_fileobj(filename, a_file)

        return a_file

    def delete_files(self, filenames: list):
        """Delete a list of files"""

        self.bucket.delete_objects(
            Delete={"Objects": [{"Key": filename} for filename in filenames]}
        )
