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

## Aspect Ratio Changer

Change the aspect ratio of images and videos using either letterboxing (adding bars) or cropping. Supports batch processing with configurable anchor points and letterbox colors.

### Features

- **Dual Modes**: Letterbox (add bars) or Crop (crop to fit)
- **Common Aspect Ratios**: 16:9, 4:3, 1:1, 9:16, 21:9, or custom dimensions
- **Flexible Crop Anchors**: Center, upper left, upper right, lower left, or lower right
- **Configurable Letterbox Colors**: Black, white, gray, or custom RGB colors
- **Batch Processing**: Process entire folders of images and/or videos
- **High Quality**: Uses Lanczos interpolation for resizing
- **Video Support**: Works with images and videos using the same workflow

### Requirements

```bash
pip install opencv-python numpy
```

### Usage

#### Interactive Mode

```bash
python change_aspect_ratio.py
```

The script will guide you through:
1. Choosing media type (images, videos, or both)
2. Selecting input/output folders
3. Choosing aspect ratio (16:9, 4:3, 1:1, 9:16, 21:9, or custom)
4. Selecting mode (letterbox or crop)
5. Configuring letterbox color (if letterbox mode) or crop anchor (if crop mode)

#### Common Aspect Ratios

| Option | Aspect Ratio | Dimensions | Use Case |
|--------|--------------|------------|----------|
| 1 | 16:9 | 1920x1080 | Widescreen, YouTube, modern displays |
| 2 | 4:3 | 1024x768 | Traditional TV, older displays |
| 3 | 1:1 | 1080x1080 | Instagram posts, square format |
| 4 | 9:16 | 1080x1920 | Vertical video, mobile, stories |
| 5 | 21:9 | 2560x1080 | Ultra-wide, cinematic |
| 6 | Custom | User defined | Specific project requirements |

### Modes

#### Letterbox Mode

Adds colored bars (pillarbox or letterbox) to preserve the entire image/video while fitting the target aspect ratio.

**Letterbox Color Options:**
- **Black** (0, 0, 0) - Default, classic cinema look
- **White** (255, 255, 255) - Clean, minimal aesthetic
- **Gray** (128, 128, 128) - Neutral middle ground
- **Custom RGB** - Specify exact color values (0-255)

**Example:** Converting a 16:9 video to 1:1 for Instagram will add black bars on the sides.

#### Crop Mode

Crops the image/video to fit the target aspect ratio without adding bars. You can choose where to focus the crop.

**Crop Anchor Options:**

| Position | Description | Best For |
|----------|-------------|----------|
| **Center** (default) | Keep the middle of the image | General purpose, centered subjects |
| **Upper Left** | Focus on top-left corner | Top-left alignment |
| **Upper Center** | Focus on top-middle | Portraits, faces, headers |
| **Upper Right** | Focus on top-right corner | Top-right alignment |
| **Center Left** | Focus on middle-left | Left-aligned content |
| **Center Right** | Focus on middle-right | Right-aligned content |
| **Lower Left** | Focus on bottom-left corner | Bottom-left alignment |
| **Lower Center** | Focus on bottom-middle | Captions, lower content |
| **Lower Right** | Focus on bottom-right corner | Bottom-right alignment |

**Example:** Converting a portrait photo to landscape might want **Upper Center** to keep the subject's face in frame.

### Examples

#### Convert Instagram Photos to YouTube (Letterbox)

```bash
# Run script and select:
# - Media type: Images (1)
# - Aspect ratio: 16:9 (1)
# - Mode: Letterbox (1)
# - Color: Black (1)
```

This will take 1:1 Instagram photos and add black bars to make them 16:9 widescreen.

#### Convert Landscape Videos to Vertical (Crop)

```bash
# Run script and select:
# - Media type: Videos (2)
# - Aspect ratio: 9:16 (4)
# - Mode: Crop (2)
# - Anchor: Center (1)
```

This will crop 16:9 videos to 9:16 vertical format, keeping the center area.

#### Batch Process with Custom Colors

Want white letterbox bars instead of black? Simply select option 2 when choosing letterbox color, or option 4 to specify exact RGB values like brand colors.

### Folder Structure

**Default folders:**
- **Images Input**: `images_to_process/`
- **Images Output**: `images_processed/`
- **Videos Input**: `videos_to_process/`
- **Videos Output**: `videos_processed/`

You can specify custom folders during the interactive prompts.

### Supported Formats

**Images:** JPG, JPEG, PNG, BMP, GIF, WebP, TIFF
**Videos:** MP4, AVI, MOV, MKV, WMV, FLV

### Technical Details

- **Interpolation**: Lanczos4 for high-quality resizing
- **Color Format**: BGR (OpenCV standard)
- **Video Codec**: MP4V (default)
- **Progress Reporting**: Shows frame-by-frame progress for videos

### Use Cases

- **Social Media**: Adapt content between platforms (YouTube ↔ Instagram ↔ TikTok)
- **Presentations**: Standardize mixed media to consistent aspect ratio
- **Video Editing**: Prepare footage for specific aspect ratio requirements
- **Archiving**: Convert old 4:3 content to modern 16:9
- **Mobile Content**: Create vertical videos from horizontal footage

## Text to Image Converter

Convert text lines from a `.txt` file into beautifully centered images. Each line in the input file becomes a separate image with customizable fonts, colors, dimensions, and formats.

### Features

