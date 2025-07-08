# app.utils.Utils.py

import httpx
from google.oauth2 import service_account
import google.auth.transport.requests
import os
from dotenv import load_dotenv
import boto3
import uuid
from datetime import datetime
from botocore.config import Config

load_dotenv()


class Utils:
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_DEFAULT_REGION"),
        config=Config(s3={"addressing_style": "virtual"})
    )

    def __init__(self):
        pass

    @staticmethod
    def get_unique_s3_obj_key(extension: str) -> str: 
        now = datetime.now().strftime("%Y%m%d%H%M%S")
        uid = str(uuid.uuid4())
        return f"{now}_{uid}.{extension}"

    @staticmethod
    def upload_bytes_to_s3(
        bucket_name: str,
        object_key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
        expiry_seconds: int = 300,
    ) -> str:
        """
        Uploads a byte stream to S3 and returns a presigned URL valid for a given expiry.
        """
        try:
            Utils.s3_client.put_object(
                Bucket=bucket_name, Key=object_key, Body=data, ContentType=content_type
            )

            presigned_url = Utils.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket_name, "Key": object_key},
                ExpiresIn=expiry_seconds,
            )

            return presigned_url

        except Exception as e:
            raise RuntimeError(f"Failed to upload to S3: {str(e)}") from e

    @staticmethod
    async def download_file_as_stream(url: str, timeout: int = 20) -> bytes:
        """
        Downloads a file from the given URL and returns its content as a byte stream.
        Raises httpx.HTTPStatusError if the response status is not 200.
        """
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.content
        except httpx.HTTPStatusError as e:
            # Optional: log or raise more meaningful exceptions if needed
            raise ConnectionError(
                f"Failed to access file URL: {e.response.status_code} - {e.response.text}"
            ) from e
        except Exception as e:
            raise RuntimeError(
                f"Unexpected error while downloading file: {str(e)}"
            ) from e

    @staticmethod
    async def get_google_access_token() -> str:
        """
        Asynchronously retrieves an access token from the Google service account file.
        """
        try:
            service_account_path = os.getenv("SERVICE_ACCOUNT_FILE_PATH")
            scope = os.getenv("SCOPE_GOOGLE_VISION_API")

            if not service_account_path or not scope:
                raise EnvironmentError("Missing required environment variables.")

            # Create credentials
            credentials = service_account.Credentials.from_service_account_file(
                service_account_path, scopes=[scope]
            )

            # Refresh credentials to get token (must be done sync due to Google SDK constraint)
            request = google.auth.transport.requests.Request()
            credentials.refresh(request)

            return credentials.token

        except Exception as e:
            raise RuntimeError(f"Failed to obtain Google access token: {str(e)}") from e
