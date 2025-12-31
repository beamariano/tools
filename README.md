# tools

Tools used for projects (in Python)

(Written by Claude)

## Image to C Array Converter

Convert images to C header files for ESP32 Arduino projects. This tool accepts any image format and outputs JPEG data as a C array that can be embedded in your firmware.

### Features

- **Multiple Input Formats**: Supports JPEG, PNG, BMP, GIF, TIFF, WebP, and any other PIL-compatible format
- **JPEG Output**: All images are converted to JPEG format for efficient memory usage
- **Auto Resize**: Resizes images to specified dimensions (default: 240x320)
- **Image Transformations**: Flip horizontally or vertically
- **Quality Control**: Adjustable JPEG quality (1-95)
- **PROGMEM Compatible**: Output arrays use `PROGMEM` for ESP32/Arduino

### Requirements

```bash
pip install Pillow
```

### Usage

#### Basic Usage

```bash
python3 image_to_c-array.py input_image.png
```

This creates `photoData.h` with your image resized to 240x320 pixels.

#### Specify Output File

```bash
python3 image_to_c-array.py input_image.png myImage.h
```

#### Custom Dimensions and Quality

```bash
python3 image_to_c-array.py photo.jpg photoData.h 320 240 85
```

Parameters: `<input> <output> <width> <height> <quality>`

#### Image Transformations

```bash
# Flip horizontally (mirror)
python3 image_to_c-array.py photo.jpg photoData.h 240 320 75 --flip-h

# Flip vertically (upside down)
python3 image_to_c-array.py photo.jpg photoData.h 240 320 75 --flip-v

# Both flips
python3 image_to_c-array.py photo.jpg photoData.h 240 320 75 --flip-h --flip-v
```

#### Disable JPEG Optimization

```bash
python3 image_to_c-array.py photo.jpg photoData.h 240 320 75 --no-optimize
```

This makes compression faster but may result in slightly larger files.

### Parameters

#### Positional Arguments

- `input_image` - Path to input image (JPEG, PNG, BMP, GIF, TIFF, WebP, etc.)
- `output_header` - Output .h file (default: `photoData.h`)
- `width` - Target width in pixels (default: `240`)
- `height` - Target height in pixels (default: `320`)
- `quality` - JPEG quality 1-95 (default: `75`)

#### Optional Flags

- `--flip-h` - Flip image horizontally (mirror)
- `--flip-v` - Flip image vertically (upside down)
- `--no-optimize` - Disable JPEG optimization

### Using in Arduino/ESP32 Projects

1. Generate the header file:

   ```bash
   python3 image_to_c-array.py myimage.png myImage.h
   ```

2. Include it in your Arduino sketch:

   ```cpp
   #include "myImage.h"

   void setup() {
     // The image data is now available as:
     // photoData[] - byte array containing JPEG data
     // sizeof(photoData) - size in bytes

     // Example: Display on TFT screen
     tft.drawJpeg(photoData, sizeof(photoData), 0, 0);
   }
   ```

### Output Format

The generated header file contains:

```c
// Generated from: input_image.png
// Size: 240x320 pixels
// JPEG size: 12345 bytes

const unsigned char photoData[] PROGMEM = {
  0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01,
  // ... JPEG data continues ...
};
```

The array contains actual JPEG file data - those bytes could be saved as a `.jpg` file and would be a valid image. The C array format allows you to embed the image directly in your program memory (`PROGMEM`) instead of requiring a file system.

### Examples

```bash
# Convert PNG to 240x320 JPEG at 75% quality
python3 image_to_c-array.py logo.png

# High quality 320x240 landscape image
python3 image_to_c-array.py photo.jpg landscape.h 320 240 90

# Small, lower quality image for memory-constrained projects
python3 image_to_c-array.py icon.png icon.h 64 64 60

# Mirror a webcam image horizontally
python3 image_to_c-array.py webcam.jpg webcam.h 240 320 75 --flip-h
```

### Notes

- Input images are automatically converted to RGB mode if needed
- High-quality Lanczos resampling is used for resizing
- JPEG subsampling is set to 4:2:0 for better compression
- The `PROGMEM` attribute stores data in flash memory instead of RAM on ESP32/Arduino

## Image to Video Converter

Convert images (or folders of images) into videos with configurable duration, dimensions, format, and fade effects.

### Features

- Convert single images or entire folders to videos
- Configurable video duration (default: 4 seconds)
- Optional fade in/out effects
- Custom output dimensions (resize videos)
- Multiple output formats supported
- Adjustable FPS and codec settings
- Supports common image formats: JPG, PNG, GIF, BMP, WebP, TIFF

### Requirements

```bash
pip install moviepy
```

### Usage

#### Basic Usage

```bash
# Convert a single image
python image_to_video.py image.jpg

# Convert all images in a folder
python image_to_video.py photos/
```

#### With Options

```bash
# Custom duration (10 seconds)
python image_to_video.py image.jpg -d 10

# Specify output folder
python image_to_video.py photos/ -o output_videos/

# Resize to specific dimensions
python image_to_video.py photos/ -s 1920x1080

# Add fade effects (1 second fade in, 1.5 second fade out)
python image_to_video.py photos/ --fade-in 1 --fade-out 1.5

# Change output format
python image_to_video.py photos/ -f avi

# Combine multiple options
python image_to_video.py photos/ -o videos/ -d 5 -s 1280x720 --fade-in 0.5 --fade-out 0.5 --fps 30
```

