# /server/server.py

import contextlib
from collections.abc import AsyncIterator

from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.types import Scope, Receive, Send

from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
import mcp.types as types
from app.tools import (
    summarize_text,
    get_translation,
    extract_text,
    zip_file,
    tar_gz_file,
    convert_file_format,
    compress_file,
    generate_plot,
)
from app.schemas import (
    SummarizeInput,
    TranslationInput,
    FileExtractInput,
    FileZipperInput,
    FileConvertInput,
    FileCompressionInput,
    PlotInput,
)

# --- MCP Server Setup ---
app = Server("simple-mcp-demo")


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="summarize_text",
            description="Summarizes a paragraph or long text into a shorter version",
            inputSchema={
                "type": "object",
                "required": ["text"],
                "properties": {
                    "text": {
                        "type": "string",
                        "minLength": 10,
                        "maxLength": 5000,
                        "description": "Text to be summarized",
                    }
                },
            },
        ),
        types.Tool(
            name="get_translation",
            description="Translates text from one language to another",
            inputSchema={
                "type": "object",
                "required": ["text", "input_language", "output_language"],
                "properties": {
                    "text": {
                        "type": "string",
                        "minLength": 5,
                        "maxLength": 100000,
                        "description": "Text to be translated",
                    },
                    "input_language": {
                        "type": "string",
                        "minLength": 2,
                        "maxLength": 10,
                        "description": "Source language code (e.g., 'en', 'fr')",
                    },
                    "output_language": {
                        "type": "string",
                        "minLength": 2,
                        "maxLength": 10,
                        "description": "Target language code (e.g., 'es', 'de')",
                    },
                },
            },
        ),
        types.Tool(
            name="extract_text",
            description="Extracts text from a file or image given a public or signed URL",
            inputSchema={
                "type": "object",
                "required": ["file_url"],
                "properties": {
                    "file_url": {
                        "type": "string",
                        "format": "uri",
                        "description": "Public or signed URL to the file or image",
                    }
                },
            },
        ),
        types.Tool(
            name="zip_file",
            description="takes a input resource url and returns url of its zipped version",
            inputSchema={
                "type": "object",
                "required": ["file_url"],
                "properties": {
                    "file_url": {
                        "type": "string",
                        "format": "uri",
                        "description": "Public or signed URL to the file to be archived",
                    }
                },
            },
        ),
        types.Tool(
            name="tar_gz_file",
            description="takes a input resource url and returns url of its tarball or gzipped version",
            inputSchema={
                "type": "object",
                "required": ["file_url"],
                "properties": {
                    "file_url": {
                        "type": "string",
                        "format": "uri",
                        "description": "Public or signed URL to the file to be archived",
                    }
                },
            },
        ),
        types.Tool(
            name="convert_file_format",
            description="Converts or transforms a resource from one format to another and returns the url",
            inputSchema={
                "type": "object",
                "required": ["file_url", "input_format", "output_format"],
                "properties": {
                    "file_url": {
                        "type": "string",
                        "format": "uri",
                        "description": "Public or signed URL to the source file",
                    },
                    "input_format": {
                        "type": "string",
                        "description": "The current file format, e.g. 'docx'",
                    },
                    "output_format": {
                        "type": "string",
                        "description": "The desired output format, e.g. 'pdf'",
                    },
                },
            },
        ),
        types.Tool(
            name="compress_file",
            description="takes a resource url and returns the url of its compressed version",
            inputSchema={
                "type": "object",
                "required": ["file_url"],
                "properties": {
                    "file_url": {
                        "type": "string",
                        "format": "uri",
                        "description": "Public or signed URL to the file",
                    }
                },
            },
        ),
        types.Tool(
            name="generate_plot",
            description=(
                "Generates a plot image url (e.g. scatter, line, bar, heatmap, etc.) from only an XLSX file URL and no other input format "
                "Supports various plot types like scatter, bar, histogram, heatmap, etc. "
                "Optional x_column and y_column can be specified depending on the plot type."
            ),
            inputSchema={
                "type": "object",
                "required": ["file_url", "plot_type"],
                "properties": {
                    "file_url": {
                        "type": "string",
                        "format": "uri",
                        "description": "Public or signed URL to the XLSX file containing the data",
                    },
                    "plot_type": {
                        "type": "string",
                        "description": (
                            "Type of plot to generate. Must be one of: 'scatter', 'line', 'bar', "
                            "'histogram', 'heatmap', 'boxplot', 'pairplot'.\n\n"
                            "- scatter/line/bar: require x_column and y_column\n"
                            "- histogram: uses only y_column\n"
                            "- boxplot: requires y_column; x_column is optional for grouping\n"
                            "- heatmap/pairplot: ignore both x_column and y_column"
                        ),
                    },
                    "x_column": {
                        "type": "string",
                        "description": "Optional column name for the x-axis. Required for scatter/line/bar. Optional for boxplot.",
                    },
                    "y_column": {
                        "type": "string",
                        "description": "Optional column name for the y-axis. Required for most plots except heatmap/pairplot.",
                    },
                    "title": {
                        "type": "string",
                        "description": "Optional plot title to be shown in the image",
                    },
                },
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "summarize_text":
        try:
            validated_input = SummarizeInput(**arguments)
            result = await summarize_text(validated_input)
        except Exception as e:
            raise ValueError(f"Tool 'summarize_text' failed: {e}")

    elif name == "get_translation":
        try:
            validated_input = TranslationInput(**arguments)
            result = await get_translation(validated_input)
        except Exception as e:
            raise ValueError(f"Tool 'get_translation' failed: {e}")

    elif name == "extract_text":
        try:
            print("called")
            validated_input = FileExtractInput(**arguments)
            result = await extract_text(validated_input)
        except Exception as e:
            raise ValueError(f"Tool 'extract_text' failed: {e}")

    elif name == "zip_file":
        try:
            validated_input = FileZipperInput(**arguments)
            result = await zip_file(validated_input)
        except Exception as e:
            raise ValueError(f"Tool 'zip_file' failed: {e}")

    elif name == "tar_gz_file":
        try:
            validated_input = FileZipperInput(**arguments)
            result = await tar_gz_file(validated_input)
        except Exception as e:
            raise ValueError(f"Tool 'tar_gz_file' failed: {e}")

    elif name == "convert_file_format":
        try:
            validated_input = FileConvertInput(**arguments)
            result = await convert_file_format(validated_input)
        except Exception as e:
            raise ValueError(f"Tool 'convert_file_format' failed: {e}")

    elif name == "compress_file":
        try:
            validated_input = FileCompressionInput(**arguments)
            result = await compress_file(validated_input)
        except Exception as e:
            raise ValueError(f"Tool 'compress_file' failed: {e}")

    elif name == "generate_plot":
        try:
            validated_input = PlotInput(**arguments)
            result = await generate_plot(validated_input)
        except Exception as e:
            raise ValueError(f"Tool 'generate_plot' failed: {e}")

    else:
        raise ValueError(f"Unknown tool: {name}")

    return [types.TextContent(type="text", text=str(result))]


# --- Streamable HTTP Setup ---
session_manager = StreamableHTTPSessionManager(
    app=app,
    event_store=None,
    json_response=False,
    stateless=True,
)


async def handle_streamable_http(scope: Scope, receive: Receive, send: Send) -> None:
    await session_manager.handle_request(scope, receive, send)


@contextlib.asynccontextmanager
async def lifespan(app: Starlette) -> AsyncIterator[None]:
    async with session_manager.run():
        print("✅ MCP Server running at http://localhost:8000/mcp/")
        yield


# ASGI app
starlette_app = Starlette(
    debug=True,
    routes=[
        Mount("/mcp", app=handle_streamable_http),
    ],
    lifespan=lifespan,
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(starlette_app, host="0.0.0.0", port=8000)
