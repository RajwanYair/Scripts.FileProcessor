# PDF Processor Plugin

Advanced PDF processing plugin with merge, split, extract, and compression capabilities.

## Features

- **Merge PDFs** - Combine multiple PDFs into one
- **Split PDFs** - Separate into individual pages
- **Extract Pages** - Extract specific pages
- **Extract Text** - OCR-quality text extraction
- **Compress PDFs** - Reduce file size
- **PDF Info** - Get document metadata

## Operations

### Get PDF Info

```python
result = await plugin.process(pdf_path, context, operation='info')
```

### Merge PDFs

```python
result = await plugin.process(
    pdf_path, 
    context,
    operation='merge',
    files_to_merge=[pdf1, pdf2, pdf3],
    output_path='merged.pdf'
)
```

### Split PDF

```python
result = await plugin.process(
    pdf_path,
    context,
    operation='split',
    output_dir='./split_pages'
)
```

### Extract Pages

```python
result = await plugin.process(
    pdf_path,
    context,
    operation='extract_pages',
    pages=[1, 3, 5],
    output_path='extracted.pdf'
)
```

### Extract Text

```python
result = await plugin.process(
    pdf_path,
    context,
    operation='extract_text',
    output_path='text.txt'
)
```

### Compress PDF

```python
result = await plugin.process(
    pdf_path,
    context,
    operation='compress',
    output_path='compressed.pdf'
)
```

## Configuration

```json
{
  "compression_level": 5,  // 1-9
  "image_dpi": 150         // DPI for conversions
}
```

## Requirements

- PyPDF2>=3.0.0
- reportlab>=4.0.0 (optional, for advanced features)

## License

MIT
