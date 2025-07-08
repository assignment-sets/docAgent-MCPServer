from pydantic import BaseModel, Field, HttpUrl
from typing import Optional


class PlotInput(BaseModel):
    file_url: HttpUrl = Field(
        ..., description="Public or signed URL to the XLSX file containing the data"
    )
    plot_type: str = Field(
        ...,
        description=(
            "Type of plot to generate, e.g. 'scatter', 'line', 'bar', "
            "'histogram', 'heatmap', 'boxplot', 'pairplot'"
        ),
    )
    x_column: Optional[str] = Field(
        None, description="Column to use for the x-axis (required for scatter/line/bar)"
    )
    y_column: Optional[str] = Field(
        None, description="Column to use for the y-axis (required for scatter/line/bar)"
    )
    title: Optional[str] = Field(None, description="Optional plot title")
