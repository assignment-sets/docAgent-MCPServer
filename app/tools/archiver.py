# app/services/archiver.py

import tempfile
import zipfile
import tarfile
from app.schemas import FileZipperInput
from app.utils.Utils import Utils
import logging
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()


async def zip_file(input_data: FileZipperInput) -> str:
    """
    Downloads a file from a URL and returns a ZIP archive (as bytes) containing that file.
    """
    try:
        # download to memory
        file_bytes = await Utils.download_file_as_stream(str(input_data.file_url))

        with tempfile.NamedTemporaryFile(suffix=".zip", delete=True) as tmp_zip:
            with zipfile.ZipFile(
                tmp_zip.name, mode="w", compression=zipfile.ZIP_DEFLATED
            ) as zf:
                # use a generic name inside the zip
                arcname = "file"
                zf.writestr(arcname, file_bytes)

            tmp_zip.seek(0)
            archive_bytes = tmp_zip.read()

        logger.info("Successfully zipped file: %s", input_data.file_url)
        return Utils.upload_bytes_to_s3(
            os.getenv("AWS_S3_BUCKET_NAME"),
            Utils.get_unique_s3_obj_key("zip"),
            archive_bytes,
        )

    except Exception as e:
        logger.exception("Failed to zip file.")
        raise RuntimeError(f"Zip archiving failed: {str(e)}")


async def tar_gz_file(input_data: FileZipperInput) -> str:
    """
    Downloads a file from a URL and returns a tar.gz archive (as bytes) containing that file.
    """
    try:
        file_bytes = await Utils.download_file_as_stream(str(input_data.file_url))

        with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=True) as tmp_tar:
            with tarfile.open(tmp_tar.name, mode="w:gz") as tf:
                # write the file in memory to another temp file to add to tar
                with tempfile.NamedTemporaryFile(delete=True) as tmp_inner:
                    tmp_inner.write(file_bytes)
                    tmp_inner.flush()
                    tf.add(tmp_inner.name, arcname="file")

            tmp_tar.seek(0)
            archive_bytes = tmp_tar.read()

        logger.info("Successfully created tar.gz file: %s", input_data.file_url)
        return Utils.upload_bytes_to_s3(
            os.getenv("AWS_S3_BUCKET_NAME"),
            Utils.get_unique_s3_obj_key("tar.gz"),
            archive_bytes,
        )

    except Exception as e:
        logger.exception("Failed to create tar.gz file.")
        raise RuntimeError(f"Tar.gz archiving failed: {str(e)}")


if __name__ == "__main__":
    import asyncio

    input_data = FileZipperInput(
        file_url="https://storage.googleapis.com/doc-agent-buck-1/temp/sample.pdf"
    )

    async def run_tests():
        # Test the zip_file function
        zip_url = await zip_file(input_data)
        print(f"✅ Zip file uploaded, presigned URL:\n{zip_url}")

        # Test the tar_gz_file function
        tar_url = await tar_gz_file(input_data)
        print(f"✅ Tar.gz file uploaded, presigned URL:\n{tar_url}")

    asyncio.run(run_tests())