- **Line-by-Line Conversion**: Each line in the text file becomes a separate image
- **Center-Aligned Text**: All text is automatically centered both horizontally and vertically
- **Configurable Aspect Ratios**: Choose from common ratios (16:9, 4:3, 1:1, 9:16, 21:9) or custom dimensions
- **Custom Fonts**: Use system default fonts or provide your own `.ttf` or `.otf` font files
- **Font Size Control**: Adjustable font size (default: 48px)
- **Color Schemes**: Preset color combinations or custom RGB values
- **Multiple Formats**: Output as PNG (lossless), JPEG, or WebP
- **Batch Processing**: Convert entire text files in one go
- **Smart Filenames**: Output files named with line numbers and sanitized text

### Requirements

```bash
pip install Pillow
```

### Usage

#### Interactive Mode

```bash
python text_to_image.py
```

The script will guide you through:
1. Selecting input text file (default: `text_to_process/text.txt`)
2. Choosing output folder (default: `images_processed/`)
3. Selecting aspect ratio and dimensions
4. Configuring font size
5. Optional: Using a custom font file
6. Selecting color scheme
7. Choosing output format

#### Input File Format

Create a `.txt` file with one text line per image:

```text
Hello World
Welcome to Text-to-Image
Python Script
Center Aligned Text
Beautiful Images
```

Each line will be converted to a separate image file.

### Aspect Ratio Options

| Option | Aspect Ratio | Dimensions | Use Case |
|--------|--------------|------------|----------|
| 1 | 16:9 | 1920x1080 | Widescreen, presentations, YouTube |
| 2 | 4:3 | 1024x768 | Standard displays, classic format |
| 3 | 1:1 | 1080x1080 | Instagram posts, square thumbnails |
| 4 | 9:16 | 1080x1920 | Vertical video, mobile stories |
| 5 | 21:9 | 2560x1080 | Ultra-wide, cinematic |
| 6 | Custom | User defined | Specific project requirements |

### Color Schemes

**Preset Options:**
1. **White text on black background** (default) - Classic, high contrast
2. **Black text on white background** - Clean, minimal
3. **Custom RGB colors** - Specify exact colors for text and background

**Custom Colors:**
- Text color: RGB values (0-255 for red, green, blue)
- Background color: RGB values (0-255 for red, green, blue)

### Output Formats

1. **PNG** (default) - Lossless, best quality, supports transparency
2. **JPEG** - Smaller file size, good for photos and web
3. **WEBP** - Modern format, good compression and quality

### Examples

#### Create Quote Images for Social Media

```bash
# Create quotes.txt with your favorite quotes (one per line)
echo "Be the change you wish to see" > text_to_process/quotes.txt
echo "Think outside the box" >> text_to_process/quotes.txt
echo "Dream big, work hard" >> text_to_process/quotes.txt

# Run the script and select:
# - Aspect ratio: 1:1 (Square - Instagram ready)
# - Font size: 60
# - Color scheme: White on black
# - Format: PNG

python text_to_image.py
```

This creates three square images perfect for Instagram posts.

#### Create Presentation Slides

```bash
# Run script and select:
# - Aspect ratio: 16:9 (Widescreen)
# - Font size: 72
# - Color scheme: Black on white
# - Format: PNG
```

Creates widescreen images suitable for PowerPoint or Google Slides.

#### Create Vertical Story Cards

```bash
# Run script and select:
# - Aspect ratio: 9:16 (Vertical)
# - Font size: 80
# - Custom colors: Your brand colors
# - Format: JPEG
```

Perfect for Instagram or TikTok stories.

### Folder Structure

**Default folders:**
- **Input**: `text_to_process/` - Place your `.txt` files here
- **Output**: `images_processed/` - Generated images saved here

You can specify custom folders during the interactive prompts.

### Output Filenames

Generated images are named using the pattern:
```
line_{number}_{sanitized_text}.{extension}
```

**Examples:**
- `line_001_Hello_World.png`
- `line_002_Welcome_to_Text_to_Image.png`
- `line_003_Python_Script.jpg`

This makes it easy to identify which image corresponds to which text line.

### Font Selection

**System Default Fonts:**
The script automatically finds suitable fonts on your system:
- **macOS**: Helvetica, SF Display
- **Linux**: DejaVu Sans, Liberation Sans
- **Windows**: Arial

**Custom Fonts:**
When prompted, you can provide a path to any `.ttf` or `.otf` font file:
```
/path/to/your/CustomFont.ttf
```

### Use Cases

- **Social Media Content**: Create quote images, announcements, or text-based posts
- **Presentations**: Generate title slides or section headers
- **Educational Materials**: Create flashcards or study aids
- **Signage**: Design digital signs or displays
- **Video Production**: Generate text overlays or title cards
- **Marketing**: Create promotional images with key messages
- **Event Graphics**: Generate event announcements or schedules

### Technical Details

- **Text Rendering**: Uses PIL/Pillow ImageDraw with TrueType font support
- **Centering Algorithm**: Calculates text bounding box for precise centering
- **Padding**: 20px default padding around text to prevent edge clipping
- **Quality**: High-quality text rendering with anti-aliasing
- **Format Conversion**: Automatic RGB conversion for JPEG (no transparency)

### Tips

- **Text Fit Warning**: If text is too large for the image, you'll receive a warning
- **Filename Length**: Text in filenames is limited to 50 characters and sanitized
- **Empty Lines**: Blank lines in the input file are automatically skipped
- **UTF-8 Support**: Full Unicode support for international characters
- **JPEG Quality**: JPEG output uses 95% quality for best results
