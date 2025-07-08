lru cache for di
pydantic for validation
fastapi for http exceptions and di
logger for logging in stdio
use gcs for placing files a "temp/" folder with TTL logic

https://storage.googleapis.com/doc-agent-buck-1/temp/hehe.txt
https://storage.googleapis.com/doc-agent-buck-1/temp/haha.md
https://storage.googleapis.com/doc-agent-buck-1/temp/Algorithms_Data-Structures.ppt
https://storage.googleapis.com/doc-agent-buck-1/temp/Algorithms_Data-Structures.pptx
https://storage.googleapis.com/doc-agent-buck-1/temp/Algorithms_Data%20Structures.docx
https://storage.googleapis.com/doc-agent-buck-1/temp/sampleImg.png
https://storage.googleapis.com/doc-agent-buck-1/temp/sample.pdf
https://storage.googleapis.com/doc-agent-buck-1/temp/Iris.csv
https://storage.googleapis.com/doc-agent-buck-1/temp/Iris.xlsx
https://storage.googleapis.com/doc-agent-buck-1/temp/converted.pdf
https://storage.googleapis.com/doc-agent-buck-1/temp/haha.pdf

txt, md, img, pdf, doc, csv, xlsx, ppt 
6. Optional: Detect Encoding for .txt Files
ppt and pptx, doc and docx problem


pdf compression: Ghostscript
image cocompression: pillow

conversions: 
docx -> pdf : spire-doc
csv -> xlsx -> pdf : spire-xls
pptx -> pdf : Spire.Presentation

pdf -> docx: spire.pdf
pdf -> pptx: spire.pdf
pdf -> xlsx: spire.pdf


🧰 Available Tools:
- summarize_text: Summarizes a paragraph or long text into a shorter version
- get_translation: Translates text from one language to another
- extract_text: Extracts text from a file or image given a public or signed URL
- zip_file: takes a input resource url and returns url of its zipped version
- tar_gz_file: takes a input resource url and returns url of its tarball or gzipped version
- convert_file_format: Converts or transforms a resource from one format to another and returns the url
- compress_file: takes a resource url and returns the url of its compressed version
- generate_plot: Generates a plot image resource url (e.g. scatter, line, bar, heatmap, etc.) from an XLSX file URL. Supports various plot types like scatter, bar, histogram, heatmap, etc. Optional x_column and y_column can be specified depending on the plot type.

