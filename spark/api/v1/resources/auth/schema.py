from http.client import HTTPException
from sqlalchemy import or_, and_
from io import BytesIO
import os
from sqlite3 import ProgrammingError
from urllib.error import HTTPError
from sqlalchemy import func
from spark.db_session import session
import requests
from spark.models.auth import *
from werkzeug.utils import secure_filename
import boto3


def upload_file_to_s3(file, acl="public-read"):
    filename = secure_filename(file.filename)
    s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv('AWS_S3_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_S3_SECRET_ACCESS_KEY')
        )
    try:
        s3.upload_fileobj(
            file,
            os.getenv("AWS_S3_BUCKET_NAME"),
            f"uploads/{file.filename}",
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )
    except Exception as e:
        # This is a catch all exception, edit this part to fit your needs.
        print("Something Happened: ", e)
        return e
    

    # after upload file to s3 bucket, return filename of the uploaded file
    return file.filename

        
    
