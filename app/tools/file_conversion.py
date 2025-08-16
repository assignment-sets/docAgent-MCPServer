from app.schemas import FileConvertInput
from app.utils.Utils import Utils
import logging
import tempfile
import os
import pandas as pd
from spire.doc import Document as SpireDocument, FileFormat as SpireDocFileFormat
from spire.xls import Workbook as SpireWorkbook, FileFormat as SpireXlsFileFormat
from spire.presentation import (
    Presentation as SpirePresentation,
    FileFormat as SpirePptxFileFormat,
)
from spire.pdf import PdfDocument as SpirePdfDocument, FileFormat as SpirePdfFileFormat


logger = logging.getLogger(__name__)


async def convert_docx_to_pdf(input_data: FileConvertInput) -> bytes:
    """
    Converts a DOCX file to PDF using Spire.Doc
    """
    try:
        docx_bytes = await Utils.download_file_as_stream(str(input_data.file_url))

        with tempfile.NamedTemporaryFile(suffix=".docx", delete=True) as tmp_in:
            tmp_in.write(docx_bytes)
            tmp_in.flush()

            # load DOCX with Spire
            document = SpireDocument()
            document.LoadFromFile(tmp_in.name)

            # convert to PDF
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as tmp_out:
                document.SaveToFile(tmp_out.name, SpireDocFileFormat.PDF)

                tmp_out.seek(0)
                pdf_bytes = tmp_out.read()

        return pdf_bytes

    except Exception as e:
        raise RuntimeError(f"Failed to convert DOCX to PDF: {str(e)}")


async def convert_csv_to_xlsx(input_data: FileConvertInput) -> bytes:
    """
    Converts CSV to XLSX using pandas
    """
    try:
        csv_bytes = await Utils.download_file_as_stream(str(input_data.file_url))

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=True) as tmp_csv:
            tmp_csv.write(csv_bytes)
            tmp_csv.flush()

            df = pd.read_csv(tmp_csv.name)

            with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=True) as tmp_xlsx:
                df.to_excel(tmp_xlsx.name, index=False)
                tmp_xlsx.flush()
                tmp_xlsx.seek(0)
                xlsx_bytes = tmp_xlsx.read()

        return xlsx_bytes

    except Exception as e:
        raise RuntimeError(f"Failed to convert CSV to XLSX: {str(e)}")


async def convert_xlsx_to_csv(input_data: FileConvertInput) -> bytes:
    """
    Converts XLSX to CSV using pandas
    """
    try:
        xlsx_bytes = await Utils.download_file_as_stream(str(input_data.file_url))

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=True) as tmp_xlsx:
            tmp_xlsx.write(xlsx_bytes)
            tmp_xlsx.flush()

            df = pd.read_excel(tmp_xlsx.name)

            with tempfile.NamedTemporaryFile(suffix=".csv", delete=True) as tmp_csv:
                df.to_csv(tmp_csv.name, index=False)
                tmp_csv.flush()
                tmp_csv.seek(0)
                csv_bytes = tmp_csv.read()

        return csv_bytes

    except Exception as e:
        raise RuntimeError(f"Failed to convert XLSX to CSV: {str(e)}")


async def convert_xlsx_to_pdf(input_data: FileConvertInput) -> bytes:
    """
    Converts XLSX to PDF using Spire.XLS
    """
    try:
        xlsx_bytes = await Utils.download_file_as_stream(str(input_data.file_url))

        tmp_xlsx = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        try:
            tmp_xlsx.write(xlsx_bytes)
            tmp_xlsx.flush()
            tmp_xlsx.close()

            workbook = SpireWorkbook()
            workbook.LoadFromFile(tmp_xlsx.name)
            workbook.ConverterSetting.SheetFitToPage = True

            tmp_pdf = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
            try:
                workbook.SaveToFile(tmp_pdf.name, SpireXlsFileFormat.PDF)
                workbook.Dispose()

                with open(tmp_pdf.name, "rb") as f:
                    pdf_bytes = f.read()

                return pdf_bytes

            finally:
                tmp_pdf.close()
                os.unlink(tmp_pdf.name)

        finally:
            os.unlink(tmp_xlsx.name)

    except Exception as e:
        raise RuntimeError(f"Failed to convert XLSX to PDF: {str(e)}")


async def convert_csv_to_pdf(input_data: FileConvertInput) -> bytes:
    """
    Converts CSV to PDF by first converting to XLSX then using Spire.XLS
    """
    try:
        # use the first function
        xlsx_bytes = await convert_csv_to_xlsx(input_data)

        tmp_xlsx = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        try:
            tmp_xlsx.write(xlsx_bytes)
            tmp_xlsx.flush()
            tmp_xlsx.close()

            workbook = SpireWorkbook()
            workbook.LoadFromFile(tmp_xlsx.name)
            workbook.ConverterSetting.SheetFitToPage = True

            tmp_pdf = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
            try:
                workbook.SaveToFile(tmp_pdf.name, SpireXlsFileFormat.PDF)
                workbook.Dispose()

                with open(tmp_pdf.name, "rb") as f:
                    pdf_bytes = f.read()

                return pdf_bytes

            finally:
                tmp_pdf.close()
                os.unlink(tmp_pdf.name)

        finally:
            os.unlink(tmp_xlsx.name)

    except Exception as e:
        raise RuntimeError(f"Failed to convert CSV to PDF: {str(e)}")


