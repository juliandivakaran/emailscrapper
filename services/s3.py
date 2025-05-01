
"""

import boto3
import os

s3_client = boto3.client('s3',
                         aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                         aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
                         region_name=os.environ['AWS_REGION_NAME']
)

BUCKET_NAME = os.environ['BUCKET_NAME']
"""