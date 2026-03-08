# Image Optimizer Plugin

Example plugin demonstrating the File Processing Suite plugin system.

## Features

- Compress images while maintaining quality
- Resize images to maximum dimensions
- Convert between formats (JPEG, PNG, WebP)
- Preserve transparency when possible
- Optimize file size

## Configuration

```json
{
  "quality": 85,          // JPEG quality (1-100)
  "max_width": 1920,      // Maximum width in pixels
  "max_height": 1080,     // Maximum height in pixels
  "output_format": "auto" // Output format: auto, jpeg, png, webp
}
```

## Usage

The plugin is automatically loaded by the plugin manager. It processes image files with extensions: .jpg, .jpeg, .png, .webp

## Development

To test the plugin:

```bash
cd examples/plugins/example_image_optimizer
python plugin.py
```

## License

MIT