### Command-Line Arguments

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `input` | - | Input image file or folder (required) | - |
| `--output` | `-o` | Output folder | `./videos` |
| `--duration` | `-d` | Video duration in seconds | `4` |
| `--format` | `-f` | Output format (mp4, avi, etc.) | `mp4` |
| `--size` | `-s` | Output size as WIDTHxHEIGHT | Original size |
| `--fps` | - | Frames per second | `24` |
| `--codec` | - | Video codec | `libx264` |
| `--fade-in` | - | Fade in duration in seconds | `0` (disabled) |
| `--fade-out` | - | Fade out duration in seconds | `0` (disabled) |

### Examples

#### Convert vacation photos to 5-second videos with fades

```bash
python image_to_video.py vacation_photos/ -d 5 --fade-in 1 --fade-out 1
```

#### Create Instagram-ready videos (1080x1080)

```bash
python image_to_video.py photos/ -s 1080x1080 -d 3
```

#### High-quality videos for presentations

```bash
python image_to_video.py slides/ -s 1920x1080 -d 8 --fps 30
```

### Supported Image Formats

- JPEG (`.jpg`, `.jpeg`)
- PNG (`.png`)
- GIF (`.gif`)
- BMP (`.bmp`)
- WebP (`.webp`)
- TIFF (`.tiff`)

### Output

Videos are saved to the specified output folder (default: `./videos/`) with the same filename as the source image but with the chosen video format extension.

## Image Optimizer for Web

Optimize images for web use by compressing and resizing them while maintaining quality. Supports batch processing and multiple output formats.

### Features

- **Smart Compression**: Optimize JPEG, PNG, and WebP images
- **Auto Resize**: Set maximum dimensions (default: 1920x1080)
- **Quality Control**: Adjustable quality for JPEG/WebP (1-100, default: 85)
- **Format Conversion**: Convert between JPG, PNG, and WebP
- **Batch Processing**: Optimize entire directories at once
- **Progressive JPEG**: Generates progressive JPEGs for faster web loading
- **RGBA Handling**: Automatically converts RGBA to RGB for JPEG compatibility
- **Size Reports**: Shows original vs optimized file sizes and reduction percentage

### Requirements

```bash
pip install Pillow
```

### Usage

#### Optimize a Single Image

```bash
# Basic optimization
python optimize_images.py image.jpg

# With custom output path
python optimize_images.py image.jpg -o optimized.jpg

# Custom quality and dimensions
python optimize_images.py image.jpg --quality 90 --max-width 1280 --max-height 720

# Convert to WebP format
python optimize_images.py image.jpg --format webp
```

#### Batch Optimize a Directory

```bash
# Optimize all images in a folder
python optimize_images.py --dir photos/

# Specify output directory
python optimize_images.py --dir photos/ --output-dir optimized_photos/

# With custom settings
python optimize_images.py --dir photos/ --output-dir web_images/ --quality 80 --max-width 1920
```

### Command-Line Arguments

#### Single File Mode

| Argument | Description | Default |
|----------|-------------|---------|
| `input` | Input image file | Required |
| `-o, --output` | Output file path | `{input}_optimized.{ext}` |
| `--max-width` | Maximum width in pixels | `1920` |
| `--max-height` | Maximum height in pixels | `1080` |
| `--quality` | Quality for JPEG/WebP (1-100) | `85` |
| `--format` | Output format: jpg, png, webp | Same as input |

#### Directory Mode

| Argument | Description | Default |
|----------|-------------|---------|
| `--dir` | Input directory containing images | Required |
| `--output-dir` | Output directory | Same as input |
| `--max-width` | Maximum width in pixels | `1920` |
| `--max-height` | Maximum height in pixels | `1080` |
| `--quality` | Quality for JPEG/WebP (1-100) | `85` |
| `--format` | Output format: jpg, png, webp | Same as input |

### Examples

#### Optimize product images for e-commerce

```bash
python optimize_images.py --dir product_photos/ --output-dir web_products/ --max-width 1200 --quality 85
```

#### Create thumbnail-sized WebP images

```bash
python optimize_images.py --dir photos/ --output-dir thumbnails/ --max-width 400 --max-height 400 --format webp
```

#### High-quality optimization for photography portfolio

```bash
python optimize_images.py portfolio.jpg -o portfolio_web.jpg --quality 95 --max-width 2560
```

#### Batch convert PNGs to optimized JPEGs

```bash
python optimize_images.py --dir screenshots/ --output-dir web_screenshots/ --format jpg --quality 80
```

### Optimization Details

- **JPEG**: Uses progressive encoding, quality setting, and optimization flag
- **PNG**: Maximum compression (level 9) with optimization
- **WebP**: Quality setting with method 6 (best compression/quality ratio)
- **Resizing**: Uses Lanczos resampling for high-quality downscaling
- **RGBA to RGB**: Transparent backgrounds converted to white when saving as JPEG

### Output Example

```
Processing image.jpg...
Resized to 1920x1080
Original: 2450.32 KB
Optimized: 856.12 KB
Reduction: 65.1%
```
