import io
import os
from dotenv import load_dotenv
import tempfile
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from typing import Callable
from app.schemas import PlotInput
from app.utils.Utils import Utils

load_dotenv()


def plot_boxplot(df: pd.DataFrame, input_data: PlotInput) -> bytes:
    """
    Generate a boxplot using Seaborn.
    """
    if not input_data.y_column:
        raise ValueError("y_column is required for boxplot")

    plt.figure(figsize=(8, 6))
    if input_data.x_column:
        sns.boxplot(data=df, x=input_data.x_column, y=input_data.y_column)
    else:
        sns.boxplot(data=df, y=input_data.y_column)

    if input_data.title:
        plt.title(input_data.title)

    return _save_plot_to_bytes()


def plot_histogram(df: pd.DataFrame, input_data: PlotInput) -> bytes:
    """
    Generate a histogram plot using Seaborn.
    """
    if not input_data.y_column:
        raise ValueError("y_column is required for histogram plot")

    plt.figure(figsize=(8, 6))
    sns.histplot(data=df, x=input_data.y_column, kde=True)

    if input_data.title:
        plt.title(input_data.title)

    return _save_plot_to_bytes()


def plot_heatmap(df: pd.DataFrame, input_data: PlotInput) -> bytes:
    """
    Generate a heatmap using Seaborn.
    """
    plt.figure(figsize=(10, 8))
    corr = df.corr(numeric_only=True)
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")

    plt.title(input_data.title or "Correlation Heatmap")

    return _save_plot_to_bytes()


def plot_line(df: pd.DataFrame, input_data: PlotInput) -> bytes:
    """
    Generate a line plot using Seaborn.
    """
    if not input_data.x_column or not input_data.y_column:
        raise ValueError("x_column and y_column are required for line plot")

    plt.figure(figsize=(8, 6))
    sns.lineplot(data=df, x=input_data.x_column, y=input_data.y_column)

    if input_data.title:
        plt.title(input_data.title)

    return _save_plot_to_bytes()


def plot_scatter(df: pd.DataFrame, input_data: PlotInput) -> bytes:
    """
    Generate a scatter plot using Seaborn.
    """
    if not input_data.x_column or not input_data.y_column:
        raise ValueError("x_column and y_column are required for scatter plot")

    plt.figure(figsize=(8, 6))
    sns.scatterplot(data=df, x=input_data.x_column, y=input_data.y_column)

    if input_data.title:
        plt.title(input_data.title)

    return _save_plot_to_bytes()


def plot_bar(df: pd.DataFrame, input_data: PlotInput) -> bytes:
    if not input_data.x_column or not input_data.y_column:
        raise ValueError("x_column and y_column are required for bar plot.")

    plt.figure(figsize=(10, 6))
    sns.barplot(x=df[input_data.x_column], y=df[input_data.y_column])
    plt.title(input_data.title or "Bar Plot")
    plt.xticks(rotation=45)

    return _save_plot_to_bytes()


def _save_plot_to_bytes() -> bytes:
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    return buf.read()


PLOT_TYPE_MAP: dict[str, Callable[[pd.DataFrame, PlotInput], bytes]] = {
    "scatter": plot_scatter,
    "line": plot_line,
    "bar": plot_bar,
    "histogram": plot_histogram,
    "heatmap": plot_heatmap,
    "boxplot": plot_boxplot,
}


async def generate_plot(input_data: PlotInput) -> str:
    """
    Main entry point for generating plots based on plot type.
    """
    try:
        xlsx_bytes = await Utils.download_file_as_stream(str(input_data.file_url))

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=True) as tmp_file:
            tmp_file.write(xlsx_bytes)
            tmp_file.flush()
            df = pd.read_excel(tmp_file.name)

        plot_func = PLOT_TYPE_MAP.get(input_data.plot_type.lower())

        if not plot_func:
            raise ValueError(f"Unsupported plot type: {input_data.plot_type}")

        plot_bytes = plot_func(df, input_data)
        return Utils.upload_bytes_to_s3(
            os.getenv("AWS_S3_BUCKET_NAME"),
            Utils.get_unique_s3_obj_key("png"),
            plot_bytes,
        )

    except Exception as e:
        raise RuntimeError(f"Plot generation failed: {str(e)}")


if __name__ == "__main__":
    import asyncio

    plot_input = PlotInput(
        file_url="https://storage.googleapis.com/doc-agent-buck-1/temp/Iris.xlsx",
        plot_type="boxplot",
        x_column="Species",
        y_column="PetalWidthCm",
        title="boxplot",
    )

    async def test():
        plot_url = await generate_plot(plot_input)
        print(f"✅ plot created : {plot_url}")

    asyncio.run(test())
