from app.schemas import FileCompressionInput
from app.utils.Utils import Utils
import os
import logging
from typing import Callable
from PIL import Image
from io import BytesIO
import tempfile
import subprocess

logger = logging.getLogger(__name__)


async def compress_image_file(input_data: FileCompressionInput) -> bytes:
    """
    Compress an image by lowering quality to 60% (jpeg/webp) or optimizing PNG.
    """
    try:
        img_bytes = await Utils.download_file_as_stream(str(input_data.file_url))

        with tempfile.NamedTemporaryFile(suffix=".img", delete=True) as tmp_file:
            tmp_file.write(img_bytes)
            tmp_file.flush()

            with Image.open(tmp_file.name) as img:
                output_buffer = BytesIO()
                format = img.format

                if format.lower() in {"jpeg", "jpg", "webp"}:
                    img.save(output_buffer, format=format, quality=60, optimize=True)
                elif format.lower() == "png":
                    img.save(output_buffer, format="PNG", optimize=True)
                else:
                    # fallback: just return the original
                    logger.warning(
                        f"No compression rule for format {format}, returning original"
                    )
                    return img_bytes

                return output_buffer.getvalue()

    except Exception as e:
        logger.exception("Image compression failed")
        raise RuntimeError(f"Image compression failed: {str(e)}")


async def compress_pdf_file(input_data: FileCompressionInput) -> bytes:
    """
    Compress a PDF using Ghostscript.
    """
    try:
        pdf_bytes = await Utils.download_file_as_stream(str(input_data.file_url))

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as tmp_in:
            tmp_in.write(pdf_bytes)
            tmp_in.flush()

            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as tmp_out:
                cmd = [
                    "gs",
                    "-sDEVICE=pdfwrite",
                    "-dCompatibilityLevel=1.4",
                    "-dPDFSETTINGS=/ebook",  # screen, ebook, printer, prepress
                    "-dNOPAUSE",
                    "-dQUIET",
                    "-dBATCH",
                    f"-sOutputFile={tmp_out.name}",
                    tmp_in.name,
                ]
                subprocess.run(cmd, check=True)

                tmp_out.seek(0)
                return tmp_out.read()

    except subprocess.CalledProcessError as e:
        logger.exception("Ghostscript compression failed")
        raise RuntimeError(f"Ghostscript compression failed: {str(e)}")
    except Exception as e:
        logger.exception("PDF compression failed")
        raise RuntimeError(f"PDF compression failed: {str(e)}")


EXTENSION_COMPRESSION_MAP: dict[str, Callable[[FileCompressionInput], bytes]] = {
    "pdf": compress_pdf_file,
    "png": compress_image_file,
    "jpg": compress_image_file,
    "jpeg": compress_image_file,
    "webp": compress_image_file,
}


async def compress_file(input_data: FileCompressionInput) -> str:
    """
    Uses provided file_type to dispatch to the correct compression function.
    """
    try:
        ext = input_data.file_type.lower().lstrip(".")

        if ext in EXTENSION_COMPRESSION_MAP:
            compress_func = EXTENSION_COMPRESSION_MAP[ext]
            logger.info(f"Dispatching to compression for .{ext} file.")
            compressed_bytes = await compress_func(input_data)
            return Utils.upload_bytes_to_s3(
                os.getenv("AWS_S3_BUCKET_NAME"),
                Utils.get_unique_s3_obj_key(ext),
                compressed_bytes,
            )
        else:
            logger.warning(f"Unsupported file type: .{ext}")
            raise ValueError(f"Unsupported file type: .{ext}")

    except Exception as e:
        logger.exception("File compression failed.")
        raise RuntimeError(f"Failed to compress file: {str(e)}")


if __name__ == "__main__":
    import asyncio

    test_image_url = (
        "https://storage.googleapis.com/doc-agent-buck-1/temp/sampleImg.png"
    )
    test_pdf_url = "https://storage.googleapis.com/doc-agent-buck-1/temp/sample.pdf"

    input_image = FileCompressionInput(file_url=test_image_url)
    input_pdf = FileCompressionInput(file_url=test_pdf_url)

    async def test():
        img_url = await compress_file(input_image)
        pdf_url = await compress_file(input_pdf)

        print(img_url)
        print(pdf_url)

    asyncio.run(test())