async def convert_pptx_to_pdf(input_data: FileConvertInput) -> bytes:
    """
    Converts PPTX to PDF using Spire.Presentation
    """
    try:
        pptx_bytes = await Utils.download_file_as_stream(str(input_data.file_url))

        tmp_pptx = tempfile.NamedTemporaryFile(suffix=".pptx", delete=False)
        try:
            tmp_pptx.write(pptx_bytes)
            tmp_pptx.flush()
            tmp_pptx.close()

            presentation = SpirePresentation()
            presentation.LoadFromFile(tmp_pptx.name)

            tmp_pdf = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
            try:
                presentation.SaveToFile(tmp_pdf.name, SpirePptxFileFormat.PDF)
                presentation.Dispose()

                with open(tmp_pdf.name, "rb") as f:
                    pdf_bytes = f.read()

                return pdf_bytes

            finally:
                tmp_pdf.close()
                os.unlink(tmp_pdf.name)

        finally:
            os.unlink(tmp_pptx.name)

    except Exception as e:
        raise RuntimeError(f"Failed to convert PPTX to PDF: {str(e)}")


async def convert_pdf_to_docx(input_data: FileConvertInput) -> bytes:
    """
    Converts PDF to DOCX using Spire.PDF
    """
    try:
        pdf_bytes = await Utils.download_file_as_stream(str(input_data.file_url))

        tmp_pdf = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        try:
            tmp_pdf.write(pdf_bytes)
            tmp_pdf.flush()
            tmp_pdf.close()

            pdf = SpirePdfDocument()
            pdf.LoadFromFile(tmp_pdf.name)

            tmp_docx = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
            try:
                pdf.SaveToFile(tmp_docx.name, SpirePdfFileFormat.DOCX)
                pdf.Close()

                with open(tmp_docx.name, "rb") as f:
                    docx_bytes = f.read()

                return docx_bytes

            finally:
                tmp_docx.close()
                os.unlink(tmp_docx.name)

        finally:
            os.unlink(tmp_pdf.name)

    except Exception as e:
        raise RuntimeError(f"Failed to convert PDF to DOCX: {str(e)}")


async def convert_pdf_to_pptx(input_data: FileConvertInput) -> bytes:
    """
    Converts PDF to PPTX using Spire.PDF
    """
    try:
        pdf_bytes = await Utils.download_file_as_stream(str(input_data.file_url))

        tmp_pdf = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        try:
            tmp_pdf.write(pdf_bytes)
            tmp_pdf.flush()
            tmp_pdf.close()

            pdf = SpirePdfDocument()
            pdf.LoadFromFile(tmp_pdf.name)

            tmp_pptx = tempfile.NamedTemporaryFile(suffix=".pptx", delete=False)
            try:
                pdf.SaveToFile(tmp_pptx.name, SpirePdfFileFormat.PPTX)
                pdf.Close()

                with open(tmp_pptx.name, "rb") as f:
                    pptx_bytes = f.read()

                return pptx_bytes

            finally:
                tmp_pptx.close()
                os.unlink(tmp_pptx.name)

        finally:
            os.unlink(tmp_pdf.name)

    except Exception as e:
        raise RuntimeError(f"Failed to convert PDF to PPTX: {str(e)}")


async def convert_pdf_to_xlsx(input_data: FileConvertInput) -> bytes:
    """
    Converts PDF to XLSX using Spire.PDF
    """
    try:
        pdf_bytes = await Utils.download_file_as_stream(str(input_data.file_url))

        tmp_pdf = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        try:
            tmp_pdf.write(pdf_bytes)
            tmp_pdf.flush()
            tmp_pdf.close()

            pdf = SpirePdfDocument()
            pdf.LoadFromFile(tmp_pdf.name)

            tmp_xlsx = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
            try:
                pdf.SaveToFile(tmp_xlsx.name, SpirePdfFileFormat.XLSX)
                pdf.Close()

                with open(tmp_xlsx.name, "rb") as f:
                    xlsx_bytes = f.read()

                return xlsx_bytes

            finally:
                tmp_xlsx.close()
                os.unlink(tmp_xlsx.name)

        finally:
            os.unlink(tmp_pdf.name)

    except Exception as e:
        raise RuntimeError(f"Failed to convert PDF to XLSX: {str(e)}")


conversion_map = {
    ("docx", "pdf"): convert_docx_to_pdf,
    ("csv", "pdf"): convert_csv_to_pdf,
    ("csv", "xlsx"): convert_csv_to_xlsx,
    ("xlsx", "csv"): convert_xlsx_to_csv,
    ("xlsx", "pdf"): convert_xlsx_to_pdf,
    ("pptx", "pdf"): convert_pptx_to_pdf,
    ("pdf", "docx"): convert_pdf_to_docx,
    ("pdf", "pptx"): convert_pdf_to_pptx,
    ("pdf", "xlsx"): convert_pdf_to_xlsx,
}


async def convert_file_format(input_data: FileConvertInput) -> str:
    """
    Dispatcher function that routes to the correct converter based on input/output format.
    """
    key = (
        input_data.input_format.lower().lstrip("."),
        input_data.output_format.lower().lstrip("."),
    )
    handler = conversion_map.get(key)

    if handler is None:
        raise ValueError(
            f"Conversion from {input_data.input_format} to {input_data.output_format} is not supported."
        )

    conv_bytes = await handler(input_data)
    return Utils.upload_bytes_to_s3(
        os.getenv("AWS_S3_BUCKET_NAME"),
        Utils.get_unique_s3_obj_key(input_data.output_format),
        conv_bytes,
    )


if __name__ == "__main__":
    import asyncio

    async def test():
        conv_url = await convert_file_format(
            FileConvertInput(
                file_url="https://storage.googleapis.com/doc-agent-buck-1/temp/converted.pdf",
                input_format="pdf",
                output_format="xlsx",
            )
        )

        print(f"✅ conversed successfully url : {conv_url}")

    asyncio.run(test())
