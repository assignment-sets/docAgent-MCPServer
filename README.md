## sample urls to test
```bash
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
```

## handled types 
```bash
txt, md, png, jpeg, pdf, csv, xlsx, pptx, docx, pkl ...
```

## Docker container py runtime build script with container name(mandatory)
```bash
docker build -t py-runtime .
```

## meta data
- pdf compression: Ghostscript
- image cocompression: pillow

### conversions: 
- docx -> pdf : spire-doc
- csv -> xlsx -> pdf : spire-xls
- pptx -> pdf : Spire.Presentation

- pdf -> docx: spire.pdf
- pdf -> pptx: spire.pdf
- pdf -> xlsx: spire.pdf

## TODO:
- use `pydantic` schema for tool desc in main file for clear non repeated code
- fix bugs and file `ext` extracttion logic for presigned urls
